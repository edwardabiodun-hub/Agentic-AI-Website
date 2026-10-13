from datetime import date

import pytest
from seo_engine.connectors.gsc import GSCConnector
from seo_engine.domain.models import DateWindow, SiteScope


class FakeGSCService:
    def searchanalytics(self):
        return self

    def query(self, **kwargs):
        self.request = kwargs
        return self

    def execute(self):
        return {
            "rows": [
                {
                    "keys": ["live keyword", "https://example.com/live"],
                    "clicks": 4,
                    "impressions": 40,
                    "ctr": 0.1,
                    "position": 8.2,
                }
            ]
        }


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


@pytest.mark.asyncio
async def test_gsc_live_mode_queries_search_console() -> None:
    connector = GSCConnector(
        property_name="https://example.com/",
        credentials=object(),
        service=FakeGSCService(),
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.status == "complete"
    assert result.observations[0].dimensions["query"] == "live keyword"
