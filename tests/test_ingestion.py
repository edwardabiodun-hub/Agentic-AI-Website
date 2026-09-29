from datetime import UTC, date, datetime

import pytest
from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation, SiteScope
from seo_engine.persistence.db import create_test_session
from seo_engine.persistence.repositories import ObservationRepository, RunRepository
from seo_engine.workflow import collect_all


class FakeConnector:
    def __init__(self, name: str, status: str = "complete") -> None:
        self.name = name
        self.status = status

    async def collect(self, window: DateWindow, scope: SiteScope) -> CollectionResult:
        if self.status == "partial":
            return CollectionResult(source=self.name, status="partial", errors=["quota"])
        return CollectionResult(
            source=self.name,
            status="complete",
            observations=[
                NormalizedObservation(
                    source=self.name,
                    observed_at=datetime.now(UTC),
                    dimensions={"page": "https://example.com"},
                    metrics={"clicks": 1},
                    evidence_ref=f"{self.name}:1",
                )
            ],
        )


@pytest.mark.asyncio
async def test_collect_all_persists_partial_status_without_zero_metrics() -> None:
    async with create_test_session() as session:
        summary = await collect_all(
            [FakeConnector("gsc"), FakeConnector("clarity", "partial")],
            DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
            SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
            RunRepository(session),
            ObservationRepository(session),
        )
        assert summary.status == "partial"
        assert any("quota" in error for error in summary.errors)


@pytest.mark.asyncio
async def test_collect_all_is_idempotent_for_same_window() -> None:
    async with create_test_session() as session:
        args = (
            [FakeConnector("gsc")],
            DateWindow(start=date(2026, 9, 1), end=date(2026, 9, 7)),
            SiteScope(site_id="demo", site_url="https://example.com", target_root="site"),
            RunRepository(session),
            ObservationRepository(session),
        )
        first = await collect_all(*args)
        second = await collect_all(*args)
        assert first.run_id == second.run_id
