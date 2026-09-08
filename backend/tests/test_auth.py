"""
Step 16.6 — Authentication & RBAC unit tests.

Strategy
--------
Each test that needs real JWT validation:
  1. Removes the conftest get_current_user bypass from app.dependency_overrides
  2. Installs a get_settings override that supplies AUTH_ENABLED=True + TEST_SECRET
  3. Runs the request
  4. Cleans up both overrides in a finally block (via the auth_test_client fixture)

This avoids the lru_cache problem: because get_settings is now injected via
Depends() inside get_current_user, overriding it at the app level is enough
to supply fresh Settings without invalidating the module cache.

Coverage
--------
  Group 1 — Public endpoints accessible without any token
  Group 2 — Valid tokens: ADMIN / PLANNER / SUPERVISOR; role from various claims
  Group 3 — Missing token → 401
  Group 4 — Invalid / wrong-secret token → 401
  Group 5 — Expired token → 401
  Group 6 — Insufficient role → 403 with informative message
  Group 7 — Token missing 'sub' claim → 401
  Group 8 — JWT_SECRET not configured on server → 500
"""
from __future__ import annotations

import time
import asyncio
from typing import Any, Dict, Optional

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthUser, get_current_user
from app.core import auth as auth_module
from app.core.config import Settings, get_settings
from app.main import app

# ── Constants ─────────────────────────────────────────────────────────────────

TEST_SECRET = "test-jwt-secret-sih26122"
TEST_ALGORITHM = "HS256"


# ── Token builder ─────────────────────────────────────────────────────────────


def _token(
    sub: str = "user-123",
    email: str = "user@sih.local",
    role: str = "ADMIN",
    role_location: str = "app_metadata",   # "app_metadata" | "user_metadata" | "top_level"
    exp_offset: int = 3600,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {"sub": sub, "email": email, "iat": now, "exp": now + exp_offset}
    if role_location == "app_metadata":
        payload["app_metadata"] = {"role": role}
    elif role_location == "user_metadata":
        payload["user_metadata"] = {"role": role}
    else:
        payload["role"] = role
    if extra:
        payload.update(extra)
    return jwt.encode(payload, TEST_SECRET, algorithm=TEST_ALGORITHM)


# ── Settings factory ──────────────────────────────────────────────────────────


def _settings(secret: Optional[str] = TEST_SECRET) -> Settings:
    """Build Settings with auth enabled and the given JWT_SECRET."""
    return Settings(
        AUTH_ENABLED=True,
        JWT_SECRET=secret,
        JWT_ALGORITHM=TEST_ALGORITHM,
        DB_PROVIDER="in_memory",
        CORS_ORIGINS=["http://localhost:3000"],
    )


# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def auth_client():
    """
    TestClient with REAL JWT validation active.

    * Removes the conftest get_current_user bypass
    * Installs a get_settings override with TEST_SECRET
    * Restores both after the test
    """
    # Remove the conftest bypass
    app.dependency_overrides.pop(get_current_user, None)
    # Supply Settings with JWT_SECRET so the real auth path works
    real_settings = _settings(TEST_SECRET)
    app.dependency_overrides[get_settings] = lambda: real_settings

    yield TestClient(app, raise_server_exceptions=False)

    # Restore defaults
    app.dependency_overrides.pop(get_settings, None)
    # Re-install the conftest bypass so subsequent normal tests are unaffected
    app.dependency_overrides[get_current_user] = lambda: AuthUser(
        user_id="test-admin", email="test@sih.local", role="ADMIN"
    )


# ── 1. Public endpoints ───────────────────────────────────────────────────────


class TestPublicEndpoints:
    def test_root_health_no_token(self):
        """/health is public — always accessible."""
        client = TestClient(app)
        assert client.get("/health").status_code == 200

    def test_v1_status_no_token(self, auth_client):
        """/api/v1/status has no auth dependency — always accessible."""
        res = auth_client.get("/api/v1/status")
        assert res.status_code == 200


# ── 2. Valid tokens ───────────────────────────────────────────────────────────


class TestValidToken:
    def test_admin_token_dashboard_summary(self, auth_client):
        """ADMIN JWT → 200 on GET /api/v1/dashboard/summary."""
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {_token(role='ADMIN')}"},
        )
        assert res.status_code == 200

    def test_planner_token_progress_list(self, auth_client):
        """PLANNER JWT → 200 on GET /api/v1/progress."""
        res = auth_client.get(
            "/api/v1/progress",
            headers={"Authorization": f"Bearer {_token(role='PLANNER')}"},
        )
        assert res.status_code == 200

    def test_supervisor_token_reviews_list(self, auth_client):
        """SUPERVISOR JWT → 200 on GET /api/v1/reviews."""
        res = auth_client.get(
            "/api/v1/reviews",
            headers={"Authorization": f"Bearer {_token(role='SUPERVISOR')}"},
        )
        assert res.status_code == 200

    def test_role_from_app_metadata(self, auth_client):
        """Role in app_metadata.role is extracted correctly."""
        res = auth_client.get(
            "/api/v1/audit",
            headers={"Authorization": f"Bearer {_token(role='ADMIN', role_location='app_metadata')}"},
        )
        assert res.status_code == 200

    def test_role_from_user_metadata(self, auth_client):
        """Role in user_metadata.role is used when app_metadata is absent."""
        res = auth_client.get(
            "/api/v1/progress",
            headers={"Authorization": f"Bearer {_token(role='PLANNER', role_location='user_metadata')}"},
        )
        assert res.status_code == 200

    def test_role_from_top_level_claim(self, auth_client):
        """Top-level 'role' claim is the fallback."""
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {_token(role='ADMIN', role_location='top_level')}"},
        )
        assert res.status_code == 200


# ── 3. Missing token ──────────────────────────────────────────────────────────


class TestMissingToken:
    def test_dashboard_no_token_401(self, auth_client):
        assert auth_client.get("/api/v1/dashboard/summary").status_code == 401

    def test_reviews_no_token_401(self, auth_client):
        assert auth_client.get("/api/v1/reviews").status_code == 401

    def test_audit_no_token_401(self, auth_client):
        assert auth_client.get("/api/v1/audit").status_code == 401

    def test_progress_no_token_401(self, auth_client):
        assert auth_client.get("/api/v1/progress").status_code == 401

    def test_conflicts_no_token_401(self, auth_client):
        assert auth_client.get("/api/v1/conflicts").status_code == 401


# ── 4. Invalid token ──────────────────────────────────────────────────────────


class TestInvalidToken:
    def test_garbage_token_401(self, auth_client):
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert res.status_code == 401

    def test_wrong_secret_401(self, auth_client):
        bad_token = jwt.encode(
            {"sub": "u1", "role": "ADMIN", "exp": int(time.time()) + 3600},
            "wrong-secret",
            algorithm=TEST_ALGORITHM,
        )
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert res.status_code == 401

    def test_empty_bearer_value_401(self, auth_client):
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": "Bearer "},
        )
        assert res.status_code == 401


# ── 5. Expired token ──────────────────────────────────────────────────────────


class TestExpiredToken:
    def test_expired_token_401(self, auth_client):
        expired = _token(role="ADMIN", exp_offset=-10)
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {expired}"},
        )
        assert res.status_code == 401

    def test_expired_detail_contains_expired(self, auth_client):
        expired = _token(role="ADMIN", exp_offset=-60)
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {expired}"},
        )
        assert res.status_code == 401
        assert "expired" in res.json()["detail"].lower()


# ── 6. Insufficient role ──────────────────────────────────────────────────────


class TestInsufficientRole:
    def test_supervisor_cannot_create_progress_403(self, auth_client):
        """POST /progress needs PLANNER or ADMIN — SUPERVISOR gets 403."""
        res = auth_client.post(
            "/api/v1/progress",
            headers={"Authorization": f"Bearer {_token(role='SUPERVISOR')}"},
            json={"review_id": "00000000-0000-0000-0000-000000000001"},
        )
        assert res.status_code == 403

    def test_supervisor_cannot_submit_decision_403(self, auth_client):
        """POST /reviews/{id}/decision needs PLANNER — SUPERVISOR gets 403."""
        res = auth_client.post(
            "/api/v1/reviews/00000000-0000-0000-0000-000000000001/decision",
            headers={"Authorization": f"Bearer {_token(role='SUPERVISOR')}"},
            json={"decision": "APPROVED", "reviewer_id": "sv-1"},
        )
        assert res.status_code == 403

    def test_user_role_cannot_import_schedule_403(self, auth_client):
        """POST /schedules/import needs PLANNER — USER role gets 403."""
        import io
        csv_bytes = b"activity_id,activity_name,wbs,discipline\nA1,Test,1.0,Civil\n"
        res = auth_client.post(
            "/api/v1/schedules/import",
            headers={"Authorization": f"Bearer {_token(role='USER', role_location='top_level')}"},
            files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        assert res.status_code == 403

    def test_403_detail_contains_role_context(self, auth_client):
        """403 body must mention permissions or role info."""
        res = auth_client.post(
            "/api/v1/progress",
            headers={"Authorization": f"Bearer {_token(role='SUPERVISOR')}"},
            json={"review_id": "00000000-0000-0000-0000-000000000001"},
        )
        assert res.status_code == 403
        detail = res.json()["detail"].lower()
        assert "permission" in detail or "role" in detail


# ── 7. Token missing sub ──────────────────────────────────────────────────────


class TestMissingSubClaim:
    def test_no_sub_returns_401(self, auth_client):
        """Valid signature, missing 'sub' → 401."""
        token = jwt.encode(
            {"email": "u@test.com", "role": "ADMIN", "exp": int(time.time()) + 3600},
            TEST_SECRET,
            algorithm=TEST_ALGORITHM,
        )
        res = auth_client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 401
        assert "sub" in res.json()["detail"].lower()


# ── 8. JWT_SECRET not configured ─────────────────────────────────────────────


class TestJWTSecretNotConfigured:
    def test_missing_secret_returns_500(self):
        """No JWT_SECRET on server → 500."""
        # Remove bypass, install no-secret settings
        app.dependency_overrides.pop(get_current_user, None)
        no_secret = _settings(secret=None)
        app.dependency_overrides[get_settings] = lambda: no_secret

        try:
            client = TestClient(app, raise_server_exceptions=False)
            token = jwt.encode(
                {"sub": "u1", "role": "ADMIN", "exp": int(time.time()) + 3600},
                "some-secret",
                algorithm=TEST_ALGORITHM,
            )
            res = client.get(
                "/api/v1/dashboard/summary",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 500
        finally:
            app.dependency_overrides.pop(get_settings, None)
            app.dependency_overrides[get_current_user] = lambda: AuthUser(
                user_id="test-admin", email="test@sih.local", role="ADMIN"
            )


class TestSupabaseMapping:
    def test_supabase_mode_uses_database_role_not_token_claim(self, monkeypatch):
        class SigningKey:
            key = TEST_SECRET

        class Jwks:
            def get_signing_key_from_jwt(self, token):
                return SigningKey()

        class Query:
            def select(self, fields):
                return self

            def eq(self, field, value):
                assert field == "auth_user_id"
                assert value == "auth-user-1"
                return self

            def limit(self, count):
                return self

            def execute(self):
                return type("Response", (), {"data": [{"auth_user_id": "auth-user-1", "email": "planner@test", "role": "Planner"}]})()

        class Client:
            def table(self, name):
                assert name == "users"
                return Query()

        monkeypatch.setattr(auth_module, "_jwks_client", lambda url: Jwks())
        monkeypatch.setattr(auth_module, "get_service_role_client", lambda: Client())
        settings = Settings(
            DB_PROVIDER="supabase",
            SUPABASE_URL="https://example.supabase.co",
            JWT_ALGORITHM=TEST_ALGORITHM,
        )
        token = _token(
            sub="auth-user-1",
            role="Supervisor",
            extra={"iss": "https://example.supabase.co/auth/v1", "aud": "authenticated"},
        )
        user = asyncio.run(
            get_current_user(
                credentials=type("Credentials", (), {"credentials": token})(),
                settings=settings,
            )
        )
        assert user.user_id == "auth-user-1"
        assert user.role == "PLANNER"
        assert user.email == "planner@test"

    def test_supabase_mode_rejects_unmapped_user(self, monkeypatch):
        class SigningKey:
            key = TEST_SECRET

        class Jwks:
            def get_signing_key_from_jwt(self, token):
                return SigningKey()

        class Query:
            def select(self, fields): return self
            def eq(self, field, value): return self
            def limit(self, count): return self
            def execute(self): return type("Response", (), {"data": []})()

        class Client:
            def table(self, name): return Query()

        monkeypatch.setattr(auth_module, "_jwks_client", lambda url: Jwks())
        monkeypatch.setattr(auth_module, "get_service_role_client", lambda: Client())
        settings = Settings(DB_PROVIDER="supabase", SUPABASE_URL="https://example.supabase.co", JWT_ALGORITHM=TEST_ALGORITHM)
        with pytest.raises(Exception) as exc_info:
            asyncio.run(get_current_user(
                credentials=type("Credentials", (), {"credentials": _token(
                    sub="missing",
                    extra={"iss": "https://example.supabase.co/auth/v1", "aud": "authenticated"},
                )})(),
                settings=settings,
            ))
        assert getattr(exc_info.value, "status_code", None) == 403
