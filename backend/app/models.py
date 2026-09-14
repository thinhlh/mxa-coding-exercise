"""SQLAlchemy 2.0 typed models for employees, projects, timesheets and their line items."""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    manager_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    manager: Mapped[Employee] = relationship(foreign_keys=[manager_id])


class Timesheet(Base):
    __tablename__ = "timesheets"
    __table_args__ = (UniqueConstraint("employee_id", "week_start"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    submit_message: Mapped[str | None] = mapped_column(String, nullable=True)
    review_message: Mapped[str | None] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )


class TimesheetLineItem(Base):
    __tablename__ = "timesheet_line_items"
    __table_args__ = (UniqueConstraint("timesheet_id", "project_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timesheet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("timesheets.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    hours_monday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_tuesday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_wednesday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_thursday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_friday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_saturday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hours_sunday: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
