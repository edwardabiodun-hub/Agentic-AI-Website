from datetime import date

import pytest
from seo_engine.connectors.gsc import GSCConnector
from seo_engine.domain.models import DateWindow, SiteScope


@pytest.mark.asyncio
async def test_gsc_normalizes_query_rows() -> None:
    connector = GSCConnector(
        payload={
            "rows": [
                {
                    "keys": ["seo strategy", "https://example.com/page"],
                    "clicks": 10,
                    "impressions": 100,
                    "ctr": 0.1,
                    "position": 9.5,
                }
            ]
        }
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.status == "complete"
    assert result.observations[0].dimensions["query"] == "seo strategy"
    assert result.observations[0].metrics["position"] == 9.5
