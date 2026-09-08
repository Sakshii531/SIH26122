"""
Shared pytest fixtures for the SIH26122 backend test suite.

- reset_stores  — autouse; clears all in-memory stores before and after each test
- auth_bypass   — autouse; overrides get_current_user so existing tests run without JWTs
- api_client    — session-scoped TestClient
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthUser, get_current_user
from app.main import app
from app.repositories import reset_all_repositories
from app.services.audit_service import AuditService
from app.services.conflict_service import ConflictService
from app.services.progress_workflow_service import ProgressWorkflowService
from app.services.review_workflow_service import ReviewWorkflowService


# ── Auth bypass ───────────────────────────────────────────────────────────────

def _mock_admin_user() -> AuthUser:
    """Return a mock ADMIN — satisfies every role check in normal tests."""
    return AuthUser(user_id="test-admin", email="test@sih.local", role="ADMIN")


@pytest.fixture(autouse=True)
def auth_bypass():
    """
    Override get_current_user for every test so tests don't need real JWTs.

    Tests in test_auth.py create their own TestClient with this override
    removed so they can exercise the real JWT validation logic.
    """
    app.dependency_overrides[get_current_user] = _mock_admin_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# ── Store reset ───────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_stores():
    """Clear every in-memory store before and after each test."""
    reset_all_repositories()
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()
    ConflictService.clear_db()
    yield
    reset_all_repositories()
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()
    ConflictService.clear_db()


# ── Shared clients ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client() -> TestClient:
    """Session-scoped TestClient — share across tests that don't mutate state."""
    return TestClient(app)
