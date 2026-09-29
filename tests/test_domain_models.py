from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError
from seo_engine.domain.models import CollectionResult, DateWindow, NormalizedObservation


def test_normalized_observation_accepts_search_metrics() -> None:
    observation = NormalizedObservation(
        source="gsc",
        observed_at=datetime.now(UTC),
        dimensions={"query": "seo strategy", "page": "https://example.com/page"},
        metrics={"clicks": 10, "impressions": 100, "ctr": 0.1, "position": 9.5},
        evidence_ref="gsc:1",
    )
    assert observation.metrics["ctr"] == 0.1


def test_invalid_ctr_and_position_are_rejected() -> None:
    with pytest.raises(ValidationError):
        NormalizedObservation(
            source="gsc",
            observed_at=datetime.now(UTC),
            dimensions={},
            metrics={"ctr": 1.5, "position": -1},
            evidence_ref="gsc:bad",
        )


def test_partial_collection_requires_error() -> None:
    with pytest.raises(ValidationError):
        CollectionResult(source="gsc", observations=[], status="partial", errors=[], quota={})


def test_date_window_requires_ordered_dates() -> None:
    with pytest.raises(ValidationError):
        DateWindow(start=date(2026, 9, 30), end=date(2026, 9, 1))
