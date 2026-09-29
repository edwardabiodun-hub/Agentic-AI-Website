from datetime import UTC, datetime

from seo_engine.measurement import calculate_lift, create_measurement_windows


def test_measurement_windows_are_30_60_90_days() -> None:
    deployed = datetime(2026, 9, 29, tzinfo=UTC)
    windows = create_measurement_windows(deployed)
    assert [window.days for window in windows] == [30, 60, 90]
    assert windows[0].end > windows[0].start


def test_calculate_lift_handles_zero_baseline() -> None:
    lift = calculate_lift({"clicks": 0, "conversions": 0}, {"clicks": 10, "conversions": 2})
    assert lift.absolute["clicks"] == 10
    assert lift.percent["clicks"] is None
