"""Request and response DTOs for the timesheets API."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from pydantic import field_validator

from app.domain.week import week_start_for
from app.schemas.base import CamelModel


class HoursInput(CamelModel):
    monday: int = 0
    tuesday: int = 0
    wednesday: int = 0
    thursday: int = 0
    friday: int = 0
    saturday: int = 0
    sunday: int = 0


class LineItemInput(CamelModel):
    project_code: str
    hours: HoursInput


class TimesheetWriteRequest(CamelModel):
    at: int | None = None
    line_items: list[LineItemInput] | None = None
    timesheet_id: uuid.UUID | None = None
    message: str | None = None

    @field_validator("at")
    @classmethod
    def _at_is_not_in_a_future_week(cls, value: int | None) -> int | None:
        """There is no next week's timesheet to save into — the current week is the latest."""
        if value is None:
            return value
        current_week = week_start_for(int(datetime.now(timezone.utc).timestamp()))
        if week_start_for(value) > current_week:
            raise ValueError("a timesheet cannot be saved for a week after the current week")
        return value


class LineItemResponse(CamelModel):
    project_code: str
    project_name: str
    hours: dict[str, int]


class TimesheetResponse(CamelModel):
    id: uuid.UUID | None
    week_start: date
    status: str
    employee_name: str
    line_items: list[LineItemResponse]
    daily_totals: dict[str, int]
    total_hours: int
    submit_message: str | None
    review_message: str | None
    submitted_at: datetime | None
    reviewed_at: datetime | None
