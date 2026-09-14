"""Project creation and lookup, signed locally instead of against a live Keycloak."""

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
from app.models import Employee, Project

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
        session.execute(delete(Project))
        session.execute(delete(Employee))
        session.commit()
        session.close()


def _manager_headers(manager_id: uuid.UUID, name: str = "Mo Manager") -> dict[str, str]:
    token = _token(roles=["manager"], sub=str(manager_id), email="mo@mxa.com", name=name)
    return {"Authorization": f"Bearer {token}"}


def _employee_headers(employee_id: uuid.UUID | None = None) -> dict[str, str]:
    token = _token(roles=["employee"], sub=str(employee_id or uuid.uuid4()), email="e@mxa.com", name="Jamie")
    return {"Authorization": f"Bearer {token}"}


def _create_project_payload(**overrides: object) -> dict:
    payload = {
        "name": "Northwind migration",
        "description": "Migrate Northwind to the new platform",
        "startDate": "2026-01-05",
    }
    payload.update(overrides)
    return payload


def test_manager_creates_a_project_with_a_generated_six_character_code() -> None:
    manager_id = uuid.uuid4()
    client = TestClient(app)

    response = client.post(
        "/api/projects", json=_create_project_payload(), headers=_manager_headers(manager_id)
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["code"]) == 6
    assert body["code"].isalnum()
    assert body["code"].isupper()
    assert body["managerName"] == "Mo Manager"
    assert body["name"] == "Northwind migration"
    assert body["description"] == "Migrate Northwind to the new platform"
    assert body["startDate"] == "2026-01-05"


def test_client_supplied_code_is_ignored() -> None:
    manager_id = uuid.uuid4()
    client = TestClient(app)

    response = client.post(
        "/api/projects",
        json=_create_project_payload(code="AAAAAA"),
        headers=_manager_headers(manager_id),
    )

    assert response.status_code == 201
    assert response.json()["code"] != "AAAAAA"


def test_employee_cannot_create_a_project() -> None:
    client = TestClient(app)

    response = client.post("/api/projects", json=_create_project_payload(), headers=_employee_headers())

    assert response.status_code == 403


def test_list_projects_returns_only_the_manager_own_projects(session: Session) -> None:
    manager_id = uuid.uuid4()
    other_manager_id = uuid.uuid4()
    client = TestClient(app)

    client.post("/api/projects", json=_create_project_payload(), headers=_manager_headers(manager_id))
    client.post(
        "/api/projects",
        json=_create_project_payload(name="Contoso audit"),
        headers=_manager_headers(other_manager_id, name="Other Manager"),
    )

    response = client.get("/api/projects", headers=_manager_headers(manager_id))

    assert response.status_code == 200
    names = [project["name"] for project in response.json()]
    assert names == ["Northwind migration"]


def test_lookup_by_code_is_case_insensitive() -> None:
    manager_id = uuid.uuid4()
    client = TestClient(app)

    created = client.post(
        "/api/projects", json=_create_project_payload(), headers=_manager_headers(manager_id)
    ).json()
    code = created["code"]

    response = client.get(f"/api/projects/by-code/{code.lower()}", headers=_employee_headers())

    assert response.status_code == 200
    assert response.json()["code"] == code
    assert response.json()["name"] == "Northwind migration"


def test_lookup_by_unknown_code_is_a_404() -> None:
    client = TestClient(app)

    response = client.get("/api/projects/by-code/ZZZZZZ", headers=_employee_headers())

    assert response.status_code == 404
    assert response.json()["detail"] == "no project has code zzzzzz"
