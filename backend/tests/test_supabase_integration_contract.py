from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import UUID

from app.repositories.supabase_repos import SupabaseProjectRepository, SupabaseUserRepository


def test_project_repository_maps_database_primary_key_and_payload_columns():
    client = MagicMock()
    builder = MagicMock()
    client.table.return_value = builder
    builder.select.return_value = builder
    builder.insert.return_value = builder
    builder.eq.return_value = builder
    builder.execute.return_value = MagicMock(
        data=[
            {
                "project_id": "11111111-1111-1111-1111-111111111111",
                "name": "Mapped project",
                "description": "Read-only mapping test",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        ]
    )
    repository = SupabaseProjectRepository(client=client)

    rows = repository.list_all()
    assert rows[0].id == UUID("11111111-1111-1111-1111-111111111111")
    assert rows[0].project_id == rows[0].id
    assert rows[0].code is None


def test_user_repository_maps_name_role_and_user_id():
    client = MagicMock()
    builder = MagicMock()
    client.table.return_value = builder
    builder.select.return_value = builder
    builder.execute.return_value = MagicMock(
        data=[
            {
                "user_id": "22222222-2222-2222-2222-222222222222",
                "name": "Planner User",
                "email": "planner@example.test",
                "role": "Planner",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        ]
    )
    repository = SupabaseUserRepository(client=client)

    row = repository.list_all()[0]
    assert row.id == UUID("22222222-2222-2222-2222-222222222222")
    assert row.user_id == row.id
    assert row.username == "Planner User"
    assert row.role.value == "PLANNER"


def test_supabase_client_forwards_each_request_token_without_reusing_client():
    import app.db.supabase_client as supabase_client

    first_client = MagicMock()
    second_client = MagicMock()
    settings = MagicMock(
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_KEY="anon-key",
        SUPABASE_SERVICE_ROLE_KEY=None,
    )
    supabase_client.reset_clients()
    try:
        with (
            patch.object(supabase_client, "get_settings", return_value=settings),
            patch.object(
                supabase_client,
                "create_client",
                side_effect=[first_client, second_client],
            ),
        ):
            supabase_client.set_request_access_token("token-one")
            assert supabase_client.get_supabase_client() is first_client
            first_client.postgrest.auth.assert_called_once_with("token-one")

            supabase_client.set_request_access_token("token-two")
            assert supabase_client.get_supabase_client() is second_client
            second_client.postgrest.auth.assert_called_once_with("token-two")
    finally:
        supabase_client.reset_clients()
