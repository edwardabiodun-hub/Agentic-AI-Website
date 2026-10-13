from datetime import date

import pytest
from seo_engine.connectors.ga4 import GA4Connector
from seo_engine.domain.models import DateWindow, SiteScope


class Value:
    def __init__(self, value: str) -> None:
        self.value = value


class Row:
    dimension_values = [Value("/live")]
    metric_values = [Value("100"), Value("20"), Value("0.75"), Value("3")]


class Response:
    rows = [Row()]


class FakeGA4Client:
    def run_report(self, *, request):
        self.request = request
        return Response()


@pytest.mark.asyncio
async def test_ga4_normalizes_report_rows() -> None:
    connector = GA4Connector(
        payload={
            "rows": [
                {
                    "dimensionValues": [{"value": "/page"}],
                    "metricValues": [{"value": "100"}, {"value": "20"}, {"value": "0.8"}],
                }
            ]
        }
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.observations[0].dimensions["page"] == "/page"
    assert result.observations[0].metrics["sessions"] == 20


@pytest.mark.asyncio
async def test_ga4_live_mode_runs_page_report() -> None:
    connector = GA4Connector(
        property_id="123456",
        credentials=object(),
        client=FakeGA4Client(),
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.status == "complete"
    assert result.observations[0].dimensions["page"] == "/live"
    assert result.observations[0].metrics["conversions"] == 3
