"""
app.db — Supabase client helpers.

Exports the two public accessors:
  get_supabase_client()          — anon/public key client (reads, auth flows)
  get_service_role_client()      — service-role key client (admin writes, bypasses RLS)

Both raise RuntimeError when the required env vars are missing so that
misconfiguration is caught early rather than failing on the first query.

The module is intentionally lazy: no Client object is created at import time,
so the in-memory test suite continues to work without real Supabase credentials.
"""

from app.db.supabase_client import get_service_role_client, get_supabase_client

__all__ = ["get_supabase_client", "get_service_role_client"]
