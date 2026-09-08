from __future__ import annotations

import asyncio
import pytest
from fastapi.testclient import TestClient

from app.core import auth as auth_module
from app.core.auth import AuthUser, get_current_user
from app.core.config import Settings, get_settings
from app.db.supabase_client import get_request_access_token, set_request_access_token
from app.main import app


def test_settings_reject_wildcard_cors():
    with pytest.raises(ValueError, match="Wildcard CORS"):
        Settings(CORS_ORIGINS=["*"])


def test_settings_reject_unknown_database_provider():
    with pytest.raises(ValueError, match="DB_PROVIDER"):
        Settings(DB_PROVIDER="unknown")


def test_supabase_validation_does_not_expose_exception_details(monkeypatch):
    class Jwks:
        def get_signing_key_from_jwt(self, token):
            raise RuntimeError("service-role-secret-and-database-url")

    monkeypatch.setattr(auth_module, "_jwks_client", lambda url: Jwks())
    credentials = type("Credentials", (), {"credentials": "opaque-token"})()
    settings = Settings(DB_PROVIDER="supabase", SUPABASE_URL="https://example.supabase.co")

    with pytest.raises(Exception) as exc_info:
        asyncio.run(auth_module.get_current_user(credentials=credentials, settings=settings))

    assert exc_info.value.status_code == 503
    assert "service-role-secret" not in str(exc_info.value.detail)
    assert "database-url" not in str(exc_info.value.detail)


def test_request_auth_context_is_cleared_after_http_request():
    async def authenticated_dependency():
        set_request_access_token("request-only-token")
        return AuthUser(user_id="request-user", role="ADMIN")

    app.dependency_overrides[get_current_user] = authenticated_dependency
    try:
        response = TestClient(app).get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        assert get_request_access_token() is None
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_schedule_upload_is_rejected_before_full_read(monkeypatch):
    monkeypatch.setattr(get_settings(), "MAX_UPLOAD_SIZE_MB", 0)
    response = TestClient(app).post(
        "/api/v1/schedules/import",
        files={"file": ("schedule.csv", b"a,b,c", "text/csv")},
    )
    assert response.status_code == 413