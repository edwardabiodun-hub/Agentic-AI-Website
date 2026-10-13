from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class GA4Connector:
    name = "ga4"

    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        property_id: str = "",
        credentials: Any | None = None,
        client: Any | None = None,
    ) -> None:
        self.payload = payload
        self.property_id = property_id
        self.credentials = credentials
        self.client = client

    def _live_client(self) -> Any:
        if self.client is not None:
            return self.client
        if self.credentials is None:
            raise RuntimeError(
                "GA4 credentials are not configured; set GA4_PROPERTY_ID and Google credentials"
            )
        from google.analytics.data_v1beta import BetaAnalyticsDataClient

        self.client = BetaAnalyticsDataClient(credentials=self.credentials)
        return self.client

    def _run_live_report(self, window: DateWindow) -> list[Any]:
        if not self.property_id:
            raise RuntimeError("GA4_PROPERTY_ID is not configured")
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[
                DateRange(start_date=window.start.isoformat(), end_date=window.end.isoformat())
            ],
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="sessions"),
                Metric(name="engagementRate"),
                Metric(name="conversions"),
            ],
            limit=100_000,
        )
        return list(self._live_client().run_report(request=request).rows)

    async def run_report(self, window: DateWindow, offset: int = 0) -> list[NormalizedObservation]:
        if self.payload is None:
            rows = await asyncio.to_thread(self._run_live_report, window)
            observations = []
            for index, row in enumerate(rows, start=offset):
                values = [item.value for item in row.metric_values]
                observations.append(
                    NormalizedObservation(
                        source=self.name,
                        observed_at=datetime.now(UTC),
                        dimensions={"page": row.dimension_values[0].value},
                        metrics={
                            "views": float(values[0]) if len(values) > 0 else None,
                            "sessions": float(values[1]) if len(values) > 1 else None,
                            "engagement_rate": float(values[2]) if len(values) > 2 else None,
                            "conversions": float(values[3]) if len(values) > 3 else None,
                        },
                        evidence_ref=f"ga4:{window.start}:{window.end}:{index}",
                    )
                )
            return observations

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
            quota={"property": self.property_id or scope.site_id},
        )
