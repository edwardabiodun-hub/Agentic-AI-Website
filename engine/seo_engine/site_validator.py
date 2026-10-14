from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from seo_engine.domain.models import FileChange, ValidationIssue, ValidationReport
from seo_engine.runrate_routes import OVERRIDES_PATH, indexable_routes


@dataclass
class PatchResult:
    valid: bool
    changed_paths: list[str]
    issues: list[ValidationIssue]


def _safe_path(root: Path, relative: str) -> Path | None:
    if relative != OVERRIDES_PATH:
        return None
    candidate = (root / relative).resolve()
    return candidate if candidate == (root / OVERRIDES_PATH).resolve() else None


def _validate_content(root: Path, content: str) -> list[ValidationIssue]:
    try:
        overrides = json.loads(content)
    except json.JSONDecodeError:
        return [ValidationIssue(code="invalid_json", message="SEO overrides must be valid JSON")]
    if not isinstance(overrides, dict):
        return [ValidationIssue(code="invalid_schema", message="SEO overrides must be an object")]
    routes = indexable_routes(root)
    issues: list[ValidationIssue] = []
    for route, value in overrides.items():
        if route not in routes:
            issues.append(
                ValidationIssue(code="unknown_route", message=f"Not an indexable route: {route}")
            )
        if not isinstance(value, dict) or set(value) != {"title", "description"}:
            issues.append(
                ValidationIssue(code="invalid_schema", message=f"Invalid SEO entry: {route}")
            )
            continue
        if not all(isinstance(value[key], str) for key in ("title", "description")):
            issues.append(
                ValidationIssue(code="invalid_schema", message=f"Invalid SEO text: {route}")
            )
    return issues


def validate_site(root: Path, changed_paths: list[str]) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for relative in changed_paths:
        path = _safe_path(root, relative)
        if path is None:
            issues.append(
                ValidationIssue(
                    code="disallowed_path",
                    message="Only RunRate SEO data may change",
                    path=relative,
                )
            )
        elif not path.is_file():
            issues.append(
                ValidationIssue(
                    code="missing_file", message="SEO data file does not exist", path=relative
                )
            )
        else:
            issues.extend(_validate_content(root, path.read_text(encoding="utf-8")))
    return ValidationReport(issues=issues)


def apply_changes(root: Path, changes: list[FileChange]) -> PatchResult:
    """Validate the complete patch before the first write, preventing partial application."""
    issues: list[ValidationIssue] = []
    if len(changes) > 1:
        issues.append(ValidationIssue(code="file_limit", message="Only one SEO file may change"))
    for change in changes:
        path = _safe_path(root, change.path)
        if path is None:
            issues.append(
                ValidationIssue(
                    code="disallowed_path",
                    message="Only RunRate SEO data may change",
                    path=change.path,
                )
            )
            continue
        if not path.is_file():
            issues.append(
                ValidationIssue(
                    code="missing_file", message="SEO data file does not exist", path=change.path
                )
            )
            continue
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if change.original_sha256 and current != change.original_sha256:
            issues.append(
                ValidationIssue(
                    code="content_conflict", message="Original file hash changed", path=change.path
                )
            )
        issues.extend(_validate_content(root, change.content))
    if issues:
        return PatchResult(valid=False, changed_paths=[], issues=issues)
    changed: list[str] = []
    for change in changes:
        path = root / change.path
        fd, temp_name = tempfile.mkstemp(prefix="seo-change-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(change.content)
            os.replace(temp_name, path)
            changed.append(change.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    return PatchResult(valid=True, changed_paths=changed, issues=[])
