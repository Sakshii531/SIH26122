"""
Test suite validating ER diagram alignment, entity definitions, schema relationships,
terminology consistency, and dashboard integration for SIH26122 backend.
"""

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    ActivityBase,
    ActivityCreate,
    ActivityMatchBase,
    ActivityMatchCreate,
    ActivityMatchResponse,
    ActivityResponse,
    ActualProgressBase,
    ActualProgressCreate,
    ActualProgressResponse,
    AuditLogBase,
    AuditLogCreate,
    AuditLogResponse,
    ConflictBase,
    ConflictCreate,
    ConflictResponse,
    ConflictUpdate,
    EvidenceBase,
    EvidenceCreate,
    EvidenceResponse,
    ExtractedProgressEventBase,
    ExtractedProgressEventCreate,
    ExtractedProgressEventResponse,
    FieldReportBase,
    FieldReportCreate,
    FieldReportResponse,
    PlannerReviewBase,
    PlannerReviewCreate,
    PlannerReviewResponse,
    ProjectBase,
    ProjectCreate,
    ProjectResponse,
    ScheduleBase,
    ScheduleCreate,
    ScheduleResponse,
    UserBase,
    UserCreate,
    UserResponse,
    UserRole,
    WBSBase,
    WBSCreate,
    WBSResponse,
)
from app.schemas.enums import AuditEventType, MatchStatus, ProgressStatus, ReviewDecision
from app.services.conflict_service import ConflictService

client = TestClient(app)


class TestEREntitySchemasAndRelationships:
    """Test unit definitions and relationships for all 13 ER entities.

    ER diagram entities (13):
      users, projects, schedules, wbs, activities, field_reports, evidence,
      extracted_progress_events, activity_matches, planner_reviews,
      conflicts, actual_progress, audit_logs.
    """

    def test_users_er_entity(self):
        user_id = uuid4()
        user_resp = UserResponse(
            id=user_id,
            username="planner_user1",
            email="planner1@example.com",
            full_name="Chief Planner",
            role=UserRole.PLANNER,
        )
        assert user_resp.id == user_id
        assert user_resp.user_id == user_id
        assert user_resp.role == UserRole.PLANNER
        dict_data = user_resp.model_dump()
        assert "user_id" in dict_data

    def test_projects_and_schedules_er_relationship(self):
        proj_id = uuid4()
        sched_id = uuid4()
        proj = ProjectResponse(id=proj_id, name="Project Alpha", code="PRJ-A")
        sched = ScheduleResponse(id=sched_id, project_id=proj_id, name="Baseline Schedule", version="v1.0")

        assert proj.project_id == proj_id
        assert sched.schedule_id == sched_id
        assert sched.project_id == proj_id

    def test_wbs_parent_and_activities_er_relationship(self):
        sched_id = uuid4()
        root_wbs_id = uuid4()
        child_wbs_id = uuid4()

        root_wbs = WBSResponse(
            id=root_wbs_id,
            schedule_id=sched_id,
            parent_wbs_id=None,
            wbs_code="1.0",
            wbs_name="Civil Works",
            level=1,
        )
        child_wbs = WBSResponse(
            id=child_wbs_id,
            schedule_id=sched_id,
            parent_wbs_id=root_wbs_id,
            wbs_code="1.1",
            wbs_name="Excavation",
            level=2,
        )
        act = ActivityResponse(
            id=uuid4(),
            project_id=uuid4(),
            schedule_id=sched_id,
            wbs_id=child_wbs_id,
            activity_code="ACT-001",
            name="Zone A Excavation",
            discipline="Civil",
        )

        assert root_wbs.wbs_id == root_wbs_id
        assert child_wbs.parent_wbs_id == root_wbs_id
        assert act.wbs_id == child_wbs_id
        assert act.activity_id == act.id
        assert act.schedule_activity_id == act.id

    def test_field_reports_evidence_and_extracted_events_relationship(self):
        report_id = uuid4()
        ev_id = uuid4()
        event_id = uuid4()

        ev = EvidenceResponse(
            id=ev_id,
            report_id=report_id,
            file_name="site_photo.jpg",
            file_url="/storage/1.jpg",
            mime_type="image/jpeg",
        )
        report = FieldReportResponse(
            id=report_id,
            project_id=uuid4(),
            source_format="TEXT",
            reporter_id="SUP-01",
            raw_content="Excavation completed 80%",
            evidence=[ev],
        )
        extracted = ExtractedProgressEventResponse(
            id=event_id,
            report_id=report_id,
            extracted_activity_name="Excavation",
            extracted_progress_percentage=80.0,
            extraction_confidence=0.92,
        )

        assert report.report_id == report_id
        assert ev.evidence_id == ev_id
        assert extracted.event_id == event_id
        assert extracted.report_id == report_id

    def test_activity_match_and_planner_review_relationship(self):
        event_id = uuid4()
        report_id = uuid4()
        act_id = uuid4()
        match_id = uuid4()
        review_id = uuid4()
        corrected_act_id = uuid4()

        match = ActivityMatchResponse(
            id=match_id,
            event_id=event_id,
            report_id=report_id,
            activity_id=act_id,
            confidence_score=0.88,
            match_status=MatchStatus.AUTO_MATCHED,
        )
        review = PlannerReviewResponse(
            id=review_id,
            match_id=match_id,
            planner_id="PLANNER-01",
            decision=ReviewDecision.MODIFIED,
            corrected_activity_id=corrected_act_id,
        )

        assert match.match_id == match_id
        assert match.activity_id == act_id
        assert match.schedule_activity_id == act_id
        assert review.review_id == review_id
        assert review.match_id == match_id
        assert review.activity_match_id == match_id
        assert review.corrected_activity_id == corrected_act_id

    def test_conflict_er_entity_and_relationship(self):
        ev1 = uuid4()
        ev2 = uuid4()
        c_id = uuid4()

        conflict = ConflictResponse(
            id=c_id,
            event_id=ev1,
            conflicting_event_id=ev2,
            conflict_type="CONTRADICTORY_STATUS",
            severity="HIGH",
            description="Status conflict between text and voice report",
        )

        assert conflict.conflict_id == c_id
        assert conflict.event_id == ev1
        assert conflict.conflicting_event_id == ev2

    def test_actual_progress_and_validated_by_relationship(self):
        act_id = uuid4()
        proj_id = uuid4()
        rep_id = uuid4()
        rev_id = uuid4()
        prog_id = uuid4()

        prog = ActualProgressResponse(
            id=prog_id,
            activity_id=act_id,
            project_id=proj_id,
            report_id=rep_id,
            review_id=rev_id,
            progress_percentage=75.0,
            validated_by="PLANNER-CHIEF",
        )

        assert prog.progress_id == prog_id
        assert prog.activity_id == act_id
        assert prog.schedule_activity_id == act_id
        assert prog.report_id == rep_id
        assert prog.field_report_id == rep_id
        assert prog.validated_by == "PLANNER-CHIEF"

    def test_audit_log_user_entity_relationship(self):
        proj_id = uuid4()
        audit_id = uuid4()
        target_entity_id = uuid4()

        log = AuditLogResponse(
            id=audit_id,
            project_id=proj_id,
            event_type=AuditEventType.PROGRESS_UPDATED,
            entity_type="ActualProgress",
            entity_id=target_entity_id,
            actor_id="USER-123",
            description="Actual progress validated",
        )

        assert log.audit_id == audit_id
        assert log.actor_id == "USER-123"
        assert log.user_id == "USER-123"
        assert log.entity_type == "ActualProgress"


class TestConflictServiceAndEndpoints:
    """Test Conflict service & API endpoints."""

    def test_conflict_crud_service(self):
        ConflictService.clear_db()
        ev1 = uuid4()
        ev2 = uuid4()

        create_payload = ConflictCreate(
            event_id=ev1,
            conflicting_event_id=ev2,
            conflict_type="DUPLICATE_PROGRESS",
            severity="MEDIUM",
            description="Duplicate report for same activity on same day",
        )
        conflict = ConflictService.create_conflict(create_payload)
        assert conflict.conflict_id is not None
        assert conflict.resolution_status == "PENDING"

        # List conflicts
        listed = ConflictService.list_conflicts(event_id=ev1)
        assert len(listed) == 1

        # Update conflict
        updated = ConflictService.update_conflict(
            conflict.id,
            ConflictUpdate(resolution_status="RESOLVED", resolved_by="PLANNER-01", resolution_notes="Verified site log"),
        )
        assert updated.resolution_status == "RESOLVED"
        assert updated.resolved_by == "PLANNER-01"

    def test_conflict_api_endpoints(self):
        ConflictService.clear_db()
        ev1 = str(uuid4())
        ev2 = str(uuid4())

        # POST /api/v1/conflicts
        res = client.post(
            "/api/v1/conflicts",
            json={
                "event_id": ev1,
                "conflicting_event_id": ev2,
                "conflict_type": "OVERLAPPING_DATES",
                "severity": "HIGH",
                "description": "Overlapping schedule execution dates",
            },
        )
        assert res.status_code == 201
        data = res.json()
        cid = data["id"]
        assert data["conflict_id"] == cid
        assert data["resolution_status"] == "PENDING"

        # GET /api/v1/conflicts/{id}
        res = client.get(f"/api/v1/conflicts/{cid}")
        assert res.status_code == 200
        assert res.json()["conflict_type"] == "OVERLAPPING_DATES"

        # PATCH /api/v1/conflicts/{id}
        res = client.patch(
            f"/api/v1/conflicts/{cid}",
            json={"resolution_status": "RESOLVED", "resolved_by": "LEAD-PLANNER"},
        )
        assert res.status_code == 200
        assert res.json()["resolution_status"] == "RESOLVED"
        assert res.json()["resolved_by"] == "LEAD-PLANNER"


class TestProjectAndWBSApiEndpoints:
    """Test project & WBS API endpoints."""

    def test_projects_crud_endpoints(self):
        res = client.post(
            "/api/v1/projects",
            json={
                "name": "SIH Infrastructure Project",
                "code": "SIH-2026",
                "description": "Smart Construction Progress System",
                "location": "Site B",
            },
        )
        assert res.status_code == 201
        p_data = res.json()
        pid = p_data["id"]
        assert p_data["project_id"] == pid

        # GET /projects
        res_list = client.get("/api/v1/projects")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

        # GET /projects/{id}
        res_get = client.get(f"/api/v1/projects/{pid}")
        assert res_get.status_code == 200
        assert res_get.json()["code"] == "SIH-2026"

    def test_dashboard_summary_er_metrics(self):
        res = client.get("/api/v1/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert "total_activities" in data
        assert "total_actual_progress" in data
        assert "total_conflicts" in data
        assert "total_audit_logs" in data
