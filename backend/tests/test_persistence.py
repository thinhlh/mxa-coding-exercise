"""Writes and reads back a timesheet with line items against a real database."""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Employee, Project, Timesheet, TimesheetLineItem


@pytest.fixture
def session() -> Session:
    """Runs against the database migrated by `alembic upgrade head`; clears written rows after each test."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        for model in (TimesheetLineItem, Timesheet, Project, Employee):
            session.execute(delete(model))
        session.commit()
        session.close()


def test_write_and_read_back_timesheet_with_line_items(session: Session) -> None:
    employee = Employee(id=uuid.uuid4(), email="alice@example.com", display_name="Alice Dupont")
    manager = Employee(id=uuid.uuid4(), email="mo@example.com", display_name="Mo Manager")
    session.add_all([employee, manager])

    project_a = Project(
        code="K7M2QX",
        name="Northwind migration",
        manager_id=manager.id,
        description="Migrate Northwind to the new platform",
        start_date=date(2026, 1, 5),
        created_at=datetime.now(timezone.utc),
    )
    project_b = Project(
        code="P9X4LM",
        name="Contoso audit",
        manager_id=manager.id,
        description="Annual audit",
        start_date=date(2026, 2, 2),
        created_at=datetime.now(timezone.utc),
    )
    session.add_all([project_a, project_b])
    session.flush()

    timesheet = Timesheet(employee_id=employee.id, week_start=date(2026, 9, 14), status="draft")
    session.add(timesheet)
    session.flush()

    line_item_a = TimesheetLineItem(
        timesheet_id=timesheet.id,
        project_id=project_a.id,
        hours_monday=Decimal("8"),
        hours_tuesday=Decimal("8"),
        hours_wednesday=Decimal("8"),
        hours_thursday=Decimal("8"),
        hours_friday=Decimal("4"),
    )
    line_item_b = TimesheetLineItem(
        timesheet_id=timesheet.id,
        project_id=project_b.id,
        hours_saturday=Decimal("2"),
    )
    session.add_all([line_item_a, line_item_b])
    session.commit()

    loaded = session.get(Timesheet, timesheet.id)
    assert loaded is not None
    assert loaded.employee_id == employee.id
    assert loaded.week_start == date(2026, 9, 14)
    assert loaded.status == "draft"

    loaded_line_items = (
        session.query(TimesheetLineItem).filter(TimesheetLineItem.timesheet_id == timesheet.id).all()
    )
    assert len(loaded_line_items) == 2

    by_project = {item.project_id: item for item in loaded_line_items}
    assert by_project[project_a.id].hours_friday == Decimal("4.00")
    assert by_project[project_b.id].hours_saturday == Decimal("2.00")
