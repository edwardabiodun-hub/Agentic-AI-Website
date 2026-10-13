from datetime import date

import httpx
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
    assert result.status == "partial"
    assert "latest 3 days" in result.errors[0]


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


@pytest.mark.asyncio
async def test_clarity_live_mode_exports_dashboard_data() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer token"
        assert request.url.params["numOfDays"] == "3"
        return httpx.Response(
            200,
            json=[
                {
                    "metricName": "Dead Click Count",
                    "information": [{"URL": "/live", "count": "2"}],
                }
            ],
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    connector = ClarityConnector(project_id="project", api_token="token", client=client)
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 3)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    await client.aclose()
    assert result.status == "complete"
    assert result.observations[0].metrics["dead_click_count"] == 2
