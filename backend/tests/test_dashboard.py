from __future__ import annotations

"""
Step 9 — Dashboard & Reporting API tests.

Proves the dashboard is a true read-only reporting layer over existing
in-memory stores from Steps 1–8.  No hardcoded / mock values are used.

Coverage:
  GET /api/v1/dashboard/summary
    - empty-state (all zeros, null confidence)
    - counts after reviews + progress + audit data
    - average_match_confidence calculation
    - creating reviews/progress changes metrics (Requirement 1)

  GET /api/v1/dashboard/projects/{project_id}
    - empty project (zero events)
    - project with progress events (avg %, audit count)
    - project isolation (events from other project not counted)

  GET /api/v1/dashboard/activities
    - empty-state
    - returns items after progress events
    - filter by project_id
    - filter by status
    - filter by discipline
    - activity_level filter yields empty (no persistent activity store yet)
    - multiple filters combined
    - only matching real data returned (Requirement 2)

  GET /api/v1/dashboard/recent-activity
    - empty-state
    - default limit returns merged feed
    - feed includes progress / review_decision / audit event_kinds
    - custom limit respected
    - limit=1 returns single newest item
    - invalid limit (0, 101) returns 422
    - contains actual workflow events (Requirement 3)
    - empty state returns zeros/empty lists (Requirement 4)

  No-hardcoded-values guard (Requirement 5)
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.audit_service import AuditService
from app.services.progress_workflow_service import ProgressWorkflowService
from app.services.review_workflow_service import ReviewWorkflowService

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_all_stores():
    """Wipe every in-memory store before each test for full isolation."""
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()
    yield
    ReviewWorkflowService.clear_db()
    ProgressWorkflowService.clear_db()
    AuditService.clear_db()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_review(
    *,
    confidence: float = 0.80,
    progress_pct: float = 50.0,
    discipline: str | None = "Civil",
    project_id: str | None = None,
) -> dict:
    """Create a PENDING review item and return the response JSON."""
    payload: dict = {
        "report_id": str(uuid4()),
        "schedule_activity_id": str(uuid4()),
        "confidence_score": confidence,
        "extracted_progress_percentage": progress_pct,
        "extracted_status": "IN_PROGRESS",
        "discipline": discipline,
        "metadata": {},
    }
    if project_id:
        payload["metadata"] = {"project_id": project_id}
    res = client.post("/api/v1/reviews", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def _approve_review(review_id: str, reviewer: str = "PLANNER-01") -> dict:
    res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "APPROVED", "reviewer_id": reviewer},
    )
    assert res.status_code == 200, res.text
    return res.json()


def _reject_review(review_id: str) -> dict:
    res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={"decision": "REJECTED", "reviewer_id": "PLANNER-01"},
    )
    assert res.status_code == 200, res.text
    return res.json()


def _modify_review(review_id: str, corrected_pct: float = 75.0) -> dict:
    res = client.post(
        f"/api/v1/reviews/{review_id}/decision",
        json={
            "decision": "MODIFIED",
            "reviewer_id": "PLANNER-01",
            "corrected_progress_percentage": corrected_pct,
        },
    )
    assert res.status_code == 200, res.text
    return res.json()


def _create_progress(review_id: str, project_id: str | None = None) -> dict:
    payload: dict = {"review_id": review_id}
    if project_id:
        payload["project_id"] = project_id
    res = client.post("/api/v1/progress", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dashboard/summary
# ═══════════════════════════════════════════════════════════════════════════════


class TestDashboardSummary:

    def test_empty_state(self):
        """All counters zero, average_match_confidence null when stores are empty.
        Requirement 4: empty datasets return valid zero/empty responses.
        """
        res = client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_activities"] == 0
        assert data["completed_activities"] == 0
        assert data["in_progress_activities"] == 0
        assert data["delayed_activities"] == 0
        assert data["pending_reviews"] == 0
        assert data["approved_reviews"] == 0
        assert data["rejected_reviews"] == 0
        assert data["modified_reviews"] == 0
        assert data["total_progress_events"] == 0
        assert data["average_match_confidence"] is None

    def test_review_counts_reflected(self):
        """Summary reflects correct PENDING / APPROVED / REJECTED / MODIFIED counts.
        Requirement 1: creating reviews changes dashboard metrics.
        """
        r1 = _make_review(confidence=0.9)
        r2 = _make_review(confidence=0.7)
        r3 = _make_review(confidence=0.5)
        r4 = _make_review(confidence=0.6)

        _approve_review(r1["id"])
        _reject_review(r2["id"])
        _modify_review(r3["id"])
        # r4 stays PENDING

        res = client.get("/api/v1/dashboard/summary")
        data = res.json()

        assert data["approved_reviews"] == 1
        assert data["rejected_reviews"] == 1
        assert data["modified_reviews"] == 1
        assert data["pending_reviews"] == 1

    def test_creating_reviews_changes_metrics(self):
        """Requirement 1: Creating reviews changes dashboard metrics in real-time.
        Metrics before and after review creation must differ.
        """
        before = client.get("/api/v1/dashboard/summary").json()
        assert before["pending_reviews"] == 0
        assert before["average_match_confidence"] is None

        _make_review(confidence=0.80)
        after_one = client.get("/api/v1/dashboard/summary").json()
        assert after_one["pending_reviews"] == 1
        assert after_one["average_match_confidence"] == pytest.approx(0.80, abs=1e-3)

        _make_review(confidence=0.60)
        after_two = client.get("/api/v1/dashboard/summary").json()
        assert after_two["pending_reviews"] == 2
        assert after_two["average_match_confidence"] == pytest.approx(0.70, abs=1e-3)

    def test_creating_progress_changes_metrics(self):
        """Requirement 1: Creating progress events changes total_progress_events.
        Before creating progress, total_progress_events is 0.
        After, it must reflect the real count.
        """
        before = client.get("/api/v1/dashboard/summary").json()
        assert before["total_progress_events"] == 0
        assert before["total_activities"] == 0

        r = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        after = client.get("/api/v1/dashboard/summary").json()
        assert after["total_progress_events"] == 1
        assert after["total_activities"] == 1
        assert after["in_progress_activities"] == 1

    def test_average_confidence_calculation(self):
        """Average confidence is the mean of all review items' confidence_score."""
        _make_review(confidence=0.80)
        _make_review(confidence=0.60)

        res = client.get("/api/v1/dashboard/summary")
        data = res.json()
        # Mean of 0.80 and 0.60 = 0.70
        assert data["average_match_confidence"] == pytest.approx(0.70, abs=1e-3)

    def test_progress_event_count(self):
        """total_progress_events increments when progress events are created."""
        r1 = _make_review(confidence=0.85)
        _approve_review(r1["id"])
        _create_progress(r1["id"])

        r2 = _make_review(confidence=0.75)
        _approve_review(r2["id"])
        _create_progress(r2["id"])

        res = client.get("/api/v1/dashboard/summary")
        data = res.json()
        assert data["total_progress_events"] == 2

    def test_activity_counts_from_progress_events(self):
        """total_activities counts unique activities; in_progress when 0 < pct < 100."""
        # Create two distinct activities via approved reviews at 50%
        r1 = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r1["id"])
        _create_progress(r1["id"])

        r2 = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r2["id"])
        _create_progress(r2["id"])

        res = client.get("/api/v1/dashboard/summary")
        data = res.json()
        # Two distinct schedule_activity_ids → 2 total activities
        assert data["total_activities"] == 2
        # Both at 50% → in_progress
        assert data["in_progress_activities"] == 2
        assert data["completed_activities"] == 0

    def test_completed_activity_counted(self):
        """An activity with 100% progress is counted as completed, not in_progress."""
        r = _make_review(confidence=0.9, progress_pct=100.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/summary")
        data = res.json()
        assert data["completed_activities"] == 1
        assert data["in_progress_activities"] == 0

    def test_delayed_activity_counted(self):
        """A progress event with status=PAUSED is counted as delayed."""
        r = _make_review(confidence=0.9, progress_pct=30.0)
        _approve_review(r["id"])

        # Create progress with PAUSED status (delayed activity)
        res = client.post(
            "/api/v1/progress",
            json={"review_id": r["id"], "status": "PAUSED"},
        )
        assert res.status_code == 201

        summary = client.get("/api/v1/dashboard/summary").json()
        assert summary["delayed_activities"] == 1
        # PAUSED at 30% → still in_progress by percentage range,
        # but delayed counter captures PAUSED status separately.
        assert summary["in_progress_activities"] == 1

    def test_response_shape(self):
        """Response contains all required keys with correct types."""
        res = client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        int_keys = [
            "total_activities", "completed_activities", "in_progress_activities",
            "delayed_activities", "pending_reviews", "approved_reviews",
            "rejected_reviews", "modified_reviews", "total_progress_events",
        ]
        for k in int_keys:
            assert k in data, f"Missing key: {k}"
            assert isinstance(data[k], int), f"Key {k} should be int, got {type(data[k])}"
        assert "average_match_confidence" in data

    def test_no_hardcoded_values(self):
        """Requirement 5: Summary must return 0 for all integer fields when stores
        are empty.  Any non-zero value in an empty state indicates a hardcoded value.
        """
        res = client.get("/api/v1/dashboard/summary")
        data = res.json()
        int_keys = [
            "total_activities", "completed_activities", "in_progress_activities",
            "delayed_activities", "pending_reviews", "approved_reviews",
            "rejected_reviews", "modified_reviews", "total_progress_events",
        ]
        for k in int_keys:
            assert data[k] == 0, (
                f"Hardcoded value detected: '{k}' = {data[k]} but stores are empty"
            )
        assert data["average_match_confidence"] is None, (
            "Hardcoded confidence detected — must be None when no reviews exist"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dashboard/projects/{project_id}
# ═══════════════════════════════════════════════════════════════════════════════


class TestProjectSummary:

    def test_unknown_project_returns_zeros(self):
        """A project with no activity returns zero metrics — never 404.
        Requirement 4: empty datasets return valid zero/empty responses.
        """
        project_id = str(uuid4())
        res = client.get(f"/api/v1/dashboard/projects/{project_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["project_id"] == project_id
        assert data["total_progress_events"] == 0
        assert data["average_progress_percentage"] is None
        assert data["total_audit_logs"] == 0

    def test_invalid_project_uuid_returns_422(self):
        """A non-UUID project_id is rejected with 422."""
        res = client.get("/api/v1/dashboard/projects/not-a-uuid")
        assert res.status_code == 422

    def test_project_summary_with_events(self):
        """Returns correct event count and average percentage for a specific project.
        Requirement 1: creating progress/audit data changes project metrics.
        """
        project_id = str(uuid4())

        r1 = _make_review(confidence=0.9, progress_pct=40.0, project_id=project_id)
        _approve_review(r1["id"])
        _create_progress(r1["id"], project_id=project_id)

        r2 = _make_review(confidence=0.8, progress_pct=60.0, project_id=project_id)
        _approve_review(r2["id"])
        _create_progress(r2["id"], project_id=project_id)

        res = client.get(f"/api/v1/dashboard/projects/{project_id}")
        assert res.status_code == 200
        data = res.json()

        assert data["total_progress_events"] == 2
        # avg of 40.0 and 60.0
        assert data["average_progress_percentage"] == pytest.approx(50.0, abs=0.1)
        # Each progress event auto-creates one audit event
        assert data["total_audit_logs"] == 2

    def test_project_isolation(self):
        """Events from project A do not appear in project B's summary.
        Requirement 2: project filters return only matching real data.
        """
        pid_a = str(uuid4())
        pid_b = str(uuid4())

        r = _make_review(confidence=0.9, progress_pct=80.0, project_id=pid_a)
        _approve_review(r["id"])
        _create_progress(r["id"], project_id=pid_a)

        res = client.get(f"/api/v1/dashboard/projects/{pid_b}")
        data = res.json()
        assert data["total_progress_events"] == 0
        assert data["total_audit_logs"] == 0

    def test_response_shape(self):
        """Project summary contains required keys."""
        pid = str(uuid4())
        res = client.get(f"/api/v1/dashboard/projects/{pid}")
        assert res.status_code == 200
        data = res.json()
        for key in ["project_id", "total_progress_events", "average_progress_percentage", "total_audit_logs"]:
            assert key in data, f"Missing key: {key}"

    def test_no_hardcoded_project_values(self):
        """Requirement 5: A never-seen project_id must return zeros, not hardcoded data."""
        pid = str(uuid4())
        data = client.get(f"/api/v1/dashboard/projects/{pid}").json()
        assert data["total_progress_events"] == 0, "Hardcoded progress event count detected"
        assert data["total_audit_logs"] == 0, "Hardcoded audit log count detected"
        assert data["average_progress_percentage"] is None, "Hardcoded avg_pct detected"


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dashboard/activities
# ═══════════════════════════════════════════════════════════════════════════════


class TestActivities:

    def test_empty_state(self):
        """Empty store returns total=0 and empty items list.
        Requirement 4: empty datasets return valid zero/empty responses.
        """
        res = client.get("/api/v1/dashboard/activities")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_returns_items_after_progress_events(self):
        """Activity items appear once progress events exist.
        Requirement 1: creating progress data changes activity list.
        """
        before = client.get("/api/v1/dashboard/activities").json()
        assert before["total"] == 0

        r = _make_review(confidence=0.85, progress_pct=55.0, discipline="Piping")
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/activities")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        item = data["items"][0]
        assert item["latest_progress_percentage"] == pytest.approx(55.0)
        assert "schedule_activity_id" in item
        assert "project_id" in item
        assert "last_updated" in item

    def test_filter_by_project_id(self):
        """project_id filter returns only activities from that project.
        Requirement 2: project_id filter returns only matching real data.
        """
        pid_a = str(uuid4())
        pid_b = str(uuid4())

        ra = _make_review(confidence=0.9, progress_pct=30.0, project_id=pid_a)
        _approve_review(ra["id"])
        pa = _create_progress(ra["id"], project_id=pid_a)

        rb = _make_review(confidence=0.8, progress_pct=70.0, project_id=pid_b)
        _approve_review(rb["id"])
        _create_progress(rb["id"], project_id=pid_b)

        pid_a_actual = pa["project_id"]

        res = client.get(f"/api/v1/dashboard/activities?project_id={pid_a_actual}")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["project_id"] == pid_a_actual

    def test_filter_by_status(self):
        """status filter returns only matching progress status.
        Requirement 2: status filter returns only matching real data.
        """
        r1 = _make_review(confidence=0.9, progress_pct=100.0)
        _approve_review(r1["id"])
        p1 = _create_progress(r1["id"])  # default IN_PROGRESS status

        r2 = _make_review(confidence=0.8, progress_pct=40.0)
        _approve_review(r2["id"])
        _create_progress(r2["id"])  # also IN_PROGRESS

        # Both are IN_PROGRESS status (default) regardless of percentage
        status_val = p1["status"]  # e.g. "IN_PROGRESS"

        res_status = client.get(f"/api/v1/dashboard/activities?status={status_val}")
        assert res_status.status_code == 200
        items = res_status.json()["items"]
        for item in items:
            assert item["progress_status"] == status_val

    def test_filter_by_status_no_matches(self):
        """Status filter with no matching items returns empty list, not an error.
        Requirement 4 & 2: filters on real data, empty OK.
        """
        r = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])  # creates IN_PROGRESS status

        res = client.get("/api/v1/dashboard/activities?status=PAUSED")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_filter_by_discipline(self):
        """discipline filter is case-insensitive and returns matching items only.
        Requirement 2: discipline filter returns only matching real data.
        """
        r1 = _make_review(confidence=0.9, progress_pct=50.0, discipline="Civil")
        _approve_review(r1["id"])
        _create_progress(r1["id"])

        r2 = _make_review(confidence=0.8, progress_pct=40.0, discipline="Electrical")
        _approve_review(r2["id"])
        _create_progress(r2["id"])

        res = client.get("/api/v1/dashboard/activities?discipline=civil")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["discipline"] == "Civil"

    def test_filter_activity_level_returns_empty(self):
        """activity_level filter returns empty list (no persistent schedule store).
        This is the expected documented behavior — not an error.
        """
        r = _make_review(confidence=0.9, progress_pct=60.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/activities?activity_level=L5")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_invalid_activity_level_returns_422(self):
        """An activity_level value not in the enum is rejected with 422."""
        res = client.get("/api/v1/dashboard/activities?activity_level=L9")
        assert res.status_code == 422

    def test_combined_filters(self):
        """project_id + discipline filters are applied together (AND semantics).
        Requirement 2: combined filters return only matching real data.
        """
        pid = str(uuid4())

        # Matching: correct project + correct discipline
        r_match = _make_review(confidence=0.9, progress_pct=50.0, discipline="Civil", project_id=pid)
        _approve_review(r_match["id"])
        p_match = _create_progress(r_match["id"], project_id=pid)

        # Non-matching: correct project, wrong discipline
        r_other = _make_review(confidence=0.8, progress_pct=40.0, discipline="Mechanical", project_id=pid)
        _approve_review(r_other["id"])
        _create_progress(r_other["id"], project_id=pid)

        actual_pid = p_match["project_id"]
        res = client.get(f"/api/v1/dashboard/activities?project_id={actual_pid}&discipline=Civil")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["discipline"] == "Civil"

    def test_items_sorted_newest_first(self):
        """Multiple activity items are returned newest-first."""
        r1 = _make_review(confidence=0.9, progress_pct=30.0)
        _approve_review(r1["id"])
        _create_progress(r1["id"])

        r2 = _make_review(confidence=0.8, progress_pct=60.0)
        _approve_review(r2["id"])
        _create_progress(r2["id"])

        res = client.get("/api/v1/dashboard/activities")
        items = res.json()["items"]
        assert len(items) == 2
        # Timestamps should be in descending order
        from datetime import datetime
        t0 = datetime.fromisoformat(items[0]["last_updated"].replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(items[1]["last_updated"].replace("Z", "+00:00"))
        assert t0 >= t1

    def test_no_hardcoded_activity_values(self):
        """Requirement 5: activities endpoint must return empty list when no data exists."""
        data = client.get("/api/v1/dashboard/activities").json()
        assert data["total"] == 0, "Hardcoded total detected in empty state"
        assert data["items"] == [], "Hardcoded items detected in empty state"


# ═══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/dashboard/recent-activity
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecentActivity:

    def test_empty_state(self):
        """Empty stores return total=0 and empty items list.
        Requirement 4: empty datasets return valid zero/empty responses.
        """
        res = client.get("/api/v1/dashboard/recent-activity")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_includes_progress_event_kind(self):
        """Feed contains 'progress' items after a progress event is created.
        Requirement 3: recent activity contains actual workflow events.
        """
        r = _make_review(confidence=0.85, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity")
        assert res.status_code == 200
        items = res.json()["items"]
        kinds = {item["event_kind"] for item in items}
        assert "progress" in kinds

    def test_includes_review_decision_kind(self):
        """Feed contains 'review_decision' items after a review is decided.
        Requirement 3: recent activity contains actual workflow events.
        """
        r = _make_review(confidence=0.75, progress_pct=40.0)
        _approve_review(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity")
        items = res.json()["items"]
        kinds = {item["event_kind"] for item in items}
        assert "review_decision" in kinds

    def test_pending_reviews_excluded_from_feed(self):
        """PENDING reviews (no decision yet) are not included in the feed."""
        _make_review(confidence=0.75)  # stays PENDING

        res = client.get("/api/v1/dashboard/recent-activity")
        items = res.json()["items"]
        review_decision_items = [i for i in items if i["event_kind"] == "review_decision"]
        assert len(review_decision_items) == 0

    def test_includes_audit_event_kind(self):
        """Feed contains 'audit' items (auto-created by progress workflow).
        Requirement 3: recent activity contains actual workflow events.
        """
        r = _make_review(confidence=0.9, progress_pct=80.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity")
        items = res.json()["items"]
        kinds = {item["event_kind"] for item in items}
        assert "audit" in kinds

    def test_all_three_kinds_present(self):
        """A complete workflow produces all three event kinds in the feed.
        Requirement 3: recent activity contains actual workflow events.
        """
        r = _make_review(confidence=0.85, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity")
        items = res.json()["items"]
        kinds = {item["event_kind"] for item in items}
        assert kinds == {"progress", "review_decision", "audit"}

    def test_feed_sorted_newest_first(self):
        """Items in the feed are ordered newest-first by timestamp."""
        r = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity")
        items = res.json()["items"]
        from datetime import datetime, timezone
        timestamps = [
            datetime.fromisoformat(i["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if i["timestamp"].endswith("Z")
            else datetime.fromisoformat(i["timestamp"])
            for i in items
        ]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_custom_limit_respected(self):
        """?limit=N caps the number of returned items at N."""
        # Create 3 complete workflows → 3 progress + 3 review_decision + 3 audit = 9 items
        for _ in range(3):
            r = _make_review(confidence=0.8, progress_pct=50.0)
            _approve_review(r["id"])
            _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity?limit=4")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 4
        assert len(data["items"]) == 4

    def test_limit_1_returns_single_item(self):
        """limit=1 returns exactly one item."""
        r = _make_review(confidence=0.9, progress_pct=60.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        res = client.get("/api/v1/dashboard/recent-activity?limit=1")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_limit_zero_returns_422(self):
        """limit=0 is below the allowed minimum (ge=1) → 422."""
        res = client.get("/api/v1/dashboard/recent-activity?limit=0")
        assert res.status_code == 422

    def test_limit_above_max_returns_422(self):
        """limit=101 exceeds the allowed maximum (le=100) → 422."""
        res = client.get("/api/v1/dashboard/recent-activity?limit=101")
        assert res.status_code == 422

    def test_item_shape(self):
        """Each feed item carries the required fields."""
        r = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r["id"])
        _create_progress(r["id"])

        items = client.get("/api/v1/dashboard/recent-activity").json()["items"]
        for item in items:
            assert "id" in item
            assert "event_kind" in item
            assert "description" in item
            assert "timestamp" in item
            assert "metadata" in item
            assert isinstance(item["metadata"], dict)

    def test_actor_id_populated_for_review_decisions(self):
        """review_decision items carry the reviewer's actor_id."""
        r = _make_review(confidence=0.88)
        _approve_review(r["id"], reviewer="REVIEWER-99")

        items = client.get("/api/v1/dashboard/recent-activity").json()["items"]
        review_items = [i for i in items if i["event_kind"] == "review_decision"]
        assert len(review_items) == 1
        assert review_items[0]["actor_id"] == "REVIEWER-99"

    def test_recent_activity_reflects_actual_workflow_events(self):
        """Requirement 3: recent activity must contain actual workflow events,
        not fabricated data.  Verify that the event IDs in the feed correspond
        to the actual progress / review / audit IDs created.
        """
        r = _make_review(confidence=0.9, progress_pct=70.0)
        review_id = r["id"]
        _approve_review(r["id"])
        pe = _create_progress(r["id"])
        progress_id = pe["id"]

        items = client.get("/api/v1/dashboard/recent-activity").json()["items"]

        item_ids = {item["id"] for item in items}
        # The progress event ID must appear
        assert progress_id in item_ids, "Progress event ID not found in feed"
        # The review ID must appear (as a review_decision item)
        assert review_id in item_ids, "Review ID not found in feed"

    def test_no_hardcoded_recent_activity_values(self):
        """Requirement 5: empty stores must produce total=0 and items=[].
        Any items present without creating data indicates hardcoded values.
        """
        data = client.get("/api/v1/dashboard/recent-activity").json()
        assert data["total"] == 0, "Hardcoded total detected in empty state"
        assert data["items"] == [], "Hardcoded items detected in empty state"

    def test_review_decision_has_metadata_fields(self):
        """review_decision feed items carry status, decision, and confidence in metadata."""
        r = _make_review(confidence=0.77)
        _approve_review(r["id"])

        items = client.get("/api/v1/dashboard/recent-activity").json()["items"]
        review_items = [i for i in items if i["event_kind"] == "review_decision"]
        assert len(review_items) == 1
        meta = review_items[0]["metadata"]
        assert meta["status"] == "APPROVED"
        assert meta["decision"] == "APPROVED"
        assert meta["confidence_score"] == pytest.approx(0.77, abs=1e-3)

    def test_audit_event_has_metadata_fields(self):
        """audit feed items carry event_type, entity_type, entity_id in metadata."""
        r = _make_review(confidence=0.9, progress_pct=50.0)
        _approve_review(r["id"])
        pe = _create_progress(r["id"])
        progress_id = pe["id"]

        items = client.get("/api/v1/dashboard/recent-activity").json()["items"]
        audit_items = [i for i in items if i["event_kind"] == "audit"]
        assert len(audit_items) >= 1
        meta = audit_items[0]["metadata"]
        assert meta["event_type"] == "PROGRESS_UPDATED"
        assert meta["entity_type"] == "ProgressEvent"
        assert meta["entity_id"] == progress_id
