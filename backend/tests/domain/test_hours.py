"""daily_totals sums every line item's hours entry for each day."""

from __future__ import annotations

from decimal import Decimal

from app.domain.hours import LineItemHours, daily_totals


def test_sums_multiple_line_items_per_day():
    totals = daily_totals([LineItemHours(monday=Decimal(20)), LineItemHours(monday=Decimal(5))])
    assert totals["monday"] == Decimal(25)


def test_an_untouched_day_totals_zero():
    totals = daily_totals([LineItemHours()])
    assert totals["monday"] == Decimal(0)
    assert totals["sunday"] == Decimal(0)


def test_decimal_split_hours_sum_exactly():
    totals = daily_totals(
        [LineItemHours(monday=Decimal("7.5")), LineItemHours(monday=Decimal("0.5"))]
    )
    assert totals["monday"] == Decimal(8)
