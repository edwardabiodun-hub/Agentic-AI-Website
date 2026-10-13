from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_ci_workflow_checks_code_and_schema() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "ruff check" in workflow
    assert "pytest" in workflow
    assert "alembic check" in workflow


def test_ci_migrates_fresh_schema_before_alembic_check() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    upgrade = workflow.index("uv run alembic upgrade head")
    check = workflow.index("uv run alembic check")

    assert upgrade < check
    assert "DATABASE_URL: sqlite:///./ci-seo-engine.db" in workflow


def test_weekly_workflow_is_scheduled_and_non_deploying() -> None:
    workflow = (ROOT / ".github" / "workflows" / "weekly-seo.yml").read_text(encoding="utf-8")
    assert "0 13 * * 1" in workflow
    assert "workflow_dispatch" in workflow
    assert "seo-engine run-weekly" in workflow
    assert "upload-artifact" in workflow
    assert "vercel --prod" not in workflow
    assert "production" not in workflow.lower()


def test_operations_docs_cover_provider_vercel_and_runbook_controls() -> None:
    provider = (ROOT / "docs" / "operations" / "provider-setup.md").read_text(encoding="utf-8")
    vercel = (ROOT / "docs" / "operations" / "vercel-github-setup.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs" / "operations" / "weekly-runbook.md").read_text(encoding="utf-8")
    assert "GSC" in provider and "Clarity" in provider and "DataForSEO" in provider
    assert "preview" in vercel.lower() and "merge" in vercel.lower()
    assert "rollback" in runbook.lower() and "partial" in runbook.lower()
