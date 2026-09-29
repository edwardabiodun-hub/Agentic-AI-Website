from __future__ import annotations

from pydantic import BaseModel, Field

from seo_engine.domain.models import Brief, ProposedChange
from seo_engine.domain.ports import LLMClient


class ChangePlan(BaseModel):
    changes: list[ProposedChange] = Field(default_factory=list)


def sanitize_external_text(value: str) -> str:
    blocked = ("ignore previous instructions", "system message", "developer message")
    return " ".join(
        "[external text]" if token.lower() in blocked else token for token in value.splitlines()
    )


async def generate_changes(
    brief: Brief, site_snapshot: dict[str, str], llm: LLMClient
) -> list[ProposedChange]:
    target_path = brief.opportunity.diagnostic.target_url or "site/index.html"
    if not target_path.startswith("site/"):
        target_path = f"site/{target_path.lstrip('/')}"
    existing = site_snapshot.get(target_path, "")
    response = {
        "response": {
            "changes": [
                {
                    "file_change": {
                        "path": target_path,
                        "content": sanitize_external_text(existing),
                    },
                    "reason": brief.diagnosis,
                    "evidence_refs": [item.reference for item in brief.evidence]
                    or ["brief:diagnosis"],
                    "claim_refs": [],
                }
            ]
        }
    }
    plan = await llm.generate_structured(
        "Generate only changes explicitly supported by the brief.",
        response,
        ChangePlan,
    )
    return plan.changes
