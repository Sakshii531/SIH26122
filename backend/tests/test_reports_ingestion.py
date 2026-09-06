from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import FieldReportFormat

client = TestClient(app)


def test_create_text_report_success():
    """Test creating a valid structured text field report via POST /api/v1/reports."""
    project_id = str(uuid4())
    payload = {
        "project_id": project_id,
        "source_format": "TEXT",
        "reporter_id": "SUP-101",
        "raw_content": "Completed foundation excavation for Section 3.",
        "discipline": "Civil",
        "location": "Sector 4",
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reporter_id"] == "SUP-101"
    assert data["raw_content"] == "Completed foundation excavation for Section 3."
    assert data["discipline"] == "Civil"
    assert data["project_id"] == project_id
    assert data["source_format"] == "TEXT"
    assert "id" in data
    assert "created_at" in data


def test_create_text_report_missing_fields():
    """Test text report creation with empty reporter_id or empty raw_content returns 400."""
    project_id = str(uuid4())
    # Missing reporter_id
    payload1 = {
        "project_id": project_id,
        "source_format": "TEXT",
        "reporter_id": "   ",
        "raw_content": "Valid content",
    }
    r1 = client.post("/api/v1/reports", json=payload1)
    assert r1.status_code == 400
    assert "Reporter ID is required" in r1.json()["detail"]

    # Empty raw_content
    payload2 = {
        "project_id": project_id,
        "source_format": "TEXT",
        "reporter_id": "SUP-101",
        "raw_content": "   ",
    }
    r2 = client.post("/api/v1/reports", json=payload2)
    assert r2.status_code == 400
    assert "Report text content cannot be empty" in r2.json()["detail"]


def test_upload_report_pdf_success():
    """Test uploading a PDF document report via POST /api/v1/reports/upload."""
    pdf_content = b"%PDF-1.4 Fake PDF Content"
    files = {"file": ("dpr_march10.pdf", pdf_content, "application/pdf")}
    data = {
        "reporter_id": "SUP-202",
        "discipline": "Civil",
        "location": "Site B",
    }
    response = client.post("/api/v1/reports/upload", files=files, data=data)
    assert response.status_code == 201
    res = response.json()
    assert res["reporter_id"] == "SUP-202"
    assert res["source_format"] == "DPR"
    assert len(res["evidence"]) == 1
    assert res["evidence"][0]["file_name"] == "dpr_march10.pdf"
    assert "dpr_march10.pdf" in res["raw_content"]


def test_upload_report_audio_success():
    """Test uploading a voice audio report via POST /api/v1/reports/upload."""
    audio_content = b"RIFF....WAVEfmt ....data...."
    files = {"file": ("voice_update.wav", audio_content, "audio/wav")}
    data = {
        "reporter_id": "SUP-303",
        "discipline": "Electrical",
    }
    response = client.post("/api/v1/reports/upload", files=files, data=data)
    assert response.status_code == 201
    res = response.json()
    assert res["reporter_id"] == "SUP-303"
    assert res["source_format"] == "VOICE"
    assert len(res["evidence"]) == 1
    assert res["evidence"][0]["file_name"] == "voice_update.wav"


def test_upload_report_photo_success():
    """Test uploading a photo/image report via POST /api/v1/reports/upload."""
    image_content = b"\xFF\xD8\xFF\xE0\x00\x10JFIF Fake JPEG Bytes"
    files = {"file": ("site_progress.jpg", image_content, "image/jpeg")}
    data = {
        "reporter_id": "SUP-404",
        "discipline": "Civil",
        "location": "Zone 2",
    }
    response = client.post("/api/v1/reports/upload", files=files, data=data)
    assert response.status_code == 201
    res = response.json()
    assert res["reporter_id"] == "SUP-404"
    assert res["source_format"] == "PHOTO"
    assert len(res["evidence"]) == 1
    assert res["evidence"][0]["file_name"] == "site_progress.jpg"
    assert res["evidence"][0]["mime_type"] == "image/jpeg"


def test_upload_report_unsupported_format():
    """Test uploading an unsupported executable or archive file format returns 400."""
    files = {"file": ("malicious.exe", b"MZ......", "application/octet-stream")}
    data = {"reporter_id": "SUP-999"}
    response = client.post("/api/v1/reports/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
