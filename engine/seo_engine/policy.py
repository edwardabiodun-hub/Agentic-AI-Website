from __future__ import annotations

from dataclasses import dataclass, field

from seo_engine.domain.models import Brief, ProposedChange, ValidationIssue, ValidationReport


@dataclass
class GenerationPolicy:
    allowed_root: str = "site/"
    max_files: int = 5
    max_lines: int = 250
    secrets: list[str] = field(default_factory=list)


def validate_generation(
    changes: list[ProposedChange | dict], brief: Brief, policy: GenerationPolicy
) -> ValidationReport:
    parsed = [
        change if isinstance(change, ProposedChange) else ProposedChange.model_validate(change)
        for change in changes
    ]
    issues: list[ValidationIssue] = []
    if len(parsed) > policy.max_files:
        issues.append(ValidationIssue(code="file_limit", message="Generated file limit exceeded"))
    lines = sum(change.file_change.content.count("\n") + 1 for change in parsed)
    if lines > policy.max_lines:
        issues.append(ValidationIssue(code="line_limit", message="Generated line limit exceeded"))
    for change in parsed:
        path = change.file_change.path
        content = change.file_change.content
        if not path.startswith(policy.allowed_root):
            issues.append(
                ValidationIssue(
                    code="disallowed_path",
                    message="Generated path is outside the target root",
                    path=path,
                )
            )
        if not change.evidence_refs:
            issues.append(
                ValidationIssue(
                    code="missing_evidence", message="Generated change has no evidence", path=path
                )
            )
        for secret in policy.secrets:
            if secret and secret in content:
                issues.append(
                    ValidationIssue(
                        code="secret_match",
                        message="Generated content contains a configured secret",
                        path=path,
                    )
                )
    return ValidationReport(issues=issues)
