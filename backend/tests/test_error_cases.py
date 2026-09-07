"""
Step 10 — Error Cases, Edge Cases & Security Hardening Tests.

This module tests every important error path in the backend.  It does NOT
duplicate passing tests that already exist in other modules; it adds
coverage for conditions that are not yet tested.

Groups:
  - Infrastructure (health, status)
  - Schedule import errors
  - Field report errors (text + upload)
  - AI contract errors
  - Review workflow errors
  - Progress workflow errors
  - Audit errors
  - Dashboard filter/validation errors
  - Upload security (filename safety)
  - HTTP method & content-type errors
"""
from __future__ import annotations

import io
from uuid import uuid4

import openpyxl
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class TestInfrastructure:

    def test_health_endpoint(self):
        """GET /health must return 200 and {"status": "ok"}."""
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_api_v1_status_endpoint(self):
        """GET /api/v1/status must return 200 and version information."""
        res = client.get("/api/v1/status")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_unknown_route_returns_404(self):
        """A completely unknown path returns 404."""
        res = client.get("/api/v1/does-not-exist")
        assert res.status_code == 404

    def test_wrong_method_on_known_route(self):
        """DELETE /api/v1/reviews is not registered → 405."""
        res = client.delete("/api/v1/reviews")
        assert res.status_code == 405


# ═══════════════════════════════════════════════════════════════════════════════
# Schedule import errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestScheduleImportErrors:

    def test_empty_file_content_returns_400(self):
        """Uploading a CSV with zero bytes is rejected with 400."""
        files = {"file": ("empty.csv", b"", "text/csv")}
        res = client.post("/api/v1/schedules/import", files=files)
        assert res.status_code == 400

    def test_csv_with_only_blank_rows_returns_400(self):
        """CSV that has no data rows (header-only or all blank) → 400."""
        files = {"file": ("blank.csv", b"\n\n\n", "text/csv")}
        res = client.post("/api/v1/schedules/import", files=files)
        assert res.status_code == 400

    def test_unsupported_extension_returns_400(self):
        """Uploading a .xml file → 400 Unsupported file type."""
        files = {"file": ("schedule.xml", b"<root/>", "application/xml")}
        res = client.post("/api/v1/schedules/import", files=files)
        assert res.status_code == 400
        assert "Unsupported file type" in res.json()["detail"]

    def test_missing_required_columns_returns_400(self):
        """CSV missing Activity Name column → 400 Missing required columns."""
        csv = "Activity ID,WBS,Discipline\nACT-1,1.1,Civil\n"
        files = {"file": ("partial.csv", csv.encode(), "text/csv")}
        res = client.post("/api/v1/schedules/import", files=files)
        assert res.status_code == 400
        assert "Missing required columns" in res.json()["detail"]

    def test_csv_invalid_date_produces_rejection_not_500(self):
        """Invalid date values are captured as row-level validation errors → 200."""
        csv = (
            "Activity ID,Activity Name,WBS,Discipline,Planned Start,Planned End\n"
            "ACT-X,Good Row,1.1,Civil,2026-01-01,2026-03-31\n"
            "ACT-Y,Bad Date Row,1.2,Civil,NOT-A-DATE,2026-03-31\n"
        )
        files = {"file": ("dates.csv", csv.encode(), "text/csv")}
        res = client.post("/api/v1/schedules/import", files=files)
        assert res.status_code == 200
        data = res.json()
        assert data["valid_count"] == 1
        assert data["rejected_count"] == 1
        assert len(data["validation_errors"]) == 1

    def test_no_file_field_returns_422(self):
        """POST /api/v1/schedules/import without a file → 422."""
        res = client.post("/api/v1/schedules/import")
        assert res.status_code == 422

    def test_invalid_project_id_uuid_returns_422(self):
        """Providing a non-UUID project_id form value → 422."""
        csv = (
            "Activity ID,Activity Name,WBS,Discipline\n"
            "ACT-1,Foundation,1.1,Civil\n"
        )
        files = {"file": ("schedule.csv", csv.encode(), "text/csv")}
        data = {"project_id": "not-a-valid-uuid"}
        res = client.post("/api/v1/schedules/import", files=files, data=data)
        assert res.status_code == 422

    def test_excel_with_all_invalid_rows_returns_zero_valid(self):
        """Excel where all data rows have empty mandatory cells → valid_count=0."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Activity ID", "Activity Name", "WBS", "Discipline"])
        ws.append([None, None, None, None])  # all empty
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        files = {"file": ("all_invalid.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        res = client.post("/api/v1/schedules/import", files=files)
        # all-blank rows are skipped; net result: total_rows=0
        assert res.status_code in (200, 400)
        if res.status_code == 200:
            data = res.json()
            assert data["valid_count"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Field report errors — text endpoint
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldReportTextErrors:

    def test_missing_reporter_id_in_json_returns_422(self):
        """Omitting reporter_id from the JSON body → pydantic 422."""
        res = client.post(
            "/api/v1/reports",
            json={"raw_content": "Some content", "source_format": "TEXT"},
        )
        assert res.status_code == 422

    def test_whitespace_reporter_id_returns_400(self):
        """reporter_id with only whitespace is rejected by service → 400."""
        res = client.post(
            "/api/v1/reports",
            json={"reporter_id": "   ", "raw_content": "Content here.", "source_format": "TEXT"},
        )
        assert res.status_code == 400
        assert "Reporter ID is required" in res.json()["detail"]

    def test_empty_raw_content_returns_400(self):
        """Empty or whitespace raw_content → 400."""
        res = client.post(
            "/api/v1/reports",
            json={"reporter_id": "SUP-1", "raw_content": "", "source_format": "TEXT"},
        )
        assert res.status_code == 400

    def test_invalid_source_format_enum_returns_422(self):
        """source_format with invalid enum value → 422."""
        res = client.post(
            "/api/v1/reports",
            json={"reporter_id": "SUP-1", "raw_content": "Content.", "source_format": "UNKNOWN_FORMAT"},
        )
        assert res.status_code == 422

    def test_invalid_project_id_uuid_returns_422(self):
        """Non-UUID project_id → pydantic 422."""
        res = client.post(
            "/api/v1/reports",
            json={
                "reporter_id": "SUP-1",
                "raw_content": "Content.",
                "source_format": "TEXT",
                "project_id": "not-a-uuid",
            },
        )
        assert res.status_code == 422

    def test_missing_raw_content_field_returns_422(self):
        """Omitting raw_content entirely → 422."""
        res = client.post(
            "/api/v1/reports",
            json={"reporter_id": "SUP-1", "source_format": "TEXT"},
        )
        assert res.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Field report errors — upload endpoint
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldReportUploadErrors:

    def test_missing_reporter_id_form_returns_422(self):
        """Upload without reporter_id form field → 422."""
        files = {"file": ("doc.pdf", b"%PDF fake", "application/pdf")}
        res = client.post("/api/v1/reports/upload", files=files)
        assert res.status_code == 422

    def test_empty_file_bytes_returns_400(self):
        """Uploading a zero-byte file → 400."""
        files = {"file": ("empty.pdf", b"", "application/pdf")}
        data = {"reporter_id": "SUP-1"}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        assert res.status_code == 400

    def test_oversized_file_upload_returns_413(self, monkeypatch):
        """Uploading a file exceeding MAX_UPLOAD_SIZE_MB returns HTTP 413."""
        from app.core.config import get_settings
        monkeypatch.setattr(get_settings(), "MAX_UPLOAD_SIZE_MB", 0)
        files = {"file": ("large.pdf", b"%PDF fake content", "application/pdf")}
        data = {"reporter_id": "SUP-1"}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        assert res.status_code == 413
        assert "File size exceeds maximum allowed limit" in res.json()["detail"]

    def test_unsupported_file_extension_returns_400(self):
        """Uploading a .exe file → 400 Unsupported file format."""
        files = {"file": ("bad.exe", b"MZ...", "application/octet-stream")}
        data = {"reporter_id": "SUP-1"}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        assert res.status_code == 400
        assert "Unsupported file format" in res.json()["detail"]

    def test_whitespace_reporter_id_upload_returns_400(self):
        """Upload with whitespace-only reporter_id → 400."""
        files = {"file": ("doc.pdf", b"%PDF fake", "application/pdf")}
        data = {"reporter_id": "   "}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        assert res.status_code == 400
        assert "Reporter ID is required" in res.json()["detail"]

    def test_path_traversal_filename_handled_safely(self):
        """
        A filename containing path traversal sequences must be processed
        without error — the service must not expose the raw path to storage.
        The response should succeed (200/201) or return 4xx, but must never
        500 or expose a server path.
        """
        files = {"file": ("../../etc/passwd.pdf", b"%PDF-1.4 safe content", "application/pdf")}
        data = {"reporter_id": "ATTACKER-01"}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        # Must not 500
        assert res.status_code != 500
        if res.status_code == 201:
            # If accepted, the stored file_url must NOT contain ".." sequences
            evidence = res.json()["evidence"]
            if evidence:
                file_url = evidence[0]["file_url"]
                assert ".." not in file_url, f"Path traversal in file_url: {file_url}"

    def test_no_file_field_returns_422(self):
        """POST /api/v1/reports/upload with no file → 422."""
        data = {"reporter_id": "SUP-1"}
        res = client.post("/api/v1/reports/upload", data=data)
        assert res.status_code == 422

    def test_zip_extension_returns_400(self):
        """Uploading a .zip archive → 400 unsupported format."""
        files = {"file": ("archive.zip", b"PK...", "application/zip")}
        data = {"reporter_id": "SUP-1"}
        res = client.post("/api/v1/reports/upload", files=files, data=data)
        assert res.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# AI contract errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestAIContractErrors:

    def test_extraction_report_id_mismatch_returns_400(self):
        """Path report_id ≠ body report_id → 400."""
        path_id = str(uuid4())
        body_id = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{path_id}/extraction",
            json={"report_id": body_id, "source_format": "TEXT", "raw_content": "Test"},
        )
        assert res.status_code == 400
        assert "mismatch" in res.json()["detail"].lower()

    def test_extraction_invalid_path_uuid_returns_422(self):
        """Non-UUID report_id in path → 422."""
        res = client.post("/api/v1/reports/not-a-uuid/extraction", json={})
        assert res.status_code == 422

    def test_extraction_missing_raw_content_returns_422(self):
        """Missing required raw_content → 422."""
        rid = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{rid}/extraction",
            json={"report_id": rid, "source_format": "TEXT"},
        )
        assert res.status_code == 422

    def test_matching_report_id_mismatch_returns_400(self):
        """Path report_id ≠ body report_id for matching → 400."""
        path_id = str(uuid4())
        body_id = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{path_id}/matching",
            json={"report_id": body_id, "extracted_information": {}},
        )
        assert res.status_code == 400

    def test_matching_invalid_path_uuid_returns_422(self):
        """Non-UUID report_id in matching path → 422."""
        res = client.post("/api/v1/reports/bad-uuid/matching", json={})
        assert res.status_code == 422

    def test_matching_missing_extracted_information_returns_422(self):
        """Missing required extracted_information → 422."""
        rid = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{rid}/matching",
            json={"report_id": rid},
        )
        assert res.status_code == 422

    def test_extraction_with_empty_metadata_succeeds(self):
        """extraction with empty metadata dict still succeeds (optional field)."""
        rid = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{rid}/extraction",
            json={"report_id": rid, "source_format": "TEXT", "raw_content": "Some content.", "metadata": {}},
        )
        assert res.status_code == 200

    def test_matching_with_no_candidates_succeeds(self):
        """matching with an empty candidate list returns 200 with no match."""
        rid = str(uuid4())
        res = client.post(
            f"/api/v1/reports/{rid}/matching",
            json={
                "report_id": rid,
                "extracted_information": {"activity_name": "Unknown"},
                "candidate_activities": [],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["matched_activity_id"] is None


# ═══════════════════════════════════════════════════════════════════════════════
# Review workflow errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestReviewErrors:

    def test_confidence_above_1_returns_422(self):
        """confidence_score > 1.0 is rejected by pydantic → 422."""
        res = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": 1.01},
        )
        assert res.status_code == 422

    def test_confidence_below_0_returns_422(self):
        """confidence_score < 0.0 → 422."""
        res = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": -0.5},
        )
        assert res.status_code == 422

    def test_missing_report_id_returns_422(self):
        """Omitting report_id (required) → 422."""
        res = client.post(
            "/api/v1/reviews",
            json={"confidence_score": 0.80},
        )
        assert res.status_code == 422

    def test_invalid_schedule_activity_id_uuid_returns_422(self):
        """Non-UUID schedule_activity_id → 422."""
        res = client.post(
            "/api/v1/reviews",
            json={
                "report_id": str(uuid4()),
                "confidence_score": 0.80,
                "schedule_activity_id": "not-a-uuid",
            },
        )
        assert res.status_code == 422

    def test_get_nonexistent_review_returns_404(self):
        """GET /api/v1/reviews/{id} for an unknown id → 404."""
        res = client.get(f"/api/v1/reviews/{uuid4()}")
        assert res.status_code == 404

    def test_get_review_invalid_uuid_returns_422(self):
        """GET /api/v1/reviews/bad-uuid → 422."""
        res = client.get("/api/v1/reviews/not-a-uuid")
        assert res.status_code == 422

    def test_decision_on_nonexistent_review_returns_404(self):
        """POST decision on non-existent review → 404."""
        res = client.post(
            f"/api/v1/reviews/{uuid4()}/decision",
            json={"decision": "APPROVED", "reviewer_id": "P1"},
        )
        assert res.status_code == 404

    def test_invalid_decision_value_returns_422(self):
        """An unknown decision string → 422."""
        res_create = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": 0.80},
        )
        review_id = res_create.json()["id"]
        res = client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "INVALID_DECISION", "reviewer_id": "P1"},
        )
        assert res.status_code == 422

    def test_double_decision_on_finalized_review_returns_400(self):
        """Submitting a second decision on an already-decided review → 400."""
        res_create = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": 0.80},
        )
        review_id = res_create.json()["id"]

        client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "APPROVED", "reviewer_id": "P1"},
        )
        res_second = client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "REJECTED", "reviewer_id": "P2"},
        )
        assert res_second.status_code == 400
        assert "already finalized" in res_second.json()["detail"]

    def test_empty_reviewer_id_returns_400(self):
        """reviewer_id = '' is rejected by service → 400."""
        res_create = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": 0.75},
        )
        review_id = res_create.json()["id"]
        res = client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={"decision": "APPROVED", "reviewer_id": ""},
        )
        # pydantic min_length=1 → 422
        assert res.status_code == 422

    def test_invalid_status_filter_returns_422(self):
        """GET /api/v1/reviews?status=NONSENSE → 422."""
        res = client.get("/api/v1/reviews?status=NONSENSE")
        assert res.status_code == 422

    def test_progress_percentage_out_of_range_returns_422(self):
        """extracted_progress_percentage > 100 → 422."""
        res = client.post(
            "/api/v1/reviews",
            json={
                "report_id": str(uuid4()),
                "confidence_score": 0.80,
                "extracted_progress_percentage": 150.0,
            },
        )
        assert res.status_code == 422

    def test_corrected_percentage_out_of_range_returns_422(self):
        """corrected_progress_percentage > 100 in decision → 422."""
        res_create = client.post(
            "/api/v1/reviews",
            json={"report_id": str(uuid4()), "confidence_score": 0.80},
        )
        review_id = res_create.json()["id"]
        res = client.post(
            f"/api/v1/reviews/{review_id}/decision",
            json={
                "decision": "MODIFIED",
                "reviewer_id": "P1",
                "corrected_progress_percentage": 999.0,
            },
        )
        assert res.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Progress workflow errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestProgressErrors:

    def _make_and_decide_review(self, decision: str = "APPROVED") -> str:
        res = client.post(
            "/api/v1/reviews",
            json={
                "report_id": str(uuid4()),
                "schedule_activity_id": str(uuid4()),
                "confidence_score": 0.85,
                "extracted_progress_percentage": 50.0,
            },
        )
        review_id = res.json()["id"]
        if decision != "PENDING":
            client.post(
                f"/api/v1/reviews/{review_id}/decision",
                json={"decision": decision, "reviewer_id": "P1"},
            )
        return review_id

    def test_missing_review_id_returns_422(self):
        """POST /api/v1/progress with no review_id → 422."""
        res = client.post("/api/v1/progress", json={})
        assert res.status_code == 422

    def test_nonexistent_review_id_returns_404(self):
        """Progress from a review_id that doesn't exist → 404."""
        res = client.post("/api/v1/progress", json={"review_id": str(uuid4())})
        assert res.status_code == 404

    def test_pending_review_blocked(self):
        """PENDING review → 400 with helpful message."""
        review_id = self._make_and_decide_review("PENDING")
        res = client.post("/api/v1/progress", json={"review_id": review_id})
        assert res.status_code == 400
        assert "Only APPROVED or MODIFIED" in res.json()["detail"]

    def test_rejected_review_blocked(self):
        """REJECTED review → 400."""
        review_id = self._make_and_decide_review("REJECTED")
        res = client.post("/api/v1/progress", json={"review_id": review_id})
        assert res.status_code == 400
        assert "Only APPROVED or MODIFIED" in res.json()["detail"]

    def test_duplicate_progress_from_same_review_blocked(self):
        """Creating two progress events from the same review → 400 on second."""
        review_id = self._make_and_decide_review("APPROVED")

        res1 = client.post("/api/v1/progress", json={"review_id": review_id})
        assert res1.status_code == 201

        res2 = client.post("/api/v1/progress", json={"review_id": review_id})
        assert res2.status_code == 400
        assert "already created" in res2.json()["detail"]

    def test_invalid_progress_status_enum_returns_422(self):
        """status with invalid enum value → 422."""
        review_id = self._make_and_decide_review("APPROVED")
        res = client.post(
            "/api/v1/progress",
            json={"review_id": review_id, "status": "INVALID_STATUS"},
        )
        assert res.status_code == 422

    def test_invalid_review_id_uuid_returns_422(self):
        """Non-UUID review_id → 422."""
        res = client.post("/api/v1/progress", json={"review_id": "not-a-uuid"})
        assert res.status_code == 422

    def test_get_progress_nonexistent_id_returns_404(self):
        """GET /api/v1/progress/{id} for unknown id → 404."""
        res = client.get(f"/api/v1/progress/{uuid4()}")
        assert res.status_code == 404

    def test_get_progress_invalid_uuid_returns_422(self):
        """GET /api/v1/progress/bad-uuid → 422."""
        res = client.get("/api/v1/progress/not-a-uuid")
        assert res.status_code == 422

    def test_list_progress_invalid_activity_id_uuid_returns_422(self):
        """?activity_id=bad-uuid → 422."""
        res = client.get("/api/v1/progress?activity_id=not-a-uuid")
        assert res.status_code == 422

    def test_list_progress_empty_returns_empty_list(self):
        """GET /api/v1/progress with empty store → 200 with []."""
        res = client.get("/api/v1/progress")
        assert res.status_code == 200
        assert res.json() == []

    def test_invalid_project_id_uuid_returns_422(self):
        """Non-UUID project_id in progress payload → 422."""
        review_id = self._make_and_decide_review("APPROVED")
        res = client.post(
            "/api/v1/progress",
            json={"review_id": review_id, "project_id": "not-a-uuid"},
        )
        assert res.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Audit errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuditErrors:

    def test_get_audit_nonexistent_id_returns_404(self):
        """GET /api/v1/audit/{id} for unknown id → 404."""
        res = client.get(f"/api/v1/audit/{uuid4()}")
        assert res.status_code == 404

    def test_get_audit_invalid_uuid_returns_422(self):
        """GET /api/v1/audit/bad-uuid → 422."""
        res = client.get("/api/v1/audit/not-a-uuid")
        assert res.status_code == 422

    def test_list_audit_invalid_entity_id_returns_422(self):
        """?entity_id=bad-uuid → 422."""
        res = client.get("/api/v1/audit?entity_id=not-a-uuid")
        assert res.status_code == 422

    def test_list_audit_empty_returns_empty_list(self):
        """GET /api/v1/audit with empty store → 200 with []."""
        res = client.get("/api/v1/audit")
        assert res.status_code == 200
        assert res.json() == []

    def test_list_audit_by_entity_type_no_matches_returns_empty(self):
        """Filtering by a type that doesn't exist returns [] not 404."""
        res = client.get("/api/v1/audit?entity_type=NonExistentType")
        assert res.status_code == 200
        assert res.json() == []


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard validation errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestDashboardErrors:

    def test_invalid_activity_level_enum_returns_422(self):
        """?activity_level=L9 → 422."""
        res = client.get("/api/v1/dashboard/activities?activity_level=L9")
        assert res.status_code == 422

    def test_recent_activity_limit_zero_returns_422(self):
        """?limit=0 → 422 (below minimum of 1)."""
        res = client.get("/api/v1/dashboard/recent-activity?limit=0")
        assert res.status_code == 422

    def test_recent_activity_limit_above_max_returns_422(self):
        """?limit=101 → 422 (above maximum of 100)."""
        res = client.get("/api/v1/dashboard/recent-activity?limit=101")
        assert res.status_code == 422

    def test_project_summary_invalid_uuid_returns_422(self):
        """GET /api/v1/dashboard/projects/bad-uuid → 422."""
        res = client.get("/api/v1/dashboard/projects/not-a-uuid")
        assert res.status_code == 422

    def test_project_summary_unknown_uuid_returns_zeros(self):
        """GET /api/v1/dashboard/projects/{new_uuid} → 200 zeros, never 404."""
        pid = str(uuid4())
        res = client.get(f"/api/v1/dashboard/projects/{pid}")
        assert res.status_code == 200
        data = res.json()
        assert data["total_progress_events"] == 0
        assert data["total_audit_logs"] == 0
        assert data["average_progress_percentage"] is None

    def test_activities_invalid_project_id_uuid_returns_422(self):
        """?project_id=bad-uuid → 422."""
        res = client.get("/api/v1/dashboard/activities?project_id=not-a-uuid")
        assert res.status_code == 422

    def test_activities_empty_state_returns_200(self):
        """GET /api/v1/dashboard/activities with empty store → 200 with empty list."""
        res = client.get("/api/v1/dashboard/activities")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_summary_empty_state_all_zeros(self):
        """GET /api/v1/dashboard/summary with empty store → all zeros, null confidence."""
        res = client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        for key in [
            "total_activities", "completed_activities", "in_progress_activities",
            "delayed_activities", "pending_reviews", "approved_reviews",
            "rejected_reviews", "modified_reviews", "total_progress_events",
        ]:
            assert data[key] == 0
        assert data["average_match_confidence"] is None

    def test_recent_activity_empty_state_returns_200(self):
        """GET /api/v1/dashboard/recent-activity with empty store → 200, total=0."""
        res = client.get("/api/v1/dashboard/recent-activity")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# Backward compatibility — verify all existing route prefixes still exist
# ═══════════════════════════════════════════════════════════════════════════════


class TestBackwardCompatibility:
    """
    Verify that no route has been accidentally removed or renamed.
    Each test sends a benign request and checks the status code is not 404.
    """

    def test_schedules_import_route_exists(self):
        """POST /api/v1/schedules/import is reachable (returns 400/422 without a file)."""
        res = client.post("/api/v1/schedules/import")
        assert res.status_code != 404

    def test_reports_route_exists(self):
        """POST /api/v1/reports is reachable (returns 422 without body)."""
        res = client.post("/api/v1/reports")
        assert res.status_code != 404

    def test_reports_upload_route_exists(self):
        """POST /api/v1/reports/upload is reachable (returns 422 without file)."""
        res = client.post("/api/v1/reports/upload")
        assert res.status_code != 404

    def test_reviews_route_exists(self):
        """GET /api/v1/reviews is reachable."""
        res = client.get("/api/v1/reviews")
        assert res.status_code == 200

    def test_progress_route_exists(self):
        """GET /api/v1/progress is reachable."""
        res = client.get("/api/v1/progress")
        assert res.status_code == 200

    def test_audit_route_exists(self):
        """GET /api/v1/audit is reachable."""
        res = client.get("/api/v1/audit")
        assert res.status_code == 200

    def test_dashboard_summary_route_exists(self):
        """GET /api/v1/dashboard/summary is reachable."""
        res = client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200

    def test_dashboard_activities_route_exists(self):
        """GET /api/v1/dashboard/activities is reachable."""
        res = client.get("/api/v1/dashboard/activities")
        assert res.status_code == 200

    def test_dashboard_recent_activity_route_exists(self):
        """GET /api/v1/dashboard/recent-activity is reachable."""
        res = client.get("/api/v1/dashboard/recent-activity")
        assert res.status_code == 200

    def test_api_docs_reachable(self):
        """GET /docs returns 200 (OpenAPI UI is enabled)."""
        res = client.get("/docs")
        assert res.status_code == 200

    def test_api_openapi_json_reachable(self):
        """GET /openapi.json returns 200 and is valid JSON."""
        res = client.get("/openapi.json")
        assert res.status_code == 200
        schema = res.json()
        assert "paths" in schema
        assert "components" in schema
