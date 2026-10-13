from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class GSCConnector:
    name = "gsc"

    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        property_name: str = "",
        credentials: Any | None = None,
        service: Any | None = None,
    ) -> None:
        self.payload = payload
        self.property_name = property_name
        self.credentials = credentials
        self.service = service

    def _live_service(self) -> Any:
        if self.service is not None:
            return self.service
        if self.credentials is None:
            raise RuntimeError(
                "GSC credentials are not configured; set GSC_PROPERTY and Google credentials"
            )
        from googleapiclient.discovery import build

        self.service = build(
            "searchconsole", "v1", credentials=self.credentials, cache_discovery=False
        )
        return self.service

    def _query_live(self, dimensions: list[str], window: DateWindow) -> list[dict[str, Any]]:
        if not self.property_name:
            raise RuntimeError("GSC_PROPERTY is not configured")
        service = self._live_service()
        rows: list[dict[str, Any]] = []
        start_row = 0
        while True:
            response = (
                service.searchanalytics()
                .query(
                    siteUrl=self.property_name,
                    body={
                        "startDate": window.start.isoformat(),
                        "endDate": window.end.isoformat(),
                        "dimensions": dimensions,
                        "rowLimit": 25_000,
                        "startRow": start_row,
                    },
                )
                .execute()
            )
            batch = response.get("rows", [])
            rows.extend(batch)
            if len(batch) < 25_000:
                return rows
            start_row += len(batch)

    async def query(
        self, dimensions: list[str], window: DateWindow, start_row: int = 0
    ) -> list[NormalizedObservation]:
        if self.payload is None:
            rows = await asyncio.to_thread(self._query_live, dimensions, window)
        else:
            rows = self.payload.get("rows", [])[start_row:]
        observations = []
        for index, row in enumerate(rows, start=start_row):
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
            quota={"site": self.property_name or scope.site_id},
        )
