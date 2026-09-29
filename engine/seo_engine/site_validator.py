from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from seo_engine.domain.models import FileChange, ValidationIssue, ValidationReport


@dataclass
class PatchResult:
    valid: bool
    changed_paths: list[str]
    issues: list[ValidationIssue]


def _safe_path(root: Path, relative: str) -> Path | None:
    normalized = Path(relative.replace("\\", "/"))
    if not relative.replace("\\", "/").startswith("site/") or ".." in normalized.parts:
        return None
    candidate = (root / normalized).resolve()
    site_root = (root / "site").resolve()
    if candidate != site_root and site_root not in candidate.parents:
        return None
    return candidate


def validate_site(root: Path, changed_paths: list[str]) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for relative in changed_paths:
        path = _safe_path(root, relative)
        if path is None:
            issues.append(
                ValidationIssue(
                    code="disallowed_path", message="Path is outside site/", path=relative
                )
            )
            continue
        if not path.exists():
            issues.append(
                ValidationIssue(
                    code="missing_file", message="Changed file does not exist", path=relative
                )
            )
            continue
        if path.suffix.lower() != ".html":
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        if not soup.title or not soup.title.get_text(strip=True):
            issues.append(
                ValidationIssue(
                    code="missing_title", message="Page requires a title", path=relative
                )
            )
        description = soup.find("meta", attrs={"name": "description"})
        if not description or not description.get("content", "").strip():
            issues.append(
                ValidationIssue(
                    code="missing_description", message="Page requires a description", path=relative
                )
            )
        canonicals = soup.find_all("link", attrs={"rel": "canonical"})
        if len(canonicals) != 1 or not canonicals[0].get("href"):
            issues.append(
                ValidationIssue(
                    code="invalid_canonical",
                    message="Page requires one canonical URL",
                    path=relative,
                )
            )
        if len(soup.find_all("h1")) != 1:
            issues.append(
                ValidationIssue(
                    code="duplicate_h1", message="Page requires exactly one H1", path=relative
                )
            )
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("/") and not (root / "site" / href.lstrip("/")).exists():
                issues.append(
                    ValidationIssue(
                        code="broken_link",
                        message=f"Internal link does not resolve: {href}",
                        path=relative,
                    )
                )
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                json.loads(script.get_text())
            except json.JSONDecodeError:
                issues.append(
                    ValidationIssue(
                        code="invalid_jsonld", message="JSON-LD is invalid JSON", path=relative
                    )
                )
    return ValidationReport(issues=issues)


def apply_changes(root: Path, changes: list[FileChange]) -> PatchResult:
    issues: list[ValidationIssue] = []
    changed: list[str] = []
    for change in changes:
        path = _safe_path(root, change.path)
        if path is None:
            issues.append(
                ValidationIssue(
                    code="disallowed_path", message="Path is outside site/", path=change.path
                )
            )
            continue
        if change.original_sha256 and path.exists():
            current = hashlib.sha256(path.read_bytes()).hexdigest()
            if current != change.original_sha256:
                issues.append(
                    ValidationIssue(
                        code="content_conflict",
                        message="Original file hash changed",
                        path=change.path,
                    )
                )
                continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="seo-change-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(change.content)
            os.replace(temp_name, path)
            changed.append(change.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    if issues:
        return PatchResult(valid=False, changed_paths=changed, issues=issues)
    report = validate_site(root, changed)
    return PatchResult(valid=report.valid, changed_paths=changed, issues=report.issues)
