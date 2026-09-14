"""Bearer token validation against the realm's JWKS, and role-gated dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.models import Employee

_JWKS_FETCH_TIMEOUT_SECONDS = 5.0

_ROLES = {"employee", "manager"}

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentEmployee:
    id: uuid.UUID
    display_name: str
    role: str


def _fetch_jwks() -> jwt.PyJWKSet:
    try:
        response = httpx.get(settings.keycloak_jwks_url, timeout=_JWKS_FETCH_TIMEOUT_SECONDS)
        response.raise_for_status()
        return jwt.PyJWKSet.from_dict(response.json())
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "could not fetch signing keys") from error


def _signing_key(key_id: str | None) -> jwt.PyJWK:
    for key in _fetch_jwks().keys:
        if key.key_id == key_id:
            return key
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")


def _decode(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        signing_key = _signing_key(header.get("kid"))
        return jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            audience=settings.keycloak_audience,
            issuer=settings.keycloak_issuer,
        )
    except jwt.InvalidTokenError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token") from error


def _role(claims: dict) -> str:
    """A token must carry exactly one of the two realm roles; both or neither is a 403."""
    roles = set(claims.get("realm_access", {}).get("roles", [])) & _ROLES
    if len(roles) != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "token must carry exactly one of employee or manager")
    return roles.pop()


def current_employee(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: Session = Depends(get_session),
) -> CurrentEmployee:
    """Validates the bearer token and upserts the subject into `employees` from its claims."""
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")

    claims = _decode(credentials.credentials)
    role = _role(claims)
    employee_id = uuid.UUID(claims["sub"])
    email = claims.get("email") or claims.get("preferred_username") or ""
    display_name = claims.get("name") or claims.get("preferred_username") or email

    employee = session.get(Employee, employee_id)
    if employee is None:
        session.add(Employee(id=employee_id, email=email, display_name=display_name))
    else:
        employee.email = email
        employee.display_name = display_name
    session.commit()

    return CurrentEmployee(id=employee_id, display_name=display_name, role=role)


def require_employee(current: CurrentEmployee = Depends(current_employee)) -> CurrentEmployee:
    if current.role != "employee":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "only an employee can perform this action")
    return current


def require_manager(current: CurrentEmployee = Depends(current_employee)) -> CurrentEmployee:
    if current.role != "manager":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "only a manager can perform this action")
    return current
