from datetime import date

import httpx
import pytest
from seo_engine.connectors.firecrawl import FirecrawlConnector
from seo_engine.domain.models import DateWindow, SiteScope


@pytest.mark.asyncio
async def test_firecrawl_extracts_page_evidence() -> None:
    connector = FirecrawlConnector(
        payload={
            "success": True,
            "data": {
                "markdown": "# Page",
                "metadata": {
                    "title": "Page",
                    "description": "Desc",
                    "sourceURL": "https://example.com/page",
                    "statusCode": 200,
                },
                "links": ["https://example.com/other"],
            },
        }
    )
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    assert result.observations[0].dimensions["title"] == "Page"
    assert result.observations[0].dimensions["url"] == "https://example.com/page"


@pytest.mark.asyncio
async def test_firecrawl_live_mode_scrapes_target_page() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer firecrawl"
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": {
                    "markdown": "# Live page",
                    "metadata": {
                        "title": "Live page",
                        "description": "Live description",
                        "sourceURL": "https://example.com/live",
                        "statusCode": 200,
                    },
                    "links": ["https://example.com/other"],
                },
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    connector = FirecrawlConnector(api_key="firecrawl", client=client)
    result = await connector.collect(
        DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
        SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
    )
    await client.aclose()
    assert result.status == "complete"
    assert result.observations[0].dimensions["title"] == "Live page"
