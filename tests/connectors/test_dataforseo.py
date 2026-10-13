import json
from datetime import date

import httpx
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


@pytest.mark.asyncio
async def test_dataforseo_live_mode_queries_bounded_keywords() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"].startswith("Basic ")
        assert json.loads(request.content)[0]["keyword"] == "seo strategy"
        return httpx.Response(
            200,
            json={
                "status_code": 20000,
                "cost": 0.003,
                "tasks": [
                    {
                        "result": [
                            {
                                "keyword": "seo strategy",
                                "items": [
                                    {
                                        "type": "organic",
                                        "rank_absolute": 4,
                                        "url": "https://example.com/live",
                                    }
                                ],
                            }
                        ]
                    }
                ],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    connector = DataForSEOConnector(
        login="login",
        password="password",
        keywords=["seo strategy"],
        client=client,
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    await client.aclose()
    assert result.status == "complete"
    assert result.observations[0].metrics["rank"] == 4
