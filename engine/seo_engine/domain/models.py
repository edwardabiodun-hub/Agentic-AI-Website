from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class DateWindow(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def ordered(self) -> DateWindow:
        if self.end < self.start:
            raise ValueError("end must be on or after start")
        return self


class SiteScope(BaseModel):
    site_id: str
    site_url: AnyHttpUrl
    target_root: Path
    base_branch: str = "main"


class NormalizedObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    observed_at: datetime
    dimensions: dict[str, str] = Field(default_factory=dict)
    metrics: dict[str, float | None] = Field(default_factory=dict)
    evidence_ref: str

    @field_validator("metrics")
    @classmethod
    def valid_metrics(cls, value: dict[str, float | None]) -> dict[str, float | None]:
        if value.get("ctr") is not None and not 0 <= value["ctr"] <= 1:
            raise ValueError("ctr must be between 0 and 1")
        if value.get("position") is not None and value["position"] < 0:
            raise ValueError("position must be non-negative")
        for key in ("clicks", "impressions"):
            if value.get(key) is not None and value[key] < 0:
                raise ValueError(f"{key} must be non-negative")
        return value


class CollectionResult(BaseModel):
    source: str
    observations: list[NormalizedObservation] = Field(default_factory=list)
    status: Literal["complete", "partial", "failed"]
    errors: list[str] = Field(default_factory=list)
    quota: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def errors_for_noncomplete(self) -> CollectionResult:
        if self.status != "complete" and not self.errors:
            raise ValueError("partial or failed collection requires an error")
        return self


class EvidenceItem(BaseModel):
    source: str
    reference: str
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)


class Diagnostic(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: str
    target_url: str | None = None
    target_query: str | None = None
    summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    score: float = 0
    risk: str = "low"


class Opportunity(BaseModel):
    diagnostic: Diagnostic
    page_archetype: str = "service"
    strategy_alignment: str = "unreviewed"
    fingerprint: str

    @classmethod
    def from_diagnostic(
        cls, diagnostic: Diagnostic, page_archetype: str = "service"
    ) -> Opportunity:
        raw = json.dumps(
            {
                "kind": diagnostic.kind,
                "url": diagnostic.target_url,
                "query": diagnostic.target_query,
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return cls(diagnostic=diagnostic, page_archetype=page_archetype, fingerprint=fingerprint)


class StrategyAlignment(BaseModel):
    status: Literal["aligned", "neutral", "excluded"]
    rationale: str
    score_delta: float = 0


class Strategy(BaseModel):
    audiences: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    priority_offerings: list[str] = Field(default_factory=list)
    conversions: list[str] = Field(default_factory=list)
    approved_archetypes: list[str] = Field(
        default_factory=lambda: ["service", "guide", "faq", "comparison"]
    )
    excluded_paths: list[str] = Field(default_factory=list)
    proof_requirements: list[str] = Field(default_factory=list)
    change_limits: dict[str, int] = Field(
        default_factory=lambda: {"max_files": 5, "max_lines": 250}
    )


class Brief(BaseModel):
    opportunity: Opportunity
    diagnosis: str
    evidence: list[EvidenceItem]
    recommended_changes: list[str]
    internal_links: list[str] = Field(default_factory=list)
    schema_plan: list[str] = Field(default_factory=list)
    conversion_implications: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    success_metrics: list[str]
    rollback: str
    confidence: float = Field(ge=0, le=1)


class FileChange(BaseModel):
    path: str
    content: str
    original_sha256: str | None = None


class ProposedChange(BaseModel):
    file_change: FileChange
    reason: str
    evidence_refs: list[str]
    claim_refs: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    code: str
    message: str
    path: str | None = None
    severity: Literal["error", "warning"] = "error"


class ValidationReport(BaseModel):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.issues)


class RunSummary(BaseModel):
    run_id: UUID
    status: Literal["complete", "partial", "failed"]
    diagnostics: int = 0
    briefs: int = 0
    pull_request_url: str | None = None
    errors: list[str] = Field(default_factory=list)
