from datetime import date

import pytest
from seo_engine.connectors.clarity import ClarityConnector
from seo_engine.domain.models import DateWindow, SiteScope


@pytest.mark.asyncio
async def test_clarity_rejects_unsupported_window() -> None:
    connector = ClarityConnector(payload=[])
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.status == "failed"
    assert "3 days" in result.errors[0]


@pytest.mark.asyncio
async def test_clarity_normalizes_friction_metrics() -> None:
    connector = ClarityConnector(
        payload=[
            {"metricName": "Rage Click Count", "information": [{"URL": "/page", "count": "4"}]}
        ]
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 3)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.observations[0].metrics["rage_click_count"] == 4
