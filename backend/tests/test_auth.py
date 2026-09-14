"""Token validation and role enforcement, signed locally instead of against a live Keycloak."""

import time
import uuid
from collections.abc import Generator

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app import auth
from app.config import settings
from app.db import SessionLocal
from app.main import app
from app.models import Employee

_KEY_ID = "test-key"
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


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
        session.execute(delete(Employee))
        session.commit()
        session.close()


def test_missing_token_is_rejected() -> None:
    client = TestClient(app)
    response = client.get("/api/me")
    assert response.status_code == 401


def test_both_roles_is_forbidden() -> None:
    client = TestClient(app)
    token = _token(roles=["employee", "manager"])
    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_neither_role_is_forbidden() -> None:
    client = TestClient(app)
    token = _token(roles=[])
    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_role_gated_route_rejects_the_wrong_role() -> None:
    gated_app = FastAPI()

    @gated_app.get("/manager-only")
    def manager_only(current: auth.CurrentEmployee = Depends(auth.require_manager)) -> dict[str, str]:
        return {"role": current.role}

    client = TestClient(gated_app)
    token = _token(roles=["employee"])
    response = client.get("/manager-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_employee_token_upserts_an_employee_row(session: Session) -> None:
    employee_id = uuid.uuid4()
    token = _token(
        roles=["employee"],
        sub=str(employee_id),
        email="jamie.employee@mxa.com",
        name="Jamie Employee",
    )

    client = TestClient(app)
    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    stored = session.get(Employee, employee_id)
    assert stored is not None
    assert stored.email == "jamie.employee@mxa.com"
    assert stored.display_name == "Jamie Employee"


def test_me_returns_the_expected_shape_for_an_employee() -> None:
    employee_id = uuid.uuid4()
    token = _token(roles=["employee"], sub=str(employee_id), email="a@mxa.com", name="Alice")

    client = TestClient(app)
    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"employeeId": str(employee_id), "displayName": "Alice", "role": "employee"}


def test_me_returns_the_expected_shape_for_a_manager() -> None:
    manager_id = uuid.uuid4()
    token = _token(roles=["manager"], sub=str(manager_id), email="m@mxa.com", name="Mo Manager")

    client = TestClient(app)
    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"employeeId": str(manager_id), "displayName": "Mo Manager", "role": "manager"}
