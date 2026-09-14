"""FastAPI application entry point."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import CurrentEmployee, current_employee
from app.config import settings

app = FastAPI(title="MXA Timesheet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/me")
def me(current: CurrentEmployee = Depends(current_employee)) -> dict[str, str]:
    return {"employeeId": str(current.id), "displayName": current.display_name, "role": current.role}
