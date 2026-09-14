"""Week vocabulary: day ordering and resolving a timestamp to its Monday."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
WEEKDAYS = DAYS[:5]


def week_start_for(epoch_seconds: int) -> date:
    """Resolve seconds since epoch, in UTC, to the Monday of that week (ADR 0002)."""
    day = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).date()
    return day - timedelta(days=day.weekday())
