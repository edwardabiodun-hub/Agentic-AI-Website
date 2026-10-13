from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class FirecrawlConnector:
    name = "firecrawl"

    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        api_key: str = "",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.payload = payload
        self.api_key = api_key
        self.client = client

    async def scrape(self, url: str) -> dict[str, Any]:
        if self.payload is not None:
            return self.payload.get("data", {})
        if not self.api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is not configured")
        close_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=60)
        try:
            response = await client.post(
                "https://api.firecrawl.dev/v2/scrape",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"url": url, "formats": ["markdown", "links"], "onlyMainContent": True},
            )
            response.raise_for_status()
            body = response.json()
            if body.get("success") is False:
                raise RuntimeError(body.get("error", "Firecrawl returned an unsuccessful response"))
            return body.get("data", body)
        finally:
            if close_client:
                await client.aclose()

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        data = await self.scrape(str(scope.site_url))
        metadata = data.get("metadata", {})
        observation = NormalizedObservation(
            source=self.name,
            observed_at=datetime.now(UTC),
            dimensions={
                "url": metadata.get("sourceURL", str(scope.site_url)),
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
            },
            metrics={
                "status_code": float(metadata.get("statusCode", 200)),
                "word_count": float(len(data.get("markdown", "").split())),
                "internal_link_count": float(
                    sum(1 for link in data.get("links", []) if str(scope.site_url) in link)
                ),
            },
            evidence_ref=f"firecrawl:{window.start}:{window.end}",
        )
        return CollectionResult(
            source=self.name, observations=[observation], status="complete", quota={}
        )
