"""HTTP routes for project creation and lookup; business logic lives in `app.services.projects`."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import CurrentEmployee, current_employee, require_manager
from app.db import get_session
from app.models import Project
from app.schemas.project import CreateProjectRequest, ProjectResponse
from app.services import projects as projects_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    responses={403: {"description": "the caller is not a manager"}},
)
def create_project(
    body: CreateProjectRequest,
    current: CurrentEmployee = Depends(require_manager),
    session: Session = Depends(get_session),
) -> Project:
    """Manager-only. The manager is the signed-in caller, not a request field; any `code` in the
    body is ignored — the platform always generates it."""
    return projects_service.create_project(
        session,
        manager_id=current.id,
        name=body.name,
        description=body.description,
        start_date=body.start_date,
    )


@router.get("", response_model=list[ProjectResponse], summary="List the signed-in manager's own projects")
def list_projects(
    current: CurrentEmployee = Depends(require_manager),
    session: Session = Depends(get_session),
) -> list[Project]:
    """Manager-only, scoped to projects the caller created."""
    return projects_service.list_projects_for_manager(session, current.id)


@router.get(
    "/by-code/{code}",
    response_model=ProjectResponse,
    summary="Resolve a project code to its project",
    responses={404: {"description": "no project has that code"}},
)
def get_project_by_code(
    code: str,
    current: CurrentEmployee = Depends(current_employee),
    session: Session = Depends(get_session),
) -> Project:
    """Open to both roles. The code is matched case-insensitively."""
    project = projects_service.get_project_by_code(session, code)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"no project has code {code.lower()}")
    return project
