from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class GSCConnector:
    name = "gsc"

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {"rows": []}

    async def query(
        self, dimensions: list[str], window: DateWindow, start_row: int = 0
    ) -> list[NormalizedObservation]:
        observations = []
        for index, row in enumerate(self.payload.get("rows", [])[start_row:], start=start_row):
            observations.append(
                NormalizedObservation(
                    source=self.name,
                    observed_at=datetime.now(UTC),
                    dimensions=dict(zip(dimensions, row.get("keys", []), strict=False)),
                    metrics={
                        key: row.get(key) for key in ("clicks", "impressions", "ctr", "position")
                    },
                    evidence_ref=f"gsc:{window.start}:{window.end}:{index}",
                )
            )
        return observations

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        observations = await self.query(["query", "page"], window)
        return CollectionResult(
            source=self.name,
            observations=observations,
            status="complete",
            quota={"site": scope.site_id},
        )
