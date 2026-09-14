"""FastAPI application entry point."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.projects import router as projects_router
from app.api.timesheets import router as timesheets_router
from app.auth import CurrentEmployee, current_employee
from app.config import settings

app = FastAPI(
    title="MXA Timesheet API",
    description="Timesheet platform for a small consulting firm: projects, weekly timesheets, and manager review.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(timesheets_router)


@app.get("/api/health", tags=["meta"], summary="Liveness check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/me", tags=["meta"], summary="The signed-in employee or manager")
def me(current: CurrentEmployee = Depends(current_employee)) -> dict[str, str]:
    """`role` comes from the token's realm roles, not a stored column."""
    return {"employeeId": str(current.id), "displayName": current.display_name, "role": current.role}
