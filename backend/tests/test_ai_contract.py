from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import MatchStatus

client = TestClient(app)


def test_extraction_endpoint_success():
    """Test POST /api/v1/reports/{report_id}/extraction with a valid extraction request payload."""
    report_id = str(uuid4())
    project_id = str(uuid4())
    payload = {
        "report_id": report_id,
        "project_id": project_id,
        "source_format": "TEXT",
        "raw_content": "Excavated 200m3 for foundation at Zone 1.",
        "metadata": {"discipline": "Civil", "location": "Zone 1"},
    }
    response = client.post(f"/api/v1/reports/{report_id}/extraction", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == report_id
    assert data["processing_status"] == "SUCCESS"
    assert data["extraction_confidence"] == 0.88
    assert data["extracted_progress_percentage"] == 45.0
    assert data["discipline"] == "Civil"
    assert data["location"] == "Zone 1"


def test_extraction_endpoint_id_mismatch():
    """Test POST /api/v1/reports/{report_id}/extraction with mismatched path and body IDs returns 400."""
    path_report_id = str(uuid4())
    body_report_id = str(uuid4())
    payload = {
        "report_id": body_report_id,
        "source_format": "TEXT",
        "raw_content": "Test content",
    }
    response = client.post(f"/api/v1/reports/{path_report_id}/extraction", json=payload)
    assert response.status_code == 400
    assert "Report ID mismatch" in response.json()["detail"]


def test_matching_endpoint_success():
    """Test POST /api/v1/reports/{report_id}/matching with candidate schedule activities."""
    report_id = str(uuid4())
    act1_id = str(uuid4())
    act2_id = str(uuid4())

    payload = {
        "report_id": report_id,
        "extracted_information": {
            "activity_name": "Foundation Excavation",
            "progress_percentage": 45.0,
            "discipline": "Civil",
        },
        "candidate_activities": [
            {
                "activity_id": act1_id,
                "activity_code": "ACT-101",
                "name": "Foundation Excavation & Site Prep",
                "wbs_code": "1.1",
                "discipline": "Civil",
            },
            {
                "activity_id": act2_id,
                "activity_code": "ACT-102",
                "name": "Trenching for Drainage",
                "wbs_code": "1.2",
                "discipline": "Civil",
            },
        ],
    }

    response = client.post(f"/api/v1/reports/{report_id}/matching", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == report_id
    assert data["matched_activity_id"] == act1_id
    assert data["matched_activity_code"] == "ACT-101"
    assert data["match_confidence"] == 0.85
    assert data["match_status"] == MatchStatus.AUTO_MATCHED.value
    assert len(data["alternative_candidates"]) == 1
    assert data["alternative_candidates"][0]["activity_id"] == act2_id


def test_matching_endpoint_validation_error():
    """Test invalid UUID or missing field produces 422 Unprocessable Entity."""
    response = client.post("/api/v1/reports/invalid-uuid/matching", json={})
    assert response.status_code == 422
