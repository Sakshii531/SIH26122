from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    # ── App metadata ──────────────────────────────────────────────────────────
    APP_NAME: str = "SIH26122 Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ── API ───────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"

    # ── Upload Limits ─────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Database & Supabase (Step 16 Readiness) ──────────────────────────────
    DB_PROVIDER: str = "in_memory"
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    DATABASE_URL: str | None = None

    # ── JWT & Authentication (Supabase Auth) ─────────────────────────────────
    JWT_SECRET: str | None = None
    JWT_ALGORITHM: str = "ES256"
    AUTH_ENABLED: bool = True

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://example.com"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow comma-separated strings to be parsed as lists
        env_list_separator=",",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        self.DB_PROVIDER = self.DB_PROVIDER.strip().lower()
        if self.DB_PROVIDER not in {"in_memory", "supabase"}:
            raise ValueError("DB_PROVIDER must be either 'in_memory' or 'supabase'")
        if "*" in self.CORS_ORIGINS:
            raise ValueError("Wildcard CORS origins are not permitted")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once)."""
    return Settings()
