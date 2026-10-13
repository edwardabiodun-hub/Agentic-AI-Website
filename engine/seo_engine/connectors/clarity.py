from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class ClarityConnector:
    name = "clarity"

    def __init__(
        self,
        payload: list[dict[str, Any]] | None = None,
        *,
        project_id: str = "",
        api_token: str = "",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.payload = payload
        self.project_id = project_id
        self.api_token = api_token
        self.client = client

    async def export(
        self, num_of_days: int, dimensions: list[str] | None = None
    ) -> CollectionResult:
        if num_of_days not in (1, 2, 3):
            return CollectionResult(
                source=self.name,
                status="failed",
                errors=["Clarity export supports a maximum of 3 days"],
            )
        if self.payload is None:
            if not self.api_token:
                return CollectionResult(
                    source=self.name,
                    observations=[],
                    status="failed",
                    errors=["CLARITY_API_TOKEN is not configured"],
                )
            params = {"numOfDays": str(num_of_days)}
            for index, dimension in enumerate(dimensions or []):
                params[f"dimension{index + 1}"] = dimension
            close_client = self.client is None
            client = self.client or httpx.AsyncClient(timeout=30)
            try:
                response = await client.get(
                    "https://www.clarity.ms/export-data/api/v1/project-live-insights",
                    params=params,
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                payload = response.json()
            finally:
                if close_client:
                    await client.aclose()
        else:
            payload = self.payload

        observations = []
        for metric in payload:
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
        requested_days = days
        export_days = min(days, 3)
        result = await self.export(export_days, ["URL"])
        if requested_days > 3 and result.status == "complete":
            return result.model_copy(
                update={
                    "status": "partial",
                    "errors":[
                        "Clarity Data Export API supports only 1-3 trailing days; "
                        f"collected the latest {export_days} days"
                    ],
                    "quota": {**result.quota, "requested_days": requested_days},
                }
            )
        return result
