from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.supabase_client import clear_request_access_token

settings = get_settings()

# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def clear_request_auth_context(request, call_next):
    """Prevent an authenticated request token from surviving request scope."""
    try:
        return await call_next(request)
    finally:
        clear_request_access_token()

# ── Root health check (no prefix) ─────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health() -> dict:
    """Basic liveness probe."""
    return {"status": "ok"}

# ── API v1 router ─────────────────────────────────────────────────────────────

from app.api.router import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

