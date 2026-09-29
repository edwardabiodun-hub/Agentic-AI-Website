from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class MeasurementWindow:
    start: datetime
    end: datetime
    days: int


@dataclass
class LiftSummary:
    absolute: dict[str, float]
    percent: dict[str, float | None]


def create_measurement_windows(deployed_at: datetime) -> list[MeasurementWindow]:
    return [
        MeasurementWindow(start=deployed_at, end=deployed_at + timedelta(days=days), days=days)
        for days in (30, 60, 90)
    ]


def calculate_lift(baseline: dict[str, float], outcome: dict[str, float]) -> LiftSummary:
    absolute = {
        key: outcome.get(key, 0) - baseline.get(key, 0) for key in set(baseline) | set(outcome)
    }
    percent = {
        key: (absolute[key] / baseline[key] * 100 if baseline.get(key) else None)
        for key in absolute
    }
    return LiftSummary(absolute=absolute, percent=percent)


def rank_strategy_outcomes(outcomes: list[dict]) -> list[dict]:
    grouped: dict[str, list[float]] = {}
    for outcome in outcomes:
        grouped.setdefault(outcome["strategy_type"], []).append(outcome.get("lift", 0))
    return [
        {
            "strategy_type": strategy,
            "sample_count": len(values),
            "average_lift": sum(values) / len(values),
        }
        for strategy, values in grouped.items()
    ]
