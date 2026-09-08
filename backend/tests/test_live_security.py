from __future__ import annotations

import pytest
import requests

from app.core.config import get_settings
from app.db.supabase_client import get_service_role_client, get_supabase_client

settings = get_settings()
is_placeholder_url = not settings.SUPABASE_URL or "your-project" in settings.SUPABASE_URL.lower()
is_placeholder_key = not settings.SUPABASE_KEY or "your" in settings.SUPABASE_KEY.lower()

pytestmark = pytest.mark.skipif(
    is_placeholder_url or is_placeholder_key,
    reason="Real Supabase credentials are not configured",
)


def test_live_supabase_uses_es256_jwks():
    response = requests.get(
        f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json",
        headers={"apikey": settings.SUPABASE_KEY},
        timeout=15,
    )
    assert response.status_code == 200
    keys = response.json()["keys"]
    assert keys
    assert {key["alg"] for key in keys} == {"ES256"}
    assert {key["kty"] for key in keys} == {"EC"}


def test_live_users_roles_and_auth_mapping_are_read_only():
    rows = get_service_role_client().table("users").select("auth_user_id,role").execute().data or []
    assert rows
    assert all(row.get("auth_user_id") for row in rows)
    assert {row["role"] for row in rows} <= {"Planner", "Supervisor"}


def test_live_anon_client_cannot_read_users_under_rls():
    response = get_supabase_client().table("users").select("user_id").limit(1).execute()
    assert response.data == []
