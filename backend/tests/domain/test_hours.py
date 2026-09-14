"""daily_totals sums every line item's hours entry for each day."""

from __future__ import annotations

from app.domain.hours import LineItemHours, daily_totals


def test_sums_multiple_line_items_per_day():
    totals = daily_totals([LineItemHours(monday=20), LineItemHours(monday=5)])
    assert totals["monday"] == 25


def test_an_untouched_day_totals_zero():
    totals = daily_totals([LineItemHours()])
    assert totals["monday"] == 0
    assert totals["sunday"] == 0


def test_multiple_line_items_sum_to_exactly_eight():
    totals = daily_totals([LineItemHours(monday=5), LineItemHours(monday=3)])
    assert totals["monday"] == 8
