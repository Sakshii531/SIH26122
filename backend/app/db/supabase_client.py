"""
Supabase client factory for the SIH26122 backend.

Design principles
-----------------
* Lazy initialisation — no Client is instantiated at import time.
  The factory functions are called only when a Supabase-backed repository
  actually needs a connection, so the in-memory test suite runs without
  any Supabase credentials present.

* Two clients, two keys
  - ``get_supabase_client()``        uses SUPABASE_KEY (anon / public key).
    Safe for operations that should respect Row-Level Security.
  - ``get_service_role_client()``    uses SUPABASE_SERVICE_ROLE_KEY.
    Bypasses RLS — must only be used for trusted server-side admin work.

* Singleton per key — each factory caches its Client in a module-level
  variable so we never create more than one connection per process.

* Never hardcodes credentials — both URL and keys are read exclusively
  from ``Settings`` (pydantic-settings → env / .env file).

* DB_PROVIDER guard — callers should only invoke these factories when
  ``settings.DB_PROVIDER == "supabase"``.  The helpers still raise a
  clear ``RuntimeError`` if credentials are absent, rather than a cryptic
  supabase-py error.

Usage (future Supabase repository implementations)
--------------------------------------------------
    from app.db import get_supabase_client

    client = get_supabase_client()
    result = client.table("projects").select("*").execute()
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

from supabase import Client, create_client

from app.core.config import get_settings

# Module-level singletons — populated on first call, None until then.
_anon_client: Optional[Client] = None
_service_role_client: Optional[Client] = None
_request_access_token: ContextVar[Optional[str]] = ContextVar("supabase_access_token", default=None)


def set_request_access_token(token: str) -> None:
    """Bind the current request's Supabase access token to its context."""
    _request_access_token.set(token)


def clear_request_access_token() -> None:
    """Clear the current request token after request-scoped work completes."""
    _request_access_token.set(None)


def get_request_access_token() -> Optional[str]:
    """Return the access token bound to the current request, if any."""
    return _request_access_token.get()


def get_supabase_client() -> Client:
    """
    Return a cached Supabase ``Client`` initialised with the **anon/public key**.

    This client respects Row-Level Security policies defined on your Supabase
    project and is suitable for data operations that run in the context of an
    authenticated (or unauthenticated) end user.

    Raises
    ------
    RuntimeError
        If ``SUPABASE_URL`` or ``SUPABASE_KEY`` are not set in the environment.
    """
    global _anon_client
    access_token = get_request_access_token()
    if access_token:
        client = _build_client(key_name="SUPABASE_KEY")
        client.postgrest.auth(access_token)
        return client
    if _anon_client is None:
        _anon_client = _build_client(key_name="SUPABASE_KEY")
    return _anon_client


def get_service_role_client() -> Client:
    """
    Return a cached Supabase ``Client`` initialised with the **service-role key**.

    This client bypasses Row-Level Security and should only be used for
    trusted server-side operations (e.g. seeding data, admin mutations,
    background jobs).  Never expose this client or its key to the frontend.

    Raises
    ------
    RuntimeError
        If ``SUPABASE_URL`` or ``SUPABASE_SERVICE_ROLE_KEY`` are not set.
    """
    global _service_role_client
    if _service_role_client is None:
        _service_role_client = _build_client(key_name="SUPABASE_SERVICE_ROLE_KEY")
    return _service_role_client


def reset_clients() -> None:
    """
    Discard cached Client singletons.

    Intended for use in tests that need to inject different settings
    between calls, or when the module state must be reset after monkeypatching.
    Not needed in normal application code.
    """
    global _anon_client, _service_role_client
    _anon_client = None
    _service_role_client = None
    clear_request_access_token()


# ── Internal helpers ──────────────────────────────────────────────────────────


def _build_client(*, key_name: str) -> Client:
    """
    Validate settings and call ``supabase.create_client``.

    Parameters
    ----------
    key_name:
        The Settings attribute name to use as the Supabase API key
        (either ``"SUPABASE_KEY"`` or ``"SUPABASE_SERVICE_ROLE_KEY"``).

    Raises
    ------
    RuntimeError
        If the URL or the requested key are missing from Settings.
    """
    settings = get_settings()

    url: Optional[str] = settings.SUPABASE_URL
    key: Optional[str] = getattr(settings, key_name, None)

    if not url:
        raise RuntimeError(
            "SUPABASE_URL is not set. "
            "Add it to your .env file or environment variables."
        )
    if not key:
        raise RuntimeError(
            f"{key_name} is not set. "
            "Add it to your .env file or environment variables."
        )

    return create_client(url, key)
