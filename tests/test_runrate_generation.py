import json
from pathlib import Path

import pytest
from seo_engine.briefs import build_brief
from seo_engine.domain.models import Diagnostic, EvidenceItem, FileChange, Opportunity, Strategy
from seo_engine.generation import generate_changes
from seo_engine.llm import FakeLLMClient
from seo_engine.policy import GenerationPolicy, validate_generation
from seo_engine.runrate_routes import OVERRIDES_PATH, indexable_routes, resolve_target_route
from seo_engine.site_validator import apply_changes, validate_site
from seo_engine.strategy import load_strategy

ROOT = Path(__file__).parents[1]
SITE_URL = "https://www.runrategroup.com"


def brief(target=f"{SITE_URL}/diagnostic"):
    diagnostic = Diagnostic(
        kind="striking_distance",
        target_url=target,
        target_query="business independence diagnostic",
        summary="Relevant existing page is near page one.",
        evidence=[
            EvidenceItem(source="gsc", reference="gsc:test", summary="Position 12, 200 impressions")
        ],
        confidence=0.9,
    )
    return build_brief(Opportunity(diagnostic=diagnostic, fingerprint="test"), Strategy())


def test_route_inventory_matches_application() -> None:
    routes = indexable_routes(ROOT)
    assert "/diagnostic" in routes
    assert "/founder-resources/automation-before-ai" in routes
    assert "/privacy" not in routes
    assert "/contact/thank-you" not in routes
    assert validate_site(ROOT, [OVERRIDES_PATH]).valid


def test_weekly_strategy_is_runrate_specific() -> None:
    strategy = load_strategy(ROOT / "config/strategy.yaml")
    assert "owner dependency" in strategy.priority_offerings
    assert "seo" not in strategy.priority_offerings
    assert "/admin" in strategy.excluded_paths


@pytest.mark.parametrize(
    "target",
    [
        "https://competitor.example/diagnostic",
        "https://www.runrategroup.com/admin/metrics",
        "https://www.runrategroup.com/founder-resources/not-a-real-slug",
        "https://www.runrategroup.com/diagnostic?ref=search",
        "site/pages/example-service.html",
    ],
)
def test_external_unknown_and_demo_targets_rejected(target):
    with pytest.raises(ValueError):
        resolve_target_route(target, SITE_URL, indexable_routes(ROOT))


def test_gsc_absolute_url_maps_to_real_route():
    assert (
        resolve_target_route(f"{SITE_URL}/assessment/", SITE_URL, indexable_routes(ROOT))
        == "/assessment"
    )


@pytest.mark.asyncio
async def test_generation_targets_runrate_metadata_only():
    original = (ROOT / OVERRIDES_PATH).read_text(encoding="utf-8")
    changes = await generate_changes(
        brief(), {OVERRIDES_PATH: original}, FakeLLMClient(), site_url=SITE_URL, repo_root=ROOT
    )
    assert len(changes) == 1
    assert changes[0].file_change.path == OVERRIDES_PATH
    assert "/diagnostic" in json.loads(changes[0].file_change.content)
    report = validate_generation(
        changes,
        brief(),
        GenerationPolicy(
            allowed_routes=indexable_routes(ROOT),
            target_route="/diagnostic",
            original_content=original,
        ),
    )
    assert report.valid, report.issues


def test_policy_blocks_code_secret_and_unrelated_route():
    code = [
        {
            "file_change": FileChange(path="app/assessment/page.tsx", content="secret"),
            "reason": "bad",
            "evidence_refs": [],
        }
    ]
    report = validate_generation(
        code,
        brief(),
        GenerationPolicy(
            allowed_routes=indexable_routes(ROOT), target_route="/diagnostic", secrets=["secret"]
        ),
    )
    assert {issue.code for issue in report.issues} >= {
        "disallowed_path",
        "secret_match",
        "missing_evidence",
    }
    unrelated = [
        {
            "file_change": FileChange(
                path=OVERRIDES_PATH,
                content=json.dumps(
                    {
                        "/about": {
                            "title": "Guaranteed #1 Ranking for Any Business",
                            "description": (
                            "Guaranteed top Google ranking for all businesses "
                            "with no investment "
                                "and no work required by anyone."
                            ),
                        }
                    }
                ),
            ),
            "reason": "bad",
            "evidence_refs": ["gsc:test"],
        }
    ]
    report = validate_generation(
        unrelated,
        brief(),
        GenerationPolicy(allowed_routes=indexable_routes(ROOT), target_route="/diagnostic"),
    )
    assert {issue.code for issue in report.issues} >= {"route_scope", "unsafe_claim"}


def test_apply_rejects_demo_code_and_invalid_route_without_writing():
    assert not apply_changes(ROOT, [FileChange(path="site/index.html", content="x")]).valid
    assert not apply_changes(ROOT, [FileChange(path="app/page.tsx", content="x")]).valid
    before = (ROOT / OVERRIDES_PATH).read_text(encoding="utf-8")
    result = apply_changes(
        ROOT,
        [
            FileChange(
                path=OVERRIDES_PATH,
                content=json.dumps({"/no-such-route": {"title": "Bad", "description": "Bad"}}),
            )
        ],
    )
    assert not result.valid
    assert (ROOT / OVERRIDES_PATH).read_text(encoding="utf-8") == before
