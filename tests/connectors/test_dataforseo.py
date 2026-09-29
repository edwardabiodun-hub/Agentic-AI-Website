from datetime import date

import pytest
from seo_engine.connectors.dataforseo import DataForSEOConnector
from seo_engine.domain.models import DateWindow, SiteScope


@pytest.mark.asyncio
async def test_dataforseo_normalizes_serp_result() -> None:
    connector = DataForSEOConnector(
        payload={
            "tasks": [
                {
                    "result": [
                        {
                            "keyword": "seo strategy",
                            "search_volume": 500,
                            "items": [
                                {
                                    "type": "organic",
                                    "rank_absolute": 3,
                                    "url": "https://example.com/page",
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.observations[0].dimensions["keyword"] == "seo strategy"
    assert result.observations[0].metrics["rank"] == 3
