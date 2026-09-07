"""
Step 10 — End-to-end Integration Flow Tests.

These tests exercise the complete backend workflow in one continuous
session rather than testing individual endpoints in isolation:

  schedule import
    → field report ingestion (text + file)
    → AI extraction contract
    → AI matching contract
    → create human review
    → approve / modify review
    → create progress event
    → verify auto-created audit event
    → verify dashboard reflects live state

All data is real — produced by the services themselves.  No hardcoded
metric values are asserted; instead we verify relational invariants
(e.g. "count increased by exactly 1", "id returned is the id stored").
"""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ── CSV fixture ───────────────────────────────────────────────────────────────

VALID_CSV = (
    "Activity ID,Activity Name,WBS,Discipline,Activity Level,Planned Start,Planned End,Status\n"
    "INT-101,Foundation Excavation,1.1,Civil,L5,2026-01-01,2026-01-31,Not Started\n"
    "INT-102,Rebar Fabrication,1.2,Civil,L6,2026-02-01,2026-02-15,Not Started\n"
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def import_schedule(project_id: str | None = None) -> dict:
    files = {"file": ("schedule.csv", VALID_CSV.encode(), "text/csv")}
    data = {}
    if project_id:
        data["project_id"] = project_id
    res = client.post("/api/v1/schedules/import", files=files, data=data)
    assert res.status_code == 200, res.text
    return res.json()


def create_text_report(project_id: str, reporter: str = "SUP-INT-01") -> dict:
    res = client.post(
        "/api/v1/reports",
        json={
            "project_id": project_id,
            "source_format": "TEXT",
            "reporter_id": reporter,
            "raw_content": "Completed 50% of foundation excavation at Zone A.",
            "discipline": "Civil",
            "location": "Zone A",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()


def ai_extract(report_id: str, project_id: str) -> dict:
    res = client.post(
        f"/api/v1/reports/{report_id}/extraction",
        json={
            "report_id": report_id,
            "project_id": project_id,
            "source_format": "TEXT",
            "raw_content": "50% foundation excavation completed.",
            "metadata": {"discipline": "Civil", "location": "Zone A"},
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def ai_match(report_id: str, activity_id: str, activity_code: str) -> dict:
    res = client.post(
        f"/api/v1/reports/{report_id}/matching",
        json={
            "report_id": report_id,
            "extracted_information": {
                "activity_name": "Foundation Excavation",
                "progress_percentage": 50.0,
                "discipline": "Civil",
            },
            "candidate_activities": [
                {
                    "activity_id": activity_id,
                    "activity_code": activity_code,
                    "name": "Foundation Excavation",
                    "wbs_code": "1.1",
                    "discipline": "Civil",
                }
            ],
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def create_review(
    report_id: str,
    activity_id: str,
    confidence: float = 0.85,
    progress_pct: float = 50.0,
    project_id: str | None = None,
    discipline: str = "Civil",
) -> dict:
    res = client.post(
        "/api/v1/reviews",
        json={
            "report_id": report_id,
            "schedule_activity_id": activity_id,
            "matched_activity_code": "INT-101",
            "confidence_score": confidence,
            "extracted_progress_percentage": progress_pct,
            "extracted_status": "IN_PROGRESS",
            "discipline": discipline,
            "metadata": {"project_id": project_id} if project_id else {},
        },
    )
    assert res.status_code == 201, res.text
    return res.json()


def approve_review(review_id: str, reviewer: str = "PLANNER-INT-01") -> dict:
    res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "APPROVED", "reviewer_id": reviewer},
    )
    assert res.status_code == 200, res.text
    return res.json()


def modify_review(review_id: str, corrected_pct: float, reviewer: str = "PLANNER-INT-02") -> dict:
    res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={
            "decision": "MODIFIED",
            "reviewer_id": reviewer,
            "corrected_progress_percentage": corrected_pct,
            "comments": "Adjusted percentage based on site verification.",
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def create_progress(review_id: str, project_id: str | None = None) -> dict:
    payload: dict = {"review_id": review_id}
    if project_id:
        payload["project_id"] = project_id
    res = client.post("/api/v1/progress", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1 — Full green-path workflow
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullWorkflow:

    def test_full_workflow_schedule_to_dashboard(self):
        """
        Complete green-path: schedule import → report → AI → review →
        progress → audit → dashboard.

        Verifies that every step produces real, linked data and that the
        dashboard summary reflects the live state at the end.
        """
        project_id = str(uuid4())

        # ── Step 1: Import schedule ───────────────────────────────────────────
        schedule = import_schedule(project_id=project_id)
        assert schedule["valid_count"] == 2
        assert schedule["rejected_count"] == 0
        act = schedule["activities"][0]
        activity_id = act["id"]
        assert act["project_id"] == project_id

        # ── Step 2: Ingest field report ───────────────────────────────────────
        report = create_text_report(project_id=project_id)
        report_id = report["id"]
        assert report["project_id"] == project_id

        # ── Step 3: AI extraction contract ───────────────────────────────────
        extraction = ai_extract(report_id, project_id)
        assert extraction["report_id"] == report_id
        assert extraction["processing_status"] == "SUCCESS"
        assert extraction["extraction_confidence"] > 0.0

        # ── Step 4: AI matching contract ──────────────────────────────────────
        match = ai_match(report_id, activity_id, act["activity_code"])
        assert match["report_id"] == report_id
        assert match["matched_activity_id"] == activity_id
        assert match["match_confidence"] >= 0.80

        # ── Step 5: Create review ─────────────────────────────────────────────
        before_summary = client.get("/api/v1/dashboard/summary").json()
        assert before_summary["pending_reviews"] == 0

        review = create_review(
            report_id=report_id,
            activity_id=activity_id,
            confidence=extraction["extraction_confidence"],
            progress_pct=extraction["extracted_progress_percentage"],
            project_id=project_id,
        )
        review_id = review["id"]
        assert review["status"] == "PENDING"

        after_review = client.get("/api/v1/dashboard/summary").json()
        assert after_review["pending_reviews"] == 1

        # ── Step 6: Approve review ────────────────────────────────────────────
        approved = approve_review(review_id)
        assert approved["status"] == "APPROVED"
        assert approved["reviewer_id"] == "PLANNER-INT-01"

        after_approve = client.get("/api/v1/dashboard/summary").json()
        assert after_approve["approved_reviews"] == 1
        assert after_approve["pending_reviews"] == 0

        # ── Step 7: Create progress event ─────────────────────────────────────
        before_progress = client.get("/api/v1/dashboard/summary").json()
        assert before_progress["total_progress_events"] == 0

        progress = create_progress(review_id=review_id, project_id=project_id)
        progress_id = progress["id"]
        assert progress["review_id"] == review_id
        assert progress["progress_percentage"] == pytest.approx(
            extraction["extracted_progress_percentage"], abs=0.01
        )

        # ── Step 8: Verify audit event auto-created ───────────────────────────
        audits = client.get(f"/api/v1/audit?entity_id={progress_id}").json()
        assert len(audits) == 1
        audit = audits[0]
        assert audit["event_type"] == "PROGRESS_UPDATED"
        assert audit["entity_type"] == "ProgressEvent"
        assert audit["entity_id"] == progress_id
        assert audit["actor_id"] == "PLANNER-INT-01"

        # ── Step 9: Verify project-level dashboard ────────────────────────────
        proj_summary = client.get(f"/api/v1/dashboard/projects/{project_id}").json()
        assert proj_summary["total_progress_events"] == 1
        assert proj_summary["total_audit_logs"] == 1
        assert proj_summary["average_progress_percentage"] == pytest.approx(
            extraction["extracted_progress_percentage"], abs=0.01
        )

        # ── Step 10: Verify global dashboard summary ──────────────────────────
        final_summary = client.get("/api/v1/dashboard/summary").json()
        assert final_summary["total_progress_events"] == 1
        assert final_summary["approved_reviews"] == 1
        assert final_summary["in_progress_activities"] == 1

        # ── Step 11: Recent activity feed ─────────────────────────────────────
        feed = client.get("/api/v1/dashboard/recent-activity").json()
        kinds = {item["event_kind"] for item in feed["items"]}
        assert kinds == {"progress", "review_decision", "audit"}

        # ── Step 12: Activities list ──────────────────────────────────────────
        acts = client.get(
            f"/api/v1/dashboard/activities?project_id={project_id}&discipline=Civil"
        ).json()
        assert acts["total"] == 1
        assert acts["items"][0]["discipline"] == "Civil"

    def test_workflow_with_modified_review(self):
        """
        Modified-review path: review created → MODIFIED → progress uses
        corrected values, not AI-extracted values.
        """
        project_id = str(uuid4())
        report = create_text_report(project_id=project_id)
        activity_id = str(uuid4())

        review = create_review(
            report_id=report["id"],
            activity_id=activity_id,
            confidence=0.65,
            progress_pct=40.0,
            project_id=project_id,
        )
        review_id = review["id"]

        modify_review(review_id, corrected_pct=72.0)
        progress = create_progress(review_id=review_id, project_id=project_id)

        # MODIFIED review → corrected_progress_percentage used
        assert progress["progress_percentage"] == pytest.approx(72.0, abs=0.01)
        assert progress["review_id"] == review_id

        # Dashboard should now show 72% average for the project
        proj = client.get(f"/api/v1/dashboard/projects/{project_id}").json()
        assert proj["average_progress_percentage"] == pytest.approx(72.0, abs=0.1)

    def test_workflow_field_report_file_upload_to_review(self):
        """
        File upload path: upload a PDF → create review linked to that
        report ID → approve → progress.
        """
        project_id = str(uuid4())
        activity_id = str(uuid4())

        # Upload a file report
        pdf_bytes = b"%PDF-1.4 fake pdf content for integration test"
        files = {"file": ("site_report_int.pdf", pdf_bytes, "application/pdf")}
        form = {
            "reporter_id": "SUP-INT-FILE",
            "discipline": "Mechanical",
            "location": "Block C",
        }
        upload_res = client.post("/api/v1/reports/upload", files=files, data=form)
        assert upload_res.status_code == 201
        report = upload_res.json()
        assert report["source_format"] == "DPR"
        assert len(report["evidence"]) == 1
        report_id = report["id"]

        # Create review referencing that report
        review = create_review(
            report_id=report_id,
            activity_id=activity_id,
            confidence=0.80,
            progress_pct=60.0,
            project_id=project_id,
            discipline="Mechanical",
        )
        approve_review(review["id"])
        progress = create_progress(review["id"], project_id=project_id)

        assert progress["field_report_id"] == report_id
        assert progress["schedule_activity_id"] == activity_id

    def test_audit_trail_for_every_progress_event(self):
        """
        Each progress event creation automatically records exactly one
        audit event in AuditService with event_type=PROGRESS_UPDATED.
        """
        project_id = str(uuid4())
        progress_ids: list[str] = []

        for pct in [30.0, 60.0, 100.0]:
            report = create_text_report(project_id=project_id)
            activity_id = str(uuid4())
            review = create_review(
                report_id=report["id"],
                activity_id=activity_id,
                progress_pct=pct,
                project_id=project_id,
            )
            approve_review(review["id"])
            pe = create_progress(review["id"], project_id=project_id)
            progress_ids.append(pe["id"])

        # Each progress event must have exactly one PROGRESS_UPDATED audit entry
        for pid in progress_ids:
            audits = client.get(f"/api/v1/audit?entity_id={pid}").json()
            assert len(audits) == 1, f"Expected 1 audit for {pid}, got {len(audits)}"
            assert audits[0]["event_type"] == "PROGRESS_UPDATED"

        # Project audit total = 3
        proj_summary = client.get(f"/api/v1/dashboard/projects/{project_id}").json()
        assert proj_summary["total_audit_logs"] == 3

    def test_dashboard_reflects_live_workflow_state(self):
        """
        Dashboard summary, project summary, activities, and recent-activity
        are all consistent with each other after a multi-review workflow.
        """
        pid_a = str(uuid4())
        pid_b = str(uuid4())

        # Project A: 2 completed activities
        for _ in range(2):
            r = create_text_report(project_id=pid_a)
            rev = create_review(
                report_id=r["id"],
                activity_id=str(uuid4()),
                progress_pct=100.0,
                project_id=pid_a,
            )
            approve_review(rev["id"])
            create_progress(rev["id"], project_id=pid_a)

        # Project B: 1 in-progress activity
        r_b = create_text_report(project_id=pid_b)
        rev_b = create_review(
            report_id=r_b["id"],
            activity_id=str(uuid4()),
            progress_pct=55.0,
            project_id=pid_b,
        )
        approve_review(rev_b["id"])
        create_progress(rev_b["id"], project_id=pid_b)

        # Global summary
        summary = client.get("/api/v1/dashboard/summary").json()
        assert summary["total_progress_events"] == 3
        assert summary["completed_activities"] == 2
        assert summary["in_progress_activities"] == 1
        assert summary["approved_reviews"] == 3

        # Per-project checks
        a_summary = client.get(f"/api/v1/dashboard/projects/{pid_a}").json()
        assert a_summary["total_progress_events"] == 2
        assert a_summary["total_audit_logs"] == 2

        b_summary = client.get(f"/api/v1/dashboard/projects/{pid_b}").json()
        assert b_summary["total_progress_events"] == 1

        # Activities list — project B isolation
        b_acts = client.get(f"/api/v1/dashboard/activities?project_id={pid_b}").json()
        assert b_acts["total"] == 1
        assert b_acts["items"][0]["latest_progress_percentage"] == pytest.approx(55.0)

        # Recent activity: 3 progress + 3 review_decision + 3 audit = 9 items
        feed = client.get("/api/v1/dashboard/recent-activity?limit=100").json()
        assert feed["total"] == 9

    def test_multiple_reviews_same_report(self):
        """
        Multiple reviews can reference the same report_id.
        Each creates an independent audit trail when a progress event is created.
        """
        project_id = str(uuid4())
        report = create_text_report(project_id=project_id)
        report_id = report["id"]

        act_a = str(uuid4())
        act_b = str(uuid4())

        rev_a = create_review(report_id=report_id, activity_id=act_a, progress_pct=30.0, project_id=project_id)
        rev_b = create_review(report_id=report_id, activity_id=act_b, progress_pct=70.0, project_id=project_id)

        approve_review(rev_a["id"])
        approve_review(rev_b["id"])

        pe_a = create_progress(rev_a["id"], project_id=project_id)
        pe_b = create_progress(rev_b["id"], project_id=project_id)

        assert pe_a["field_report_id"] == report_id
        assert pe_b["field_report_id"] == report_id

        proj = client.get(f"/api/v1/dashboard/projects/{project_id}").json()
        assert proj["total_progress_events"] == 2
        assert proj["total_audit_logs"] == 2

    def test_review_get_by_id_after_decision(self):
        """
        GET /api/v1/reviews/{id} after a decision reflects the updated status
        and decision fields.
        """
        report = create_text_report(project_id=str(uuid4()))
        review = create_review(report_id=report["id"], activity_id=str(uuid4()), progress_pct=80.0)

        approve_review(review["id"])

        fetched = client.get(f"/api/v1/reviews/{review['id']}").json()
        assert fetched["status"] == "APPROVED"
        assert fetched["reviewer_id"] == "PLANNER-INT-01"
        assert fetched["decision_at"] is not None

    def test_progress_get_by_id_returns_correct_data(self):
        """
        GET /api/v1/progress/{id} returns the exact progress event created,
        with the linked review_id and field_report_id intact.
        """
        project_id = str(uuid4())
        report = create_text_report(project_id=project_id)
        activity_id = str(uuid4())
        review = create_review(report_id=report["id"], activity_id=activity_id, progress_pct=45.0)
        approve_review(review["id"])
        progress = create_progress(review["id"], project_id=project_id)

        fetched = client.get(f"/api/v1/progress/{progress['id']}").json()
        assert fetched["id"] == progress["id"]
        assert fetched["review_id"] == review["id"]
        assert fetched["field_report_id"] == report["id"]
        assert fetched["schedule_activity_id"] == activity_id
        assert fetched["progress_percentage"] == pytest.approx(45.0, abs=0.01)

    def test_list_reviews_filter_reflects_all_statuses(self):
        """
        Creating reviews and transitioning them through statuses keeps the
        list endpoint consistent.
        """
        project_id = str(uuid4())
        report_a = create_text_report(project_id=project_id)
        report_b = create_text_report(project_id=project_id)
        report_c = create_text_report(project_id=project_id)

        rev_a = create_review(report_id=report_a["id"], activity_id=str(uuid4()), progress_pct=30.0)
        rev_b = create_review(report_id=report_b["id"], activity_id=str(uuid4()), progress_pct=60.0)
        rev_c = create_review(report_id=report_c["id"], activity_id=str(uuid4()), progress_pct=90.0)

        approve_review(rev_a["id"])
        client.post(f"/api/v1/reviews/{rev_b['id']}/decision",
                    json={"decision": "REJECTED", "reviewer_id": "P1"})
        modify_review(rev_c["id"], corrected_pct=85.0)

        assert len(client.get("/api/v1/reviews").json()) == 3
        assert len(client.get("/api/v1/reviews?status=APPROVED").json()) == 1
        assert len(client.get("/api/v1/reviews?status=REJECTED").json()) == 1
        assert len(client.get("/api/v1/reviews?status=MODIFIED").json()) == 1
        assert len(client.get("/api/v1/reviews?status=PENDING").json()) == 0

    def test_progress_list_filter_by_activity_and_report(self):
        """
        GET /api/v1/progress filtered by activity_id and report_id returns
        only the matching events.
        """
        project_id = str(uuid4())
        report_x = create_text_report(project_id=project_id)
        report_y = create_text_report(project_id=project_id)
        act_x = str(uuid4())
        act_y = str(uuid4())

        rev_x = create_review(report_id=report_x["id"], activity_id=act_x, progress_pct=50.0, project_id=project_id)
        rev_y = create_review(report_id=report_y["id"], activity_id=act_y, progress_pct=75.0, project_id=project_id)
        approve_review(rev_x["id"])
        approve_review(rev_y["id"])
        pe_x = create_progress(rev_x["id"], project_id=project_id)
        pe_y = create_progress(rev_y["id"], project_id=project_id)

        # Filter by activity_id
        act_filter = client.get(f"/api/v1/progress?activity_id={act_x}").json()
        assert len(act_filter) == 1
        assert act_filter[0]["id"] == pe_x["id"]

        # Filter by report_id
        rep_filter = client.get(f"/api/v1/progress?report_id={report_y['id']}").json()
        assert len(rep_filter) == 1
        assert rep_filter[0]["id"] == pe_y["id"]

    def test_audit_filter_by_entity_type(self):
        """
        GET /api/v1/audit?entity_type=ProgressEvent returns only
        ProgressEvent audit entries.
        """
        project_id = str(uuid4())
        report = create_text_report(project_id=project_id)
        review = create_review(report_id=report["id"], activity_id=str(uuid4()), progress_pct=50.0)
        approve_review(review["id"])
        pe = create_progress(review["id"], project_id=project_id)

        all_audits = client.get("/api/v1/audit").json()
        filtered = client.get("/api/v1/audit?entity_type=ProgressEvent").json()

        assert len(filtered) == 1
        assert filtered[0]["entity_type"] == "ProgressEvent"
        assert filtered[0]["entity_id"] == pe["id"]
