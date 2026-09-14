"""Business logic for reading and writing timesheets, independent of HTTP concerns."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import CurrentEmployee
from app.domain.hours import LineItemHours, daily_totals, days_over_limit
from app.domain.review import EDITABLE_STATUSES, IllegalTransitionError, approve, reject, submit
from app.domain.week import DAYS, week_start_for
from app.models import Project, Timesheet, TimesheetLineItem
from app.schemas.timesheet import LineItemInput, TimesheetWriteRequest


class TimesheetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


_REVIEW_ACTIONS = {TimesheetStatus.APPROVED: approve, TimesheetStatus.REJECTED: reject}
_REVIEW_VERBS = {TimesheetStatus.APPROVED: "approve", TimesheetStatus.REJECTED: "reject"}


def _parse_status(raw_status: str) -> TimesheetStatus:
    try:
        return TimesheetStatus(raw_status)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no such timesheet status {raw_status}") from None


def _line_item_hours(line_item: TimesheetLineItem) -> LineItemHours:
    return LineItemHours(**{day: getattr(line_item, f"hours_{day}") for day in DAYS})


def _serialize(timesheet: Timesheet | None, *, employee_name: str, week_start) -> dict:
    line_items = timesheet.line_items if timesheet else []
    totals = daily_totals([_line_item_hours(item) for item in line_items])

    return {
        "id": timesheet.id if timesheet else None,
        "week_start": timesheet.week_start if timesheet else week_start,
        "status": timesheet.status if timesheet else TimesheetStatus.DRAFT,
        "employee_name": employee_name,
        "line_items": [
            {
                "project_code": item.project.code,
                "project_name": item.project.name,
                "hours": {day: getattr(item, f"hours_{day}") for day in DAYS},
            }
            for item in line_items
        ],
        "daily_totals": totals,
        "total_hours": sum(totals.values()),
        "submit_message": timesheet.submit_message if timesheet else None,
        "review_message": timesheet.review_message if timesheet else None,
        "submitted_at": timesheet.submitted_at if timesheet else None,
        "reviewed_at": timesheet.reviewed_at if timesheet else None,
    }


def get_timesheet_for_week(session: Session, current: CurrentEmployee, at: int | None) -> dict:
    epoch_seconds = at if at is not None else int(datetime.now(timezone.utc).timestamp())
    week_start = week_start_for(epoch_seconds)

    timesheet = (
        session.query(Timesheet)
        .filter(Timesheet.employee_id == current.id, Timesheet.week_start == week_start)
        .one_or_none()
    )
    return _serialize(timesheet, employee_name=current.display_name, week_start=week_start)


def list_timesheets(
    session: Session, current: CurrentEmployee, timesheet_status: str, project_id: uuid.UUID | None = None
) -> list[dict]:
    target = _parse_status(timesheet_status)

    query = session.query(Timesheet).filter(Timesheet.status == target.value)
    if current.role == "employee":
        query = query.filter(Timesheet.employee_id == current.id)
    if project_id is not None:
        query = query.join(Timesheet.line_items).filter(TimesheetLineItem.project_id == project_id).distinct()

    timesheets = query.order_by(Timesheet.week_start.desc()).all()
    return [
        _serialize(timesheet, employee_name=timesheet.employee.display_name, week_start=timesheet.week_start)
        for timesheet in timesheets
    ]


def _resolve_line_items(session: Session, inputs: list[LineItemInput]) -> list[TimesheetLineItem]:
    seen_codes: set[str] = set()
    resolved: list[TimesheetLineItem] = []

    for item in inputs:
        code = item.project_code.upper()
        if code in seen_codes:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"project code {code.lower()} is listed twice")
        seen_codes.add(code)

        hours = item.hours.model_dump()
        if any(value < 0 for value in hours.values()):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "hours cannot be negative")

        project = session.query(Project).filter(Project.code == code).one_or_none()
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"no project has code {code.lower()}")

        resolved.append(TimesheetLineItem(project_id=project.id, **{f"hours_{day}": hours[day] for day in DAYS}))

    return resolved


def _check_daily_cap(inputs: list[LineItemInput]) -> None:
    hours = [LineItemHours(**item.hours.model_dump()) for item in inputs]
    over_limit = days_over_limit(daily_totals(hours))
    if over_limit:
        day, total = next(iter(over_limit.items()))
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{day} totals {total} hours; a day cannot exceed 24")


def _apply_line_items(session: Session, timesheet: Timesheet, line_items: list[TimesheetLineItem]) -> None:
    timesheet.line_items.clear()
    # A single flush emits every insert before every delete, so the old rows must go
    # first: otherwise re-saving a week that already lists a project code collides with
    # the (timesheet_id, project_id) unique constraint.
    session.flush()
    timesheet.line_items.extend(line_items)


def _write_editable(
    session: Session, current: CurrentEmployee, target_status: TimesheetStatus, body: TimesheetWriteRequest
) -> Timesheet:
    if current.role != "employee":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "only an employee can perform this action")
    if body.at is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "saving a timesheet needs at")
    if body.line_items is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "saving a timesheet needs lineItems")
    if target_status == TimesheetStatus.SUBMITTED and not body.line_items:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "a timesheet needs at least one line item before it can be submitted",
        )

    resolved = _resolve_line_items(session, body.line_items)
    _check_daily_cap(body.line_items)

    week_start = week_start_for(body.at)
    timesheet = (
        session.query(Timesheet)
        .filter(Timesheet.employee_id == current.id, Timesheet.week_start == week_start)
        .one_or_none()
    )
    if timesheet is None:
        timesheet = Timesheet(employee_id=current.id, week_start=week_start, status=TimesheetStatus.DRAFT.value)
        session.add(timesheet)
    elif timesheet.status not in EDITABLE_STATUSES:
        raise HTTPException(status.HTTP_409_CONFLICT, f"a {timesheet.status} timesheet cannot be edited")

    _apply_line_items(session, timesheet, resolved)

    if target_status == TimesheetStatus.SUBMITTED:
        timesheet.status = submit(timesheet.status)
        timesheet.submitted_at = datetime.now(timezone.utc)
        timesheet.submit_message = body.message
    else:
        timesheet.status = TimesheetStatus.DRAFT.value

    session.commit()
    return timesheet


def _write_review(
    session: Session, current: CurrentEmployee, target_status: TimesheetStatus, body: TimesheetWriteRequest
) -> Timesheet:
    if current.role != "manager":
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"only a manager can {_REVIEW_VERBS[target_status]} a timesheet")
    if body.timesheet_id is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"{_REVIEW_VERBS[target_status]}ing a timesheet needs a timesheetId"
        )

    timesheet = session.get(Timesheet, body.timesheet_id)
    if timesheet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no timesheet with that id")

    try:
        timesheet.status = _REVIEW_ACTIONS[target_status](timesheet.status)
    except IllegalTransitionError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"only a submitted timesheet can be {_REVIEW_VERBS[target_status]}d"
        ) from None

    timesheet.review_message = body.message
    timesheet.reviewed_at = datetime.now(timezone.utc)
    timesheet.reviewed_by = current.id

    session.commit()
    return timesheet


def write_timesheet(session: Session, current: CurrentEmployee, target_status: str, body: TimesheetWriteRequest) -> dict:
    target = _parse_status(target_status)

    handler = _write_review if target in _REVIEW_ACTIONS else _write_editable
    timesheet = handler(session, current, target, body)

    return _serialize(timesheet, employee_name=timesheet.employee.display_name, week_start=timesheet.week_start)
