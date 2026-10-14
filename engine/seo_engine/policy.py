from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from seo_engine.domain.models import Brief, ProposedChange, ValidationIssue, ValidationReport
from seo_engine.runrate_routes import OVERRIDES_PATH


@dataclass
class GenerationPolicy:
    allowed_routes: set[str] = field(default_factory=set)
    target_route: str = ""
    original_content: str = "{}"
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
    if len(parsed) > 1:
        issues.append(
            ValidationIssue(code="file_limit", message="Only one SEO data file may change")
        )
    lines = sum(change.file_change.content.count("\n") + 1 for change in parsed)
    if lines > policy.max_lines:
        issues.append(ValidationIssue(code="line_limit", message="Generated line limit exceeded"))
    original = json.loads(policy.original_content)
    if not isinstance(original, dict):
        raise ValueError("Original SEO metadata must be a JSON object")
    target = policy.target_route
    for change in parsed:
        path = change.file_change.path
        content = change.file_change.content
        if path != OVERRIDES_PATH:
            issues.append(
                ValidationIssue(
                    code="disallowed_path",
                    message="Only RunRate SEO metadata may change",
                    path=path,
                )
            )
        if not change.evidence_refs or not set(change.evidence_refs).issubset(
            {item.reference for item in brief.evidence}
        ):
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
        try:
            proposed = json.loads(content)
        except json.JSONDecodeError:
            issues.append(
                ValidationIssue(
                    code="invalid_json", message="SEO data is not valid JSON", path=path
                )
            )
            continue
        if not isinstance(proposed, dict):
            issues.append(
                ValidationIssue(
                    code="invalid_schema", message="SEO data must be an object", path=path
                )
            )
            continue
        changed = {
            key
            for key in original.keys() | proposed.keys()
            if original.get(key) != proposed.get(key)
        }
        if changed != {target} or any(key not in policy.allowed_routes for key in proposed):
            issues.append(
                ValidationIssue(
                    code="route_scope",
                    message="Only one indexable RunRate route may change",
                    path=path,
                )
            )
        if any(key not in proposed for key in original):
            issues.append(
                ValidationIssue(
                    code="deletion", message="Existing metadata cannot be deleted", path=path
                )
            )
        for value in proposed.values():
            if not isinstance(value, dict) or set(value) != {"title", "description"}:
                issues.append(
                    ValidationIssue(
                        code="invalid_schema",
                        message="Only title and description are allowed",
                        path=path,
                    )
                )
                continue
            title, description = value["title"], value["description"]
            if (
                not isinstance(title, str)
                or not isinstance(description, str)
                or not 15 <= len(title) <= 75
                or not 50 <= len(description) <= 170
            ):
                issues.append(
                    ValidationIssue(
                        code="invalid_metadata", message="Metadata length is invalid", path=path
                    )
                )
                continue
            if re.search(
                r"[<>]|https?://|\b(?:guaranteed|#1 ranking)\b", title + description, re.I
            ):
                issues.append(
                    ValidationIssue(
                        code="unsafe_claim", message="Unsafe metadata claim or markup", path=path
                    )
                )
    return ValidationReport(issues=issues)
