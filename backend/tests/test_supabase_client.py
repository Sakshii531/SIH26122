"""
Step 16.2 — Supabase client setup tests.

All tests run with **fake** credentials injected via monkeypatch / direct
Settings overrides.  No real Supabase network calls are made.

Design:
* We never instantiate the real create_client with live credentials.
* The module-level singletons are reset between tests with reset_clients().
* DB_PROVIDER is left as "in_memory" to confirm the rest of the app is
  unaffected — the factories must only be invoked explicitly.
"""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest

# ── helpers ──────────────────────────────────────────────────────────────────


def _fake_settings(*, url: str | None, key: str | None, srv: str | None):
    """Return a mock Settings-like object with the given Supabase fields."""
    s = MagicMock()
    s.SUPABASE_URL = url
    s.SUPABASE_KEY = key
    s.SUPABASE_SERVICE_ROLE_KEY = srv
    s.DB_PROVIDER = "in_memory"
    return s


# ── import fresh module so module globals are pristine each test ─────────────


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset the singleton cache in supabase_client before each test."""
    import app.db.supabase_client as mod

    mod.reset_clients()
    yield
    mod.reset_clients()


# ── tests: successful construction (no real network) ─────────────────────────


class TestGetSupabaseClient:
    """get_supabase_client() — anon/public key path."""

    def test_returns_client_when_credentials_present(self):
        """Factory builds and caches a Client when URL + KEY are set."""
        fake_client = MagicMock()
        fake_settings = _fake_settings(
            url="https://fake.supabase.co",
            key="fake-anon-key",
            srv=None,
        )

        import app.db.supabase_client as mod

        with (
            patch.object(mod, "get_settings", return_value=fake_settings),
            patch("app.db.supabase_client.create_client", return_value=fake_client) as mock_create,
        ):
            client = mod.get_supabase_client()

        mock_create.assert_called_once_with("https://fake.supabase.co", "fake-anon-key")
        assert client is fake_client

    def test_singleton_not_recreated_on_second_call(self):
        """create_client is called only once — singleton is reused."""
        fake_client = MagicMock()
        fake_settings = _fake_settings(
            url="https://fake.supabase.co",
            key="fake-anon-key",
            srv=None,
        )

        import app.db.supabase_client as mod

        with (
            patch.object(mod, "get_settings", return_value=fake_settings),
            patch("app.db.supabase_client.create_client", return_value=fake_client) as mock_create,
        ):
            c1 = mod.get_supabase_client()
            c2 = mod.get_supabase_client()

        assert c1 is c2
        mock_create.assert_called_once()


class TestGetServiceRoleClient:
    """get_service_role_client() — service-role key path."""

    def test_returns_client_when_credentials_present(self):
        """Factory builds a Client using the service-role key."""
        fake_client = MagicMock()
        fake_settings = _fake_settings(
            url="https://fake.supabase.co",
            key=None,
            srv="fake-service-role-key",
        )

        import app.db.supabase_client as mod

        with (
            patch.object(mod, "get_settings", return_value=fake_settings),
            patch("app.db.supabase_client.create_client", return_value=fake_client) as mock_create,
        ):
            client = mod.get_service_role_client()

        mock_create.assert_called_once_with(
            "https://fake.supabase.co", "fake-service-role-key"
        )
        assert client is fake_client

    def test_singleton_not_recreated_on_second_call(self):
        """Service-role client is also a singleton."""
        fake_client = MagicMock()
        fake_settings = _fake_settings(
            url="https://fake.supabase.co",
            key=None,
            srv="fake-service-role-key",
        )

        import app.db.supabase_client as mod

        with (
            patch.object(mod, "get_settings", return_value=fake_settings),
            patch("app.db.supabase_client.create_client", return_value=fake_client) as mock_create,
        ):
            c1 = mod.get_service_role_client()
            c2 = mod.get_service_role_client()

        assert c1 is c2
        mock_create.assert_called_once()


# ── tests: error handling ─────────────────────────────────────────────────────


class TestMissingCredentials:
    """RuntimeError is raised when required env vars are absent."""

    def test_missing_url_raises_for_anon_client(self):
        fake_settings = _fake_settings(url=None, key="fake-key", srv=None)

        import app.db.supabase_client as mod

        with patch.object(mod, "get_settings", return_value=fake_settings):
            with pytest.raises(RuntimeError, match="SUPABASE_URL is not set"):
                mod.get_supabase_client()

    def test_missing_key_raises_for_anon_client(self):
        fake_settings = _fake_settings(
            url="https://fake.supabase.co", key=None, srv=None
        )

        import app.db.supabase_client as mod

        with patch.object(mod, "get_settings", return_value=fake_settings):
            with pytest.raises(RuntimeError, match="SUPABASE_KEY is not set"):
                mod.get_supabase_client()

    def test_missing_url_raises_for_service_role_client(self):
        fake_settings = _fake_settings(url=None, key=None, srv="fake-srv-key")

        import app.db.supabase_client as mod

        with patch.object(mod, "get_settings", return_value=fake_settings):
            with pytest.raises(RuntimeError, match="SUPABASE_URL is not set"):
                mod.get_service_role_client()

    def test_missing_service_role_key_raises(self):
        fake_settings = _fake_settings(
            url="https://fake.supabase.co", key=None, srv=None
        )

        import app.db.supabase_client as mod

        with patch.object(mod, "get_settings", return_value=fake_settings):
            with pytest.raises(RuntimeError, match="SUPABASE_SERVICE_ROLE_KEY is not set"):
                mod.get_service_role_client()


# ── tests: reset_clients ──────────────────────────────────────────────────────


class TestResetClients:
    """reset_clients() clears the singleton cache."""

    def test_reset_allows_fresh_client_creation(self):
        """After reset, the next call to get_supabase_client() creates a new instance."""
        first_client = MagicMock()
        second_client = MagicMock()
        fake_settings = _fake_settings(
            url="https://fake.supabase.co", key="fake-key", srv=None
        )

        import app.db.supabase_client as mod

        with (
            patch.object(mod, "get_settings", return_value=fake_settings),
            patch(
                "app.db.supabase_client.create_client",
                side_effect=[first_client, second_client],
            ) as mock_create,
        ):
            c1 = mod.get_supabase_client()
            mod.reset_clients()
            c2 = mod.get_supabase_client()

        assert c1 is first_client
        assert c2 is second_client
        assert mock_create.call_count == 2


# ── tests: public API surface (app.db re-export) ──────────────────────────────


class TestPublicAPIExport:
    """app.db must re-export both helpers."""

    def test_get_supabase_client_importable_from_app_db(self):
        from app.db import get_supabase_client  # noqa: F401

        assert callable(get_supabase_client)

    def test_get_service_role_client_importable_from_app_db(self):
        from app.db import get_service_role_client  # noqa: F401

        assert callable(get_service_role_client)


# ── tests: Settings integration (no hardcoded credentials) ───────────────────


class TestSettingsIntegration:
    """Verify SUPABASE_URL and SUPABASE_KEY fields exist on Settings."""

    def test_settings_has_supabase_url_field(self):
        from app.core.config import Settings

        # Field must exist and default to None
        s = Settings(
            SUPABASE_URL=None,
            SUPABASE_KEY=None,
        )
        assert s.SUPABASE_URL is None

    def test_settings_has_supabase_key_field(self):
        from app.core.config import Settings

        s = Settings(SUPABASE_KEY=None)
        assert s.SUPABASE_KEY is None

    def test_settings_has_service_role_key_field(self):
        from app.core.config import Settings

        s = Settings(SUPABASE_SERVICE_ROLE_KEY=None)
        assert s.SUPABASE_SERVICE_ROLE_KEY is None

    def test_db_provider_default_is_in_memory(self):
        """DB_PROVIDER must default to in_memory — storage must not switch."""
        from app.core.config import Settings

        s = Settings()
        assert s.DB_PROVIDER == "in_memory"
