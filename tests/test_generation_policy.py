import pytest
from seo_engine.briefs import build_brief
from seo_engine.domain.models import Diagnostic, FileChange, Opportunity, Strategy
from seo_engine.generation import generate_changes
from seo_engine.llm import FakeLLMClient
from seo_engine.policy import GenerationPolicy, validate_generation


def brief() -> object:
    opportunity = Opportunity(
        diagnostic=Diagnostic(
            kind="striking_distance",
            target_url="/pages/example-service.html",
            target_query="seo service",
            summary="Improve page one visibility.",
            confidence=0.9,
            score=50,
        ),
        page_archetype="service",
        fingerprint="op-1",
    )
    return build_brief(opportunity, Strategy(priority_offerings=["seo"]))


@pytest.mark.asyncio
async def test_fake_generation_returns_bounded_site_change() -> None:
    changes = await generate_changes(
        brief(),
        {"site/pages/example-service.html": "<h1>SEO strategy service</h1>"},
        FakeLLMClient(),
    )
    assert changes[0].file_change.path.startswith("site/")
    assert changes[0].evidence_refs


def test_policy_rejects_secret_and_disallowed_path() -> None:
    changes = [
        {
            "file_change": FileChange(path="engine/secrets.txt", content="OPENAI_API_KEY=secret"),
            "reason": "bad",
            "evidence_refs": [],
        }
    ]
    report = validate_generation(
        changes,
        brief(),
        GenerationPolicy(allowed_root="site/", secrets=["secret"]),
    )
    assert not report.valid
    assert {issue.code for issue in report.issues} == {
        "disallowed_path",
        "secret_match",
        "missing_evidence",
    }
