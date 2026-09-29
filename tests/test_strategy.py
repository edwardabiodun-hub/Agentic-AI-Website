from seo_engine.briefs import build_brief, render_brief_markdown
from seo_engine.domain.models import Diagnostic, Opportunity, Strategy
from seo_engine.strategy import adjust_priorities


def make_opportunity() -> Opportunity:
    return Opportunity(
        diagnostic=Diagnostic(
            kind="striking_distance",
            target_url="/services/seo",
            target_query="seo service",
            summary="Improve page one visibility.",
            confidence=0.9,
            score=50,
        ),
        page_archetype="service",
        fingerprint="op-1",
    )


def test_strategy_alignment_prioritizes_service_page() -> None:
    strategy = Strategy(priority_offerings=["seo"], conversions=["lead_form"])
    ranked = adjust_priorities([make_opportunity()], strategy)
    assert ranked[0].strategy_alignment == "aligned"


def test_brief_contains_evidence_metrics_and_rollback() -> None:
    opportunity = make_opportunity()
    brief = build_brief(opportunity, Strategy(priority_offerings=["seo"]))
    markdown = render_brief_markdown(brief)
    assert "Evidence" in markdown
    assert "Success metrics" in markdown
    assert "Rollback" in markdown
