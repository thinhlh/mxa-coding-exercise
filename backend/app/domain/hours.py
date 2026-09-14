"""Line item hours and the daily total they sum to."""

from __future__ import annotations

from dataclasses import dataclass

from .week import DAYS


@dataclass(frozen=True)
class LineItemHours:
    monday: int = 0
    tuesday: int = 0
    wednesday: int = 0
    thursday: int = 0
    friday: int = 0
    saturday: int = 0
    sunday: int = 0

    def __getitem__(self, day: str) -> int:
        return getattr(self, day)


def daily_totals(line_items: list[LineItemHours]) -> dict[str, int]:
    """Sum every line item's hours entry for each day of the week."""
    return {day: sum((item[day] for item in line_items), 0) for day in DAYS}
