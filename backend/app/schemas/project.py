"""Request and response DTOs for the projects API. Response models read straight off the ORM objects."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import AliasPath, Field

from app.schemas.base import AppModel


class CreateProjectRequest(AppModel):
    name: str
    description: str
    start_date: date


class ProjectResponse(AppModel):
    id: uuid.UUID
    code: str
    name: str
    manager_name: str = Field(validation_alias=AliasPath("manager", "display_name"))
    description: str
    start_date: date
