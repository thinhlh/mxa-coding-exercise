"""week_start_for resolves any timestamp to that week's Monday."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.domain.week import DAYS, WEEKDAYS, week_start_for


def test_days_are_monday_first():
    assert DAYS == ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    assert WEEKDAYS == ("monday", "tuesday", "wednesday", "thursday", "friday")


def test_mid_week_resolves_to_its_monday():
    # Wednesday 2026-09-16
    ts = int(datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc).timestamp())
    assert week_start_for(ts) == date(2026, 9, 14)


def test_sunday_resolves_to_the_prior_monday():
    ts = int(datetime(2026, 9, 20, 23, 59, tzinfo=timezone.utc).timestamp())
    assert week_start_for(ts) == date(2026, 9, 14)


def test_resolves_across_a_week_boundary():
    monday = int(datetime(2026, 9, 21, 0, 0, tzinfo=timezone.utc).timestamp())
    sunday_before = int(datetime(2026, 9, 20, 23, 59, 59, tzinfo=timezone.utc).timestamp())
    assert week_start_for(sunday_before) == date(2026, 9, 14)
    assert week_start_for(monday) == date(2026, 9, 21)


def test_resolves_across_a_year_boundary():
    # 2025-12-31 is a Wednesday, week starts Monday 2025-12-29.
    # 2026-01-01 is a Thursday, still in that same week.
    dec31 = int(datetime(2025, 12, 31, 6, 0, tzinfo=timezone.utc).timestamp())
    jan1 = int(datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc).timestamp())
    assert week_start_for(dec31) == date(2025, 12, 29)
    assert week_start_for(jan1) == date(2025, 12, 29)
