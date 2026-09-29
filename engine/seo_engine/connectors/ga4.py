from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class GA4Connector:
    name = "ga4"

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        self.payload = payload or {"rows": []}

    async def run_report(self, window: DateWindow, offset: int = 0) -> list[NormalizedObservation]:
        observations = []
        for index, row in enumerate(self.payload.get("rows", [])[offset:], start=offset):
            values = [item.get("value") for item in row.get("metricValues", [])]
            metrics = {
                "views": float(values[0]) if len(values) > 0 else None,
                "sessions": float(values[1]) if len(values) > 1 else None,
                "engagement_rate": float(values[2]) if len(values) > 2 else None,
            }
            observations.append(
                NormalizedObservation(
                    source=self.name,
                    observed_at=datetime.now(UTC),
                    dimensions={"page": row.get("dimensionValues", [{}])[0].get("value", "")},
                    metrics=metrics,
                    evidence_ref=f"ga4:{window.start}:{window.end}:{index}",
                )
            )
        return observations

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        return CollectionResult(
            source=self.name,
            observations=await self.run_report(window),
            status="complete",
            quota={"property": scope.site_id},
        )
