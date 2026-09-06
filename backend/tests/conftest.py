"""
Shared pytest fixtures for the SIH26122 backend test suite.

This conftest is placed at the tests/ level so every test module
automatically benefits from:
  - reset_stores  — autouse fixture that clears all in-memory stores
                    before AND after each test, guaranteeing isolation.
  - TestClient    — re-exported for convenience (optional, each module
                    may still create its own).

Do NOT import database helpers or external services here; this backend
is strictly in-memory.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_service import AuditService
from app.services.progress_workflow_service import ProgressWorkflowService
from app.services.review_workflow_service import ReviewWorkflowService


@pytest.fixture(autouse=True)
def reset_stores():
    """
    Clear every in-memory store before and after each test.

    Because the stores are class-level dicts (not request-scoped), tests
    that run in the same process share state unless we reset explicitly.
    This fixture runs automatically for *every* test in the suite.
    """
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()
    yield
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()


@pytest.fixture(scope="session")
def api_client() -> TestClient:
    """Session-scoped TestClient — share across tests that don't mutate state."""
    return TestClient(app)
