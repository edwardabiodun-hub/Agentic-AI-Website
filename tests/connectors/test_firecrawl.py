from datetime import date

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
