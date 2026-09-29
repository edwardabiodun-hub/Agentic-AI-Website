from datetime import UTC, datetime

import pytest
from seo_engine.domain.models import NormalizedObservation
from seo_engine.persistence.db import create_test_session
from seo_engine.persistence.repositories import ObservationRepository, RunRepository


@pytest.mark.asyncio
async def test_run_and_observation_round_trip() -> None:
    async with create_test_session() as session:
        runs = RunRepository(session)
        observations = ObservationRepository(session)
        run_id = await runs.start("demo", "fingerprint-1")
        count = await observations.insert_many(
            run_id,
            [
                NormalizedObservation(
                    source="gsc",
                    observed_at=datetime.now(UTC),
                    dimensions={"page": "https://example.com"},
                    metrics={"clicks": 1},
                    evidence_ref="gsc:1",
                )
            ],
        )
        await runs.finish(run_id, "complete", [])

        assert count == 1
        assert await runs.has_fingerprint("demo", "fingerprint-1")


@pytest.mark.asyncio
async def test_duplicate_fingerprint_is_reused() -> None:
    async with create_test_session() as session:
        runs = RunRepository(session)
        first = await runs.start("demo", "same")
        second = await runs.start("demo", "same")
        assert first == second
