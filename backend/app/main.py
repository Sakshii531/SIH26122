from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Root health check (no prefix) ─────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health() -> dict:
    """Basic liveness probe."""
    return {"status": "ok"}

# ── API v1 router ─────────────────────────────────────────────────────────────

from app.api.router import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

