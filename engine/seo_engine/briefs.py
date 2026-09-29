from __future__ import annotations

from seo_engine.domain.models import Brief, Opportunity, Strategy
from seo_engine.strategy import compare_strategy


def build_brief(opportunity: Opportunity, strategy: Strategy) -> Brief:
    alignment = compare_strategy(opportunity, strategy)
    return Brief(
        opportunity=opportunity,
        diagnosis=opportunity.diagnostic.summary,
        evidence=opportunity.diagnostic.evidence,
        recommended_changes=[
            "Improve the opening answer and page structure.",
            "Refresh metadata and structured data where evidence supports it.",
        ],
        internal_links=[],
        schema_plan=["Preserve valid JSON-LD and update only supported properties."],
        conversion_implications=[
            "Keep the primary CTA visible and aligned to the configured conversion."
        ],
        risks=["Do not introduce unsupported claims or duplicate search intent."],
        success_metrics=["Clicks", "Average position", "Conversion rate"],
        rollback="Revert the generated commit if validation or post-deployment metrics regress.",
        confidence=opportunity.diagnostic.confidence,
    ).model_copy(
        update={
            "opportunity": opportunity.model_copy(update={"strategy_alignment": alignment.status})
        }
    )


def render_brief_markdown(brief: Brief) -> str:
    evidence = "\n".join(
        f"- {item.source}: {item.summary} ({item.reference})" for item in brief.evidence
    )
    changes = "\n".join(f"- {item}" for item in brief.recommended_changes)
    metrics = "\n".join(f"- {item}" for item in brief.success_metrics)
    return f"""# SEO Opportunity Brief

## Diagnosis

{brief.diagnosis}

## Evidence

{evidence or "- No evidence recorded."}

## Recommended changes

{changes}

## Success metrics

{metrics}

## Risks

{chr(10).join(f"- {item}" for item in brief.risks)}

## Rollback

{brief.rollback}
"""
