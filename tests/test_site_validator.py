from pathlib import Path

from seo_engine.domain.models import FileChange
from seo_engine.site_validator import apply_changes, validate_site


def test_valid_site_passes_validation(tmp_path: Path) -> None:
    page = tmp_path / "site" / "page.html"
    page.parent.mkdir()
    page.write_text(
        """
        <html><head><title>Page</title>
        <meta name="description" content="Desc">
        <link rel="canonical" href="https://example.com/page"></head>
        <body><h1>Page</h1><a href="/page.html">Link</a></body></html>
        """,
        encoding="utf-8",
    )
    assert validate_site(tmp_path, ["site/page.html"]).valid


def test_invalid_structure_and_path_are_rejected(tmp_path: Path) -> None:
    page = tmp_path / "site" / "page.html"
    page.parent.mkdir()
    page.write_text(
        """
        <html><head><title>Page</title>
        <link rel="canonical" href="https://wrong.example"></head>
        <body><h1>A</h1><h1>B</h1><a href="/missing.html">Broken</a></body></html>
        """,
        encoding="utf-8",
    )
    report = validate_site(tmp_path, ["site/page.html"])
    assert not report.valid
    assert {issue.code for issue in report.issues} >= {
        "duplicate_h1",
        "missing_description",
        "broken_link",
    }


def test_apply_changes_blocks_path_traversal(tmp_path: Path) -> None:
    result = apply_changes(tmp_path, [FileChange(path="site/../secret.txt", content="secret")])
    assert not result.valid
