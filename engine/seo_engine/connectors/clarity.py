from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class ClarityConnector:
    name = "clarity"

    def __init__(self, payload: list[dict[str, Any]] | None = None) -> None:
        self.payload = payload or []

    async def export(
        self, num_of_days: int, dimensions: list[str] | None = None
    ) -> CollectionResult:
        if num_of_days not in (1, 2, 3):
            return CollectionResult(
                source=self.name,
                status="failed",
                errors=["Clarity export supports a maximum of 3 days"],
            )
        observations = []
        for metric in self.payload:
            metric_name = metric.get("metricName", "").lower().replace(" ", "_")
            for index, row in enumerate(metric.get("information", [])):
                value = row.get("count", row.get("value", 0))
                observations.append(
                    NormalizedObservation(
                        source=self.name,
                        observed_at=datetime.now(UTC),
                        dimensions={"url": row.get("URL", "")},
                        metrics={metric_name: float(value)},
                        evidence_ref=f"clarity:{num_of_days}:{index}",
                    )
                )
        return CollectionResult(
            source=self.name,
            observations=observations,
            status="complete",
            quota={"days": num_of_days},
        )

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        days = (window.end - window.start).days + 1
        return await self.export(days, ["URL"])
