from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from uuid import UUID

from seo_engine.briefs import build_brief, render_brief_markdown
from seo_engine.config import Settings
from seo_engine.connectors.clarity import ClarityConnector
from seo_engine.connectors.dataforseo import DataForSEOConnector
from seo_engine.connectors.firecrawl import FirecrawlConnector
from seo_engine.connectors.ga4 import GA4Connector
from seo_engine.connectors.gsc import GSCConnector
from seo_engine.diagnostics import (
    DiagnosticConfig,
    EvidenceSet,
    find_striking_distance,
    rank_diagnostics,
)
from seo_engine.domain.models import CollectionResult, DateWindow, RunSummary, SiteScope
from seo_engine.domain.ports import DataConnector
from seo_engine.generation import generate_changes
from seo_engine.github_delivery import GitHubDelivery
from seo_engine.google_auth import GA4_SCOPE, GSC_SCOPE, service_account_credentials
from seo_engine.llm import OpenAIModelClient
from seo_engine.persistence.db import create_persistent_session
from seo_engine.persistence.repositories import ObservationRepository, RunRepository
from seo_engine.policy import GenerationPolicy, validate_generation
from seo_engine.runrate_routes import OVERRIDES_PATH, indexable_routes, resolve_target_route
from seo_engine.site_validator import _validate_content
from seo_engine.strategy import adjust_priorities, load_strategy


@dataclass
class IngestionSummary:
    run_id: UUID
    status: str
    connector_results: list[CollectionResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_fingerprint(site_id: str, window: DateWindow, connectors: list[DataConnector]) -> str:
    names = ",".join(sorted(connector.name for connector in connectors))
    raw = f"{site_id}:{window.start.isoformat()}:{window.end.isoformat()}:{names}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def collect_all(
    connectors: list[DataConnector],
    window: DateWindow,
    scope: SiteScope,
    runs: RunRepository,
    observations: ObservationRepository,
) -> IngestionSummary:
    fingerprint = run_fingerprint(scope.site_id, window, connectors)
    if await runs.has_fingerprint(scope.site_id, fingerprint):
        existing_id = await runs.start(scope.site_id, fingerprint)
        status, errors = await runs.state(existing_id)
        saved = await observations.list_for_run(existing_id)
        return IngestionSummary(
            run_id=existing_id,
            status=status,
            connector_results=[
                CollectionResult(source="persisted", status="complete", observations=saved)
            ],
            errors=errors,
        )

    run_id = await runs.start(scope.site_id, fingerprint)
    semaphore = asyncio.Semaphore(5)

    async def collect_one(connector: DataConnector) -> CollectionResult:
        async with semaphore:
            try:
                return await connector.collect(window, scope)
            except Exception as exc:  # provider isolation boundary
                return CollectionResult(
                    source=connector.name,
                    status="failed",
                    errors=[f"{type(exc).__name__}: {exc}"],
                )

    results = await asyncio.gather(*(collect_one(connector) for connector in connectors))
    errors = [error for result in results for error in result.errors]
    for result in results:
        if result.observations:
            await observations.insert_many(run_id, result.observations)
    status = "complete" if all(result.status == "complete" for result in results) else "partial"
    await runs.finish(run_id, status, errors)
    return IngestionSummary(run_id=run_id, status=status, connector_results=results, errors=errors)


async def run_weekly(
    settings: Settings,
    run_date: date | None = None,
    fixture_mode: bool = False,
    propose_pr: bool = False,
) -> RunSummary:
    target_date = run_date or date.today()
    window = DateWindow(start=target_date - timedelta(days=6), end=target_date)
    scope = SiteScope(
        site_id=settings.site_id,
        site_url=settings.site_url,
        target_root=Path(settings.target_site_root),
        base_branch=settings.github_base_branch,
    )
    if fixture_mode:
        connectors: list[DataConnector] = [
            GSCConnector(
                payload={
                    "rows": [
                        {
                            "keys": ["seo service", "/pages/example-service.html"],
                            "clicks": 20,
                            "impressions": 500,
                            "ctr": 0.04,
                            "position": 9.5,
                        }
                    ]
                }
            )
        ]
        database_url = "sqlite+aiosqlite:///artifacts/fixture.sqlite"
    else:
        connectors = _build_live_connectors(settings)
        database_url = settings.database_url

    if database_url.startswith("sqlite+aiosqlite:///"):
        Path(database_url.removeprefix("sqlite+aiosqlite:///")).parent.mkdir(
            parents=True, exist_ok=True
        )

    async with create_persistent_session(database_url) as session:
        summary = await collect_all(
            connectors,
            window,
            scope,
            RunRepository(session),
            ObservationRepository(session),
        )
    observations = [item for result in summary.connector_results for item in result.observations]
    diagnostics = find_striking_distance(EvidenceSet(observations), DiagnosticConfig())
    strategy = load_strategy(Path("config/strategy.yaml"))
    opportunities = adjust_priorities(rank_diagnostics(diagnostics, strategy), strategy)
    brief_count = 0
    if opportunities:
        brief = build_brief(opportunities[0], strategy)
        artifact = Path("artifacts/briefs")
        artifact.mkdir(parents=True, exist_ok=True)
        artifact_name = hashlib.sha256(opportunities[0].fingerprint.encode()).hexdigest()[:16]
        (artifact / f"{artifact_name}.md").write_text(
            render_brief_markdown(brief), encoding="utf-8"
        )
        brief_count = 1
    pull_request_url = None
    errors = list(summary.errors)
    if propose_pr and not fixture_mode and opportunities:
        try:
            if summary.status != "complete":
                raise ValueError("A partial provider run cannot publish an SEO proposal")
            if not settings.openai_api_key or not settings.github_token:
                raise ValueError("OPENAI_API_KEY and GITHUB_TOKEN are required for PR proposals")
            if not settings.github_owner or not settings.github_repository:
                raise ValueError("GitHub repository identity is required for PR proposals")
            root = Path(settings.target_site_root).resolve()
            routes = indexable_routes(root)
            selected = next(
                (
                    item
                    for item in opportunities
                    if item.diagnostic.kind == "striking_distance"
                    and _is_supported_target(
                        item.diagnostic.target_url, str(settings.site_url), routes
                    )
                ),
                None,
            )
            if selected is not None:
                selected_brief = build_brief(selected, strategy)
                original = (root / OVERRIDES_PATH).read_text(encoding="utf-8")
                changes = await generate_changes(
                    selected_brief,
                    {OVERRIDES_PATH: original},
                    OpenAIModelClient(
                        settings.openai_api_key.get_secret_value(), settings.openai_model
                    ),
                    site_url=str(settings.site_url),
                    repo_root=root,
                )
                if changes:
                    target_route = resolve_target_route(
                        selected.diagnostic.target_url, str(settings.site_url), routes
                    )
                    report = validate_generation(
                        changes,
                        selected_brief,
                        GenerationPolicy(
                            allowed_routes=routes,
                            target_route=target_route,
                            original_content=original,
                            secrets=[
                                settings.openai_api_key.get_secret_value(),
                                settings.github_token.get_secret_value(),
                            ],
                        ),
                    )
                    site_issues = _validate_content(root, changes[0].file_change.content)
                    if not report.valid or site_issues:
                        raise ValueError("Generated SEO metadata failed policy or route validation")
                    artifact = Path("artifacts/proposals")
                    artifact.mkdir(parents=True, exist_ok=True)
                    (artifact / f"{selected.fingerprint.replace(':', '-')[:40]}.json").write_text(
                        changes[0].file_change.content, encoding="utf-8"
                    )
                    branch_id = hashlib.sha256(selected.fingerprint.encode()).hexdigest()[:8]
                    branch = f"codex/weekly-seo-{target_date:%Y%m%d}-{branch_id}"
                    delivery = GitHubDelivery(
                        settings.github_owner,
                        settings.github_repository,
                        settings.github_token.get_secret_value(),
                    )
                    try:
                        base_sha = await delivery.base_sha(settings.github_base_branch)
                        await delivery.create_branch(branch, base_sha)
                        await delivery.commit_files(
                            branch,
                            [changes[0].file_change],
                            "seo: propose RunRate metadata improvement",
                        )
                        pr = await delivery.open_draft_pr(
                            branch,
                            settings.github_base_branch,
                            f"SEO: review metadata for {target_route}",
                            render_brief_markdown(selected_brief)
                            + "\n## Scope\nOnly `content/seo-overrides.json` changes. "
                            "Review claim accuracy and any available Cloudflare preview "
                            "before merging.\n",
                        )
                        pull_request_url = pr.url
                    finally:
                        await delivery.client.aclose()
        except Exception as exc:
            errors.append(f"SEO proposal not delivered: {type(exc).__name__}: {exc}")
    status = "partial" if errors and propose_pr else summary.status
    return RunSummary(
        run_id=summary.run_id,
        status=status,
        diagnostics=len(diagnostics),
        briefs=brief_count,
        pull_request_url=pull_request_url,
        errors=errors,
    )


def _is_supported_target(target_url: str | None, site_url: str, routes: set[str]) -> bool:
    try:
        resolve_target_route(target_url, site_url, routes)
    except ValueError:
        return False
    return True


def _build_live_connectors(settings: Settings) -> list[DataConnector]:
    google_credentials = None
    if settings.gsc_property or settings.ga4_property_id:
        try:
            google_credentials = service_account_credentials(settings, [GSC_SCOPE, GA4_SCOPE])
        except Exception:
            # The individual connectors report the missing credential as a
            # provider-level failure, allowing the rest of the weekly run to
            # produce useful partial evidence.
            google_credentials = None

    keywords = [item.strip() for item in settings.seo_keywords.split(",") if item.strip()]
    return [
        GSCConnector(
            property_name=settings.gsc_property,
            credentials=google_credentials,
        ),
        GA4Connector(
            property_id=settings.ga4_property_id,
            credentials=google_credentials,
        ),
        ClarityConnector(
            project_id=settings.clarity_project_id,
            api_token=(
                settings.clarity_api_token.get_secret_value() if settings.clarity_api_token else ""
            ),
        ),
        FirecrawlConnector(
            api_key=(
                settings.firecrawl_api_key.get_secret_value() if settings.firecrawl_api_key else ""
            ),
        ),
        DataForSEOConnector(
            login=(
                settings.dataforseo_login.get_secret_value() if settings.dataforseo_login else ""
            ),
            password=(
                settings.dataforseo_password.get_secret_value()
                if settings.dataforseo_password
                else ""
            ),
            keywords=keywords,
            location_code=settings.dataforseo_location_code,
            language_code=settings.dataforseo_language_code,
            device=settings.dataforseo_device,
        ),
    ]
