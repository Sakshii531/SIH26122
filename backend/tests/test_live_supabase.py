import os
from uuid import uuid4
import pytest

from app.core.config import get_settings
from app.repositories.factory import (
    get_audit_log_repository,
    get_project_repository,
    get_schedule_repository,
    get_user_repository,
    get_wbs_repository,
    reset_all_repositories,
)
from app.repositories.supabase_repos import (
    SupabaseAuditLogRepository,
    SupabaseProjectRepository,
    SupabaseScheduleRepository,
    SupabaseUserRepository,
    SupabaseWBSRepository,
)

settings = get_settings()

is_placeholder_url = not settings.SUPABASE_URL or "your-project" in settings.SUPABASE_URL.lower()
is_placeholder_key = not settings.SUPABASE_KEY or "your" in settings.SUPABASE_KEY.lower()
skip_live_tests = is_placeholder_url or is_placeholder_key

pytestmark = pytest.mark.skipif(
    skip_live_tests,
    reason="Real Supabase credentials (SUPABASE_URL & SUPABASE_KEY) are not configured in backend/.env",
)


@pytest.fixture
def live_supabase_env(monkeypatch):
    """Ensure DB_PROVIDER is set to supabase specifically for live verification tests."""
    monkeypatch.setattr(settings, "DB_PROVIDER", "supabase")
    reset_all_repositories()
    yield
    reset_all_repositories()


def test_live_supabase_connection(live_supabase_env):
    """Verify live Supabase connection and read access on repositories with DB_PROVIDER=supabase."""
    project_repo = get_project_repository()
    assert isinstance(project_repo, SupabaseProjectRepository)
    projects = project_repo.list_all()
    assert isinstance(projects, list)

    schedule_repo = get_schedule_repository()
    assert isinstance(schedule_repo, SupabaseScheduleRepository)
    schedules = schedule_repo.list_all()
    assert isinstance(schedules, list)

    user_repo = get_user_repository()
    assert isinstance(user_repo, SupabaseUserRepository)
    users = user_repo.list_all()
    assert isinstance(users, list)


def test_live_supabase_safety_behavior(live_supabase_env):
    """Verify that clear() raises NotImplementedError for data-safety on live Supabase repos."""
    project_repo = get_project_repository()
    with pytest.raises(NotImplementedError):
        project_repo.clear()

    schedule_repo = get_schedule_repository()
    with pytest.raises(NotImplementedError):
        schedule_repo.clear()

    audit_repo = get_audit_log_repository()
    with pytest.raises(NotImplementedError):
        audit_repo.clear()


