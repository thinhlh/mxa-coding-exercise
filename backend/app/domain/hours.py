"""Line item hours and the daily total they sum to."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .week import DAYS


@dataclass(frozen=True)
class LineItemHours:
    monday: Decimal = Decimal(0)
    tuesday: Decimal = Decimal(0)
    wednesday: Decimal = Decimal(0)
    thursday: Decimal = Decimal(0)
    friday: Decimal = Decimal(0)
    saturday: Decimal = Decimal(0)
    sunday: Decimal = Decimal(0)

    def __getitem__(self, day: str) -> Decimal:
        return getattr(self, day)


def daily_totals(line_items: list[LineItemHours]) -> dict[str, Decimal]:
    """Sum every line item's hours entry for each day of the week."""
    return {day: sum((item[day] for item in line_items), Decimal(0)) for day in DAYS}
