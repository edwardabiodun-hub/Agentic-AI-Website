from datetime import date

import pytest
from seo_engine.connectors.ga4 import GA4Connector
from seo_engine.domain.models import DateWindow, SiteScope


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
