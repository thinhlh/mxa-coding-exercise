"""HTTP routes for reading and writing timesheets; business logic lives in `app.services.timesheets`."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import CurrentEmployee, current_employee, require_employee
from app.db import get_session
from app.schemas.timesheet import TimesheetResponse, TimesheetWriteRequest
from app.services import timesheets as timesheets_service

router = APIRouter(prefix="/api/timesheets", tags=["timesheets"])


@router.get("", response_model=TimesheetResponse)
def get_current_week(
    at: int | None = Query(default=None),
    current: CurrentEmployee = Depends(require_employee),
    session: Session = Depends(get_session),
) -> dict:
    return timesheets_service.get_timesheet_for_week(session, current, at)


@router.get("/{timesheet_status}", response_model=list[TimesheetResponse])
def list_by_status(
    timesheet_status: str,
    current: CurrentEmployee = Depends(current_employee),
    session: Session = Depends(get_session),
) -> list[dict]:
    return timesheets_service.list_timesheets(session, current, timesheet_status)


@router.post("/{timesheet_status}", response_model=TimesheetResponse)
def write_by_status(
    timesheet_status: str,
    body: TimesheetWriteRequest,
    current: CurrentEmployee = Depends(current_employee),
    session: Session = Depends(get_session),
) -> dict:
    return timesheets_service.write_timesheet(session, current, timesheet_status, body)
