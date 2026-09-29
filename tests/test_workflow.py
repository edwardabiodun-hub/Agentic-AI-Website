from datetime import date

import pytest
from seo_engine.api import create_app
from seo_engine.cli import build_cli
from seo_engine.config import Settings
from seo_engine.workflow import run_weekly
from typer.testing import CliRunner


@pytest.mark.asyncio
async def test_fixture_weekly_run_is_idempotent() -> None:
    settings = Settings(site_id="demo", site_url="https://example.com", target_site_root="site")
    first = await run_weekly(settings, date(2026, 9, 29), fixture_mode=True)
    second = await run_weekly(settings, date(2026, 9, 29), fixture_mode=True)
    assert first.run_id == second.run_id
    assert first.status in {"complete", "partial"}


def test_status_api_has_health_route() -> None:
    routes = {route.path for route in create_app().routes}
    assert "/healthz" in routes


def test_cli_exposes_weekly_pipeline_commands() -> None:
    result = CliRunner().invoke(build_cli(), ["--help"])
    assert result.exit_code == 0
    for command in ("collect", "diagnose", "generate-brief", "run-weekly"):
        assert command in result.stdout
