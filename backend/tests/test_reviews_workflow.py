from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.review_workflow_service import ReviewWorkflowService

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory review database before each test."""
    ReviewWorkflowService.clear_db()


def test_create_review_pending():
    """Test creating a review item creates it with initial PENDING status."""
    report_id = str(uuid4())
    activity_id = str(uuid4())
    payload = {
        "report_id": report_id,
        "schedule_activity_id": activity_id,
        "matched_activity_code": "ACT-101",
        "confidence_score": 0.75,
        "extracted_progress_percentage": 50.0,
        "extracted_status": "IN_PROGRESS",
        "discipline": "Civil",
        "location": "Zone 1",
    }
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["confidence_score"] == 0.75
    assert data["report_id"] == report_id
    assert data["matched_activity_code"] == "ACT-101"
    assert "id" in data


def test_get_review_by_id():
    """Test retrieving a review item by its UUID."""
    report_id = str(uuid4())
    payload = {
        "report_id": report_id,
        "confidence_score": 0.82,
        "extracted_progress_percentage": 60.0,
    }
    create_res = client.post("/api/v1/reviews", json=payload)
    review_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/reviews/{review_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == review_id
    assert get_res.json()["status"] == "PENDING"


def test_get_review_not_found():
    """Test retrieving a non-existent review ID returns 404."""
    non_existent_id = str(uuid4())
    response = client.get(f"/api/v1/reviews/{non_existent_id}")
    assert response.status_code == 404


def test_approve_decision():
    """Test approving a pending review item."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"report_id": str(uuid4()), "confidence_score": 0.85, "extracted_progress_percentage": 40.0},
    )
    review_id = create_res.json()["id"]

    decision_payload = {
        "decision": "APPROVED",
        "reviewer_id": "PLANNER-01",
        "comments": "Verified and approved.",
    }
    dec_res = client.post(f"/api/v1/reviews/{review_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    data = dec_res.json()
    assert data["status"] == "APPROVED"
    assert data["decision"] == "APPROVED"
    assert data["reviewer_id"] == "PLANNER-01"
    assert data["comments"] == "Verified and approved."
    assert data["decision_at"] is not None


def test_reject_decision():
    """Test rejecting a pending review item."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"report_id": str(uuid4()), "confidence_score": 0.40, "extracted_progress_percentage": 10.0},
    )
    review_id = create_res.json()["id"]

    decision_payload = {
        "decision": "REJECTED",
        "reviewer_id": "PLANNER-02",
        "comments": "Report conflicts with site photos.",
    }
    dec_res = client.post(f"/api/v1/reviews/{review_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    data = dec_res.json()
    assert data["status"] == "REJECTED"
    assert data["decision"] == "REJECTED"
    assert data["reviewer_id"] == "PLANNER-02"


def test_modify_decision():
    """Test modifying a review item with corrected values."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"report_id": str(uuid4()), "confidence_score": 0.65, "extracted_progress_percentage": 30.0},
    )
    review_id = create_res.json()["id"]
    corrected_act_id = str(uuid4())

    decision_payload = {
        "decision": "MODIFIED",
        "reviewer_id": "PLANNER-03",
        "corrected_activity_id": corrected_act_id,
        "corrected_progress_percentage": 45.0,
        "comments": "Corrected activity match and percentage.",
    }
    dec_res = client.post(f"/api/v1/reviews/{review_id}/decision", json=decision_payload)
    assert dec_res.status_code == 200
    data = dec_res.json()
    assert data["status"] == "MODIFIED"
    assert data["decision"] == "MODIFIED"
    assert data["corrected_activity_id"] == corrected_act_id
    assert data["corrected_progress_percentage"] == 45.0


def test_invalid_confidence_score():
    """Test creating review with confidence score out of range 0.0 - 1.0 produces 422."""
    res1 = client.post("/api/v1/reviews", json={"report_id": str(uuid4()), "confidence_score": 1.5})
    assert res1.status_code == 422

    res2 = client.post("/api/v1/reviews", json={"report_id": str(uuid4()), "confidence_score": -0.1})
    assert res2.status_code == 422


def test_invalid_decision():
    """Test submitting invalid decision value returns 422."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"report_id": str(uuid4()), "confidence_score": 0.80},
    )
    review_id = create_res.json()["id"]

    dec_res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "UNKNOWN_DECISION", "reviewer_id": "PLANNER-01"},
    )
    assert dec_res.status_code == 422


def test_duplicate_finalized_decision():
    """Test attempting to submit a decision on an already finalized review returns 400."""
    create_res = client.post(
        "/api/v1/reviews",
        json={"report_id": str(uuid4()), "confidence_score": 0.90},
    )
    review_id = create_res.json()["id"]

    # First decision
    client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "APPROVED", "reviewer_id": "PLANNER-01"},
    )

    # Second decision attempt on finalized review
    second_res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "REJECTED", "reviewer_id": "PLANNER-02"},
    )
    assert second_res.status_code == 400
    assert "already finalized" in second_res.json()["detail"]


def test_list_reviews_with_status_filter():
    """Test listing review items with optional status filter."""
    r1 = client.post("/api/v1/reviews", json={"report_id": str(uuid4()), "confidence_score": 0.9}).json()
    r2 = client.post("/api/v1/reviews", json={"report_id": str(uuid4()), "confidence_score": 0.8}).json()

    # Finalize r1
    client.post(f"/api/v1/reviews/{r1['id']}/decision", json={"decision": "APPROVED", "reviewer_id": "P1"})

    # All reviews
    res_all = client.get("/api/v1/reviews")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2

    # Filter PENDING
    res_pending = client.get("/api/v1/reviews?status=PENDING")
    assert res_pending.status_code == 200
    assert len(res_pending.json()) == 1
    assert res_pending.json()[0]["id"] == r2["id"]

    # Filter APPROVED
    res_approved = client.get("/api/v1/reviews?status=APPROVED")
    assert res_approved.status_code == 200
    assert len(res_approved.json()) == 1
    assert res_approved.json()[0]["id"] == r1["id"]
