"""Business logic for creating and looking up projects, independent of HTTP concerns.

Returns ORM objects; the route's `response_model` reads them via `from_attributes`.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.project_code import generate_project_code
from app.models import Project

_MAX_CODE_ATTEMPTS = 5


def create_project(
    session: Session, *, manager_id: uuid.UUID, name: str, description: str, start_date: date
) -> Project:
    """A unique violation on the generated code retries with a fresh one instead of failing the request."""
    for _ in range(_MAX_CODE_ATTEMPTS):
        project = Project(
            code=generate_project_code(),
            name=name,
            manager_id=manager_id,
            description=description,
            start_date=start_date,
            created_at=datetime.now(timezone.utc),
        )
        session.add(project)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            continue
        return project
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "could not generate a unique project code")


def list_projects_for_manager(session: Session, manager_id: uuid.UUID) -> list[Project]:
    return (
        session.query(Project)
        .filter(Project.manager_id == manager_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project_by_code(session: Session, code: str) -> Project | None:
    return session.query(Project).filter(Project.code == code.upper()).one_or_none()
