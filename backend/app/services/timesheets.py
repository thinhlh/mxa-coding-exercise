"""Business logic for reading and writing timesheets, independent of HTTP concerns."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import CurrentEmployee
from app.domain.hours import LineItemHours, daily_totals, days_over_limit
from app.domain.review import IllegalTransitionError, approve, reject, submit
from app.domain.week import DAYS, week_start_for
from app.models import Project, Timesheet, TimesheetLineItem
from app.schemas.timesheet import LineItemInput, TimesheetWriteRequest

_REVIEW_ACTIONS = {"approved": approve, "rejected": reject}
_REVIEW_VERBS = {"approved": "approve", "rejected": "reject"}


def _line_item_hours(line_item: TimesheetLineItem) -> LineItemHours:
    return LineItemHours(**{day: getattr(line_item, f"hours_{day}") for day in DAYS})


def _serialize(timesheet: Timesheet | None, *, employee_name: str, week_start) -> dict:
    if timesheet is None:
        totals = daily_totals([])
        return {
            "id": None,
            "week_start": week_start,
            "status": "draft",
            "employee_name": employee_name,
            "line_items": [],
            "daily_totals": totals,
            "total_hours": 0,
            "submit_message": None,
            "review_message": None,
            "submitted_at": None,
            "reviewed_at": None,
        }

    totals = daily_totals([_line_item_hours(item) for item in timesheet.line_items])
    return {
        "id": timesheet.id,
        "week_start": timesheet.week_start,
        "status": timesheet.status,
        "employee_name": employee_name,
        "line_items": [
            {
                "project_code": item.project.code,
                "project_name": item.project.name,
                "hours": {day: getattr(item, f"hours_{day}") for day in DAYS},
            }
            for item in timesheet.line_items
        ],
        "daily_totals": totals,
        "total_hours": sum(totals.values()),
        "submit_message": timesheet.submit_message,
        "review_message": timesheet.review_message,
        "submitted_at": timesheet.submitted_at,
        "reviewed_at": timesheet.reviewed_at,
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


def list_timesheets(session: Session, current: CurrentEmployee, timesheet_status: str) -> list[dict]:
    query = session.query(Timesheet).filter(Timesheet.status == timesheet_status)
    if current.role == "employee":
        query = query.filter(Timesheet.employee_id == current.id)

    timesheets = query.order_by(Timesheet.week_start.desc()).all()
    return [
        _serialize(timesheet, employee_name=timesheet.employee.display_name, week_start=timesheet.week_start)
        for timesheet in timesheets
    ]


def _resolve_line_items(session: Session, inputs: list[LineItemInput]) -> list[tuple[Project, LineItemInput]]:
    seen_codes: set[str] = set()
    resolved: list[tuple[Project, LineItemInput]] = []

    for item in inputs:
        code = item.project_code.upper()
        if code in seen_codes:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"project code {code.lower()} is listed twice")
        seen_codes.add(code)

        for day in DAYS:
            if getattr(item.hours, day) < 0:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "hours cannot be negative")

        project = session.query(Project).filter(Project.code == code).one_or_none()
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"no project has code {code.lower()}")

        resolved.append((project, item))

    return resolved


def _check_daily_cap(inputs: list[LineItemInput]) -> None:
    hours = [LineItemHours(**item.hours.model_dump()) for item in inputs]
    over_limit = days_over_limit(daily_totals(hours))
    if over_limit:
        day, total = next(iter(over_limit.items()))
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{day} totals {total} hours; a day cannot exceed 24")


def _apply_line_items(session: Session, timesheet: Timesheet, resolved: list[tuple[Project, LineItemInput]]) -> None:
    timesheet.line_items.clear()
    # A single flush emits every insert before every delete, so the old rows must go
    # first: otherwise re-saving a week that already lists a project code collides with
    # the (timesheet_id, project_id) unique constraint.
    session.flush()

    for project, item in resolved:
        timesheet.line_items.append(
            TimesheetLineItem(
                project_id=project.id,
                **{f"hours_{day}": getattr(item.hours, day) for day in DAYS},
            )
        )


def _write_editable(
    session: Session, current: CurrentEmployee, target_status: str, body: TimesheetWriteRequest
) -> Timesheet:
    if current.role != "employee":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "only an employee can perform this action")
    if body.at is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "saving a timesheet needs at")
    if body.line_items is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "saving a timesheet needs lineItems")
    if target_status == "submitted" and not body.line_items:
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
        timesheet = Timesheet(employee_id=current.id, week_start=week_start, status="draft")
        session.add(timesheet)
    elif timesheet.status not in ("draft", "rejected"):
        raise HTTPException(status.HTTP_409_CONFLICT, f"a {timesheet.status} timesheet cannot be edited")

    _apply_line_items(session, timesheet, resolved)

    if target_status == "submitted":
        timesheet.status = submit(timesheet.status)
        timesheet.submitted_at = datetime.now(timezone.utc)
        timesheet.submit_message = body.message
    else:
        timesheet.status = "draft"

    session.commit()
    return timesheet


def _write_review(
    session: Session, current: CurrentEmployee, target_status: str, body: TimesheetWriteRequest
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
    if target_status in ("draft", "submitted"):
        timesheet = _write_editable(session, current, target_status, body)
    elif target_status in _REVIEW_ACTIONS:
        timesheet = _write_review(session, current, target_status, body)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no such timesheet status {target_status}")

    return _serialize(timesheet, employee_name=timesheet.employee.display_name, week_start=timesheet.week_start)
