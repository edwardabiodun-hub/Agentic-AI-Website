from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from uuid import UUID

from seo_engine.briefs import build_brief, render_brief_markdown
from seo_engine.connectors.gsc import GSCConnector
from seo_engine.diagnostics import (
    DiagnosticConfig,
    EvidenceSet,
    find_striking_distance,
    rank_diagnostics,
)
from seo_engine.domain.models import CollectionResult, DateWindow, RunSummary, SiteScope, Strategy
from seo_engine.domain.ports import DataConnector
from seo_engine.persistence.db import create_persistent_session
from seo_engine.persistence.repositories import ObservationRepository, RunRepository


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
        return IngestionSummary(run_id=existing_id, status="complete")

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
    settings,
    run_date: date | None = None,
    fixture_mode: bool = False,
) -> RunSummary:
    if not fixture_mode:
        raise RuntimeError("live mode requires configured provider credentials and a database")
    target_date = run_date or date.today()
    window = DateWindow(start=target_date - timedelta(days=6), end=target_date)
    scope = SiteScope(
        site_id=settings.site_id,
        site_url=settings.site_url,
        target_root=Path(settings.target_site_root),
        base_branch=settings.github_base_branch,
    )
    connector = GSCConnector(
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
    fixture_database = Path("artifacts/fixture.sqlite")
    fixture_database.parent.mkdir(parents=True, exist_ok=True)
    async with create_persistent_session(
        f"sqlite+aiosqlite:///{fixture_database.as_posix()}"
    ) as session:
        summary = await collect_all(
            [connector],
            window,
            scope,
            RunRepository(session),
            ObservationRepository(session),
        )
    observations = [item for result in summary.connector_results for item in result.observations]
    diagnostics = find_striking_distance(EvidenceSet(observations), DiagnosticConfig())
    opportunities = rank_diagnostics(diagnostics, Strategy(priority_offerings=["seo"]))
    brief_count = 0
    if opportunities:
        brief = build_brief(opportunities[0], Strategy(priority_offerings=["seo"]))
        artifact = Path("artifacts/briefs")
        artifact.mkdir(parents=True, exist_ok=True)
        artifact_name = hashlib.sha256(opportunities[0].fingerprint.encode()).hexdigest()[:16]
        (artifact / f"{artifact_name}.md").write_text(
            render_brief_markdown(brief), encoding="utf-8"
        )
        brief_count = 1
    return RunSummary(
        run_id=summary.run_id,
        status=summary.status,
        diagnostics=len(diagnostics),
        briefs=brief_count,
        errors=summary.errors,
    )
