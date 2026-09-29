from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class FirecrawlConnector:
    name = "firecrawl"

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {"success": True, "data": {}}

    async def scrape(self, url: str) -> dict[str, Any]:
        return self.payload.get("data", {})

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
            metrics={"status_code": float(metadata.get("statusCode", 0))},
            evidence_ref=f"firecrawl:{window.start}:{window.end}",
        )
        return CollectionResult(
            source=self.name, observations=[observation], status="complete", quota={}
        )
