"""Saving and submitting a week's timesheet, signed locally instead of against a live Keycloak."""

import time
import uuid
from collections.abc import Generator

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app import auth
from app.config import settings
from app.db import SessionLocal
from app.main import app
from app.models import Employee, Project, Timesheet, TimesheetLineItem

_KEY_ID = "test-key"
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# A Monday inside the week under test, as epoch seconds.
_MONDAY = 1789377420


def _jwks_dict() -> dict:
    jwk = jwt.algorithms.RSAAlgorithm.to_jwk(_PRIVATE_KEY.public_key(), as_dict=True)
    jwk.update(kid=_KEY_ID, use="sig", alg="RS256")
    return {"keys": [jwk]}


def _token(*, roles: list[str], sub: str | None = None, **claims: str) -> str:
    payload = {
        "iss": settings.keycloak_issuer,
        "aud": settings.keycloak_audience,
        "sub": sub or str(uuid.uuid4()),
        "exp": int(time.time()) + 300,
        "realm_access": {"roles": roles},
        **claims,
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm="RS256", headers={"kid": _KEY_ID})


@pytest.fixture(autouse=True)
def _stub_jwks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth, "_fetch_jwks", lambda: jwt.PyJWKSet.from_dict(_jwks_dict()))


@pytest.fixture(autouse=True)
def session() -> Generator[Session, None, None]:
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


def _manager_headers(manager_id: uuid.UUID | None = None) -> dict[str, str]:
    token = _token(roles=["manager"], sub=str(manager_id or uuid.uuid4()), email="mo@mxa.com", name="Mo Manager")
    return {"Authorization": f"Bearer {token}"}


def _employee_headers(employee_id: uuid.UUID) -> dict[str, str]:
    token = _token(roles=["employee"], sub=str(employee_id), email="jamie@mxa.com", name="Jamie Employee")
    return {"Authorization": f"Bearer {token}"}


def _create_project(client: TestClient, name: str = "Northwind migration") -> str:
    response = client.post(
        "/api/projects",
        json={"name": name, "description": "Some work", "startDate": "2026-01-05"},
        headers=_manager_headers(),
    )
    assert response.status_code == 201
    return response.json()["code"]


def _create_project_full(client: TestClient, name: str = "Northwind migration") -> dict:
    response = client.post(
        "/api/projects",
        json={"name": name, "description": "Some work", "startDate": "2026-01-05"},
        headers=_manager_headers(),
    )
    assert response.status_code == 201
    return response.json()


def _week(code: str, **hours: int) -> dict:
    days = {day: 0 for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")}
    days.update(hours)
    return {"projectCode": code, "hours": days}


def test_saving_a_draft_twice_keeps_the_same_project_code() -> None:
    employee_id = uuid.uuid4()
    client = TestClient(app)
    code = _create_project(client)
    headers = _employee_headers(employee_id)

    client.post("/api/timesheets/draft", json={"at": _MONDAY, "lineItems": [_week(code, monday=8)]}, headers=headers)
    response = client.post(
        "/api/timesheets/draft",
        json={"at": _MONDAY, "lineItems": [_week(code, monday=6, tuesday=2)]},
        headers=headers,
    )

    assert response.status_code == 200
    line_items = response.json()["lineItems"]
    assert len(line_items) == 1
    assert line_items[0]["projectCode"] == code
    assert line_items[0]["hours"]["monday"] == 6
    assert line_items[0]["hours"]["tuesday"] == 2


def test_submitting_a_saved_draft_reuses_its_project_codes() -> None:
    employee_id = uuid.uuid4()
    client = TestClient(app)
    first_code = _create_project(client)
    second_code = _create_project(client, name="Contoso audit")
    headers = _employee_headers(employee_id)

    line_items = [_week(first_code, monday=8, tuesday=8), _week(second_code, wednesday=4)]
    saved = client.post("/api/timesheets/draft", json={"at": _MONDAY, "lineItems": line_items}, headers=headers)
    assert saved.status_code == 200

    response = client.post("/api/timesheets/submitted", json={"at": _MONDAY, "lineItems": line_items}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "submitted"
    assert {item["projectCode"] for item in body["lineItems"]} == {first_code, second_code}


def test_a_rejected_timesheet_can_be_resubmitted_with_the_same_project_code() -> None:
    employee_id = uuid.uuid4()
    client = TestClient(app)
    code = _create_project(client)
    headers = _employee_headers(employee_id)

    submitted = client.post(
        "/api/timesheets/submitted",
        json={"at": _MONDAY, "lineItems": [_week(code, monday=8)]},
        headers=headers,
    )
    assert submitted.status_code == 200
    rejected = client.post(
        "/api/timesheets/rejected",
        json={"timesheetId": submitted.json()["id"], "message": "please fix Monday"},
        headers=_manager_headers(),
    )
    assert rejected.status_code == 200

    response = client.post(
        "/api/timesheets/submitted",
        json={"at": _MONDAY, "lineItems": [_week(code, monday=7, tuesday=1)]},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "submitted"
    assert len(body["lineItems"]) == 1
    assert body["lineItems"][0]["hours"]["monday"] == 7


def test_dropping_a_line_item_removes_it_from_the_week() -> None:
    employee_id = uuid.uuid4()
    client = TestClient(app)
    first_code = _create_project(client)
    second_code = _create_project(client, name="Contoso audit")
    headers = _employee_headers(employee_id)

    client.post(
        "/api/timesheets/draft",
        json={"at": _MONDAY, "lineItems": [_week(first_code, monday=8), _week(second_code, tuesday=4)]},
        headers=headers,
    )
    response = client.post(
        "/api/timesheets/draft",
        json={"at": _MONDAY, "lineItems": [_week(second_code, tuesday=4)]},
        headers=headers,
    )

    assert response.status_code == 200
    assert [item["projectCode"] for item in response.json()["lineItems"]] == [second_code]


def test_listing_submitted_timesheets_by_project_only_returns_timesheets_with_that_project() -> None:
    client = TestClient(app)
    first_project = _create_project_full(client)
    second_project = _create_project_full(client, name="Contoso audit")

    first_employee = _employee_headers(uuid.uuid4())
    second_employee = _employee_headers(uuid.uuid4())

    client.post(
        "/api/timesheets/submitted",
        json={"at": _MONDAY, "lineItems": [_week(first_project["code"], monday=8)]},
        headers=first_employee,
    )
    client.post(
        "/api/timesheets/submitted",
        json={"at": _MONDAY, "lineItems": [_week(second_project["code"], monday=8)]},
        headers=second_employee,
    )

    response = client.get(
        f"/api/timesheets/submitted?projectId={first_project['id']}", headers=_manager_headers()
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert {item["projectCode"] for item in body[0]["lineItems"]} == {first_project["code"]}


def test_listing_submitted_timesheets_by_project_matches_a_multi_project_timesheet_once() -> None:
    client = TestClient(app)
    first_project = _create_project_full(client)
    second_project = _create_project_full(client, name="Contoso audit")
    employee = _employee_headers(uuid.uuid4())

    client.post(
        "/api/timesheets/submitted",
        json={
            "at": _MONDAY,
            "lineItems": [_week(first_project["code"], monday=4), _week(second_project["code"], monday=4)],
        },
        headers=employee,
    )

    response = client.get(
        f"/api/timesheets/submitted?projectId={first_project['id']}", headers=_manager_headers()
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
