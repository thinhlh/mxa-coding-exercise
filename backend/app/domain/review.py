"""Timesheet status transitions: draft -> submitted -> approved (terminal) / rejected -> submitted."""

from __future__ import annotations

EDITABLE_STATUSES = frozenset({"draft", "rejected"})


class IllegalTransitionError(Exception):
    """Raised when a status does not permit the requested transition."""


def submit(status: str) -> str:
    if status not in EDITABLE_STATUSES:
        raise IllegalTransitionError(f"a {status} timesheet cannot be submitted")
    return "submitted"


def approve(status: str) -> str:
    if status != "submitted":
        raise IllegalTransitionError(f"a {status} timesheet cannot be approved")
    return "approved"


def reject(status: str) -> str:
    if status != "submitted":
        raise IllegalTransitionError(f"a {status} timesheet cannot be rejected")
    return "rejected"
