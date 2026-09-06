from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_service import AuditService
from app.services.progress_workflow_service import ProgressWorkflowService
from app.services.review_workflow_service import ReviewWorkflowService

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db_stores():
    """Reset in-memory databases before each test."""
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()


def create_sample_review(decision: str | None = None) -> str:
    """Helper to create and optionally finalize a review item."""
    report_id = str(uuid4())
    act_id = str(uuid4())
    create_res = client.post(
        "/api/v1/reviews",
        json={
            "report_id": report_id,
            "schedule_activity_id": act_id,
            "confidence_score": 0.85,
            "extracted_progress_percentage": 50.0,
            "extracted_status": "IN_PROGRESS",
        },
    )
    review_id = create_res.json()["id"]

    if decision == "APPROVED":
        client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "APPROVED", "reviewer_id": "PLANNER-01", "comments": "Approved AI match"},
        )
    elif decision == "REJECTED":
        client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "REJECTED", "reviewer_id": "PLANNER-01", "comments": "Rejected AI match"},
        )
    elif decision == "MODIFIED":
        client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={
                "decision": "MODIFIED",
                "reviewer_id": "PLANNER-01",
                "corrected_progress_percentage": 65.0,
                "comments": "Corrected progress to 65%",
            },
        )

    return review_id


def test_approved_review_to_progress():
    """Test 1: Approved review converts to a ProgressEvent preserving AI-suggested values."""
    review_id = create_sample_review(decision="APPROVED")

    res = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res.status_code == 201
    data = res.json()
    assert data["review_id"] == review_id
    assert data["progress_percentage"] == 50.0
    assert "id" in data
    assert "timestamp" in data


def test_modified_review_to_progress():
    """Test 2: Modified review converts to ProgressEvent using reviewer-corrected values."""
    review_id = create_sample_review(decision="MODIFIED")

    res = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res.status_code == 201
    data = res.json()
    assert data["review_id"] == review_id
    assert data["progress_percentage"] == 65.0


def test_rejected_review_blocked():
    """Test 3: Progress creation from a REJECTED review is blocked with 400 Bad Request."""
    review_id = create_sample_review(decision="REJECTED")

    res = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res.status_code == 400
    assert "Only APPROVED or MODIFIED reviews are allowed" in res.json()["detail"]


def test_pending_review_blocked():
    """Test 4: Progress creation from a PENDING review is blocked with 400 Bad Request."""
    review_id = create_sample_review(decision=None)  # Status is PENDING

    res = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res.status_code == 400
    assert "Only APPROVED or MODIFIED reviews are allowed" in res.json()["detail"]


def test_duplicate_progress_blocked():
    """Test 5: Attempting to create duplicate progress events from the same review is blocked."""
    review_id = create_sample_review(decision="APPROVED")

    # First attempt
    res1 = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res1.status_code == 201

    # Second attempt
    res2 = client.post("/api/v1/progress", json={"review_id": review_id})
    assert res2.status_code == 400
    assert "already created for review" in res2.json()["detail"]


def test_progress_retrieval_and_filtering():
    """Test 6: Progress event retrieval by ID and filtering list by activity_id and report_id."""
    rev1 = create_sample_review(decision="APPROVED")
    prog1 = client.post("/api/v1/progress", json={"review_id": rev1}).json()
    prog_id = prog1["id"]
    act_id = prog1["schedule_activity_id"]
    rep_id = prog1["field_report_id"]

    # Get by ID
    get_res = client.get(f"/api/v1/progress/{prog_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == prog_id

    # Filter by activity_id
    filter_act = client.get(f"/api/v1/progress?activity_id={act_id}")
    assert filter_act.status_code == 200
    assert len(filter_act.json()) == 1
    assert filter_act.json()[0]["id"] == prog_id

    # Filter by report_id
    filter_rep = client.get(f"/api/v1/progress?report_id={rep_id}")
    assert filter_rep.status_code == 200
    assert len(filter_rep.json()) == 1


def test_audit_event_creation():
    """Test 7: Creating a progress event automatically records an AuditEvent."""
    rev_id = create_sample_review(decision="APPROVED")
    prog = client.post("/api/v1/progress", json={"review_id": rev_id}).json()
    prog_id = prog["id"]

    # List audit events
    audit_res = client.get("/api/v1/audit")
    assert audit_res.status_code == 200
    audits = audit_res.json()
    assert len(audits) >= 1

    event = next(a for a in audits if a["entity_id"] == prog_id)
    assert event["event_type"] == "PROGRESS_UPDATED"
    assert event["entity_type"] == "ProgressEvent"
    assert event["actor_id"] == "PLANNER-01"


def test_audit_retrieval_and_filtering():
    """Test 8: Audit event retrieval by ID and filtering by entity_type / entity_id."""
    rev_id = create_sample_review(decision="APPROVED")
    prog = client.post("/api/v1/progress", json={"review_id": rev_id}).json()
    prog_id = prog["id"]

    # Get audit list filtered by entity_id
    audits = client.get(f"/api/v1/audit?entity_id={prog_id}").json()
    assert len(audits) == 1
    audit_id = audits[0]["id"]

    # Get single audit event by ID
    single = client.get(f"/api/v1/audit/{audit_id}")
    assert single.status_code == 200
    assert single.json()["id"] == audit_id


def test_invalid_ids_handling():
    """Test 9: Invalid/non-existent IDs for progress and audit return 404/422."""
    missing_id = str(uuid4())

    # Progress 404
    p_404 = client.get(f"/api/v1/progress/{missing_id}")
    assert p_404.status_code == 404

    # Audit 404
    a_404 = client.get(f"/api/v1/audit/{missing_id}")
    assert a_404.status_code == 404

    # Invalid UUID 422
    inv_res = client.get("/api/v1/progress/invalid-uuid-string")
    assert inv_res.status_code == 422
