from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/status")
async def get_status() -> dict[str, str]:
    """API v1 status endpoint."""
    return {"status": "ok", "version": "v1"}
