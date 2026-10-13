from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope


class DataForSEOConnector:
    name = "dataforseo"

    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        login: str = "",
        password: str = "",
        keywords: list[str] | None = None,
        location_code: int = 2840,
        language_code: str = "en",
        device: str = "desktop",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.payload = payload
        self.login = login
        self.password = password
        self.keywords = keywords or []
        self.location_code = location_code
        self.language_code = language_code
        self.device = device
        self.client = client

    async def track_keywords(
        self, keywords: list[str], location_code: int, language_code: str
    ) -> CollectionResult:
        if self.payload is None:
            return await self._collect_live(keywords, location_code, language_code)
        return await self.collect(
            DateWindow(start=datetime.now(UTC).date(), end=datetime.now(UTC).date()),
            SiteScope(site_id="keywords", site_url="https://example.com", target_root="site"),
        )

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        if self.payload is None:
            return await self._collect_live(self.keywords, self.location_code, self.language_code)

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

    async def _collect_live(
        self, keywords: list[str], location_code: int, language_code: str
    ) -> CollectionResult:
        if not self.login or not self.password:
            return CollectionResult(
                source=self.name,
                observations=[],
                status="failed",
                errors=["DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are not configured"],
            )
        if not keywords:
            return CollectionResult(
                source=self.name,
                observations=[],
                status="failed",
                errors=["SEO_KEYWORDS is empty; refusing to spend on an unbounded SERP crawl"],
            )

        close_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=90)
        try:
            response = await client.post(
                "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
                auth=(self.login, self.password),
                json=[
                    {
                        "keyword": keyword,
                        "location_code": location_code,
                        "language_code": language_code,
                        "device": self.device,
                        "depth": 100,
                    }
                    for keyword in keywords[:100]
                ],
            )
            response.raise_for_status()
            body = response.json()
            if body.get("status_code") != 20000:
                raise RuntimeError(body.get("status_message", "DataForSEO returned an error"))
            observations = self._normalize_tasks(body.get("tasks", []))
            return CollectionResult(
                source=self.name,
                observations=observations,
                status="complete",
                quota={
                    "keywords_requested": min(len(keywords), 100),
                    "cost": body.get("cost"),
                },
            )
        finally:
            if close_client:
                await client.aclose()

    def _normalize_tasks(self, tasks: list[dict[str, Any]]) -> list[NormalizedObservation]:
        observations = []
        for task_index, task in enumerate(tasks):
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
                                "rank": item.get("rank_absolute"),
                                "search_volume": result.get("search_volume"),
                            },
                            evidence_ref=f"dataforseo:{task_index}:{result_index}",
                        )
                    )
        return observations
