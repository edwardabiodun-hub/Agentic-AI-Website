from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class DataForSEOConnector:
    name = "dataforseo"

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {"tasks": []}

    async def track_keywords(
        self, keywords: list[str], location_code: int, language_code: str
    ) -> CollectionResult:
        return await self.collect(
            DateWindow(start=datetime.now(UTC).date(), end=datetime.now(UTC).date()),
            SiteScope(site_id="keywords", site_url="https://example.com", target_root="site"),
        )

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        observations = []
        for task_index, task in enumerate(self.payload.get("tasks", [])):
            for result_index, result in enumerate(task.get("result", [])):
                for item in result.get("items", []):
                    if item.get("type") != "organic":
                        continue
                    observations.append(
                        NormalizedObservation(
                            source=self.name,
                            observed_at=datetime.now(UTC),
                            dimensions={
                                "keyword": result.get("keyword", ""),
                                "url": item.get("url", ""),
                            },
                            metrics={
                                "search_volume": result.get("search_volume"),
                                "rank": item.get("rank_absolute"),
                            },
                            evidence_ref=f"dataforseo:{task_index}:{result_index}",
                        )
                    )
        return CollectionResult(
            source=self.name,
            observations=observations,
            status="complete",
            quota={"site": scope.site_id},
        )
