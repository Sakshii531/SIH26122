from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    activities,
    audit,
    dashboard,
    projects,
    progress,
    reports,
    reviews,
    schedules,
    status,
)

api_router = APIRouter()

api_router.include_router(status.router)
api_router.include_router(projects.router)
api_router.include_router(schedules.router)
api_router.include_router(reports.router)
api_router.include_router(activities.router)
api_router.include_router(reviews.router)
api_router.include_router(progress.router)
api_router.include_router(dashboard.router)
api_router.include_router(audit.router)
