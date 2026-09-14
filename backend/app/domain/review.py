"""Timesheet status transitions: draft -> submitted -> approved (terminal) / rejected -> submitted."""

from __future__ import annotations

from enum import Enum


class TimesheetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


EDITABLE_STATUSES = frozenset({TimesheetStatus.DRAFT, TimesheetStatus.REJECTED})


class IllegalTransitionError(Exception):
    """Raised when a status does not permit the requested transition."""


def submit(status: TimesheetStatus) -> TimesheetStatus:
    if status not in EDITABLE_STATUSES:
        raise IllegalTransitionError(f"a {status} timesheet cannot be submitted")
    return TimesheetStatus.SUBMITTED


def approve(status: TimesheetStatus) -> TimesheetStatus:
    if status != TimesheetStatus.SUBMITTED:
        raise IllegalTransitionError(f"a {status} timesheet cannot be approved")
    return TimesheetStatus.APPROVED


def reject(status: TimesheetStatus) -> TimesheetStatus:
    if status != TimesheetStatus.SUBMITTED:
        raise IllegalTransitionError(f"a {status} timesheet cannot be rejected")
    return TimesheetStatus.REJECTED
