"""Every legal and illegal status transition."""

from __future__ import annotations

import pytest

from app.domain.review import EDITABLE_STATUSES, IllegalTransitionError, approve, reject, submit


def test_editable_statuses_are_draft_and_rejected():
    assert EDITABLE_STATUSES == frozenset({"draft", "rejected"})


def test_draft_submits_to_submitted():
    assert submit("draft") == "submitted"


def test_rejected_submits_to_submitted():
    assert submit("rejected") == "submitted"


@pytest.mark.parametrize("status", ["submitted", "approved"])
def test_submit_is_illegal_from_non_editable_statuses(status):
    with pytest.raises(IllegalTransitionError):
        submit(status)


def test_submitted_approves_to_approved():
    assert approve("submitted") == "approved"


@pytest.mark.parametrize("status", ["draft", "approved", "rejected"])
def test_approve_is_illegal_outside_submitted(status):
    with pytest.raises(IllegalTransitionError):
        approve(status)


def test_submitted_rejects_to_rejected():
    assert reject("submitted") == "rejected"


@pytest.mark.parametrize("status", ["draft", "approved", "rejected"])
def test_reject_is_illegal_outside_submitted(status):
    with pytest.raises(IllegalTransitionError):
        reject(status)


def test_approved_is_terminal():
    with pytest.raises(IllegalTransitionError):
        submit("approved")
    with pytest.raises(IllegalTransitionError):
        approve("approved")
    with pytest.raises(IllegalTransitionError):
        reject("approved")
