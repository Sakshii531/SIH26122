"""
Unit tests validating repository layer contracts, CRUD interfaces, and in-memory persistence
for all 13 ER entities in the SIH26122 backend.
"""
from datetime import datetime
from uuid import uuid4

import pytest

from app.repositories import (
    InMemoryActivityMatchRepository,
    InMemoryActivityRepository,
    InMemoryActualProgressRepository,
    InMemoryAuditLogRepository,
    InMemoryConflictRepository,
    InMemoryEvidenceRepository,
    InMemoryExtractedProgressEventRepository,
    InMemoryFieldReportRepository,
    InMemoryPlannerReviewRepository,
    InMemoryProjectRepository,
    InMemoryScheduleRepository,
    InMemoryUserRepository,
    InMemoryWBSRepository,
    get_activity_repository,
    get_actual_progress_repository,
    get_audit_log_repository,
    get_conflict_repository,
    get_planner_review_repository,
    get_project_repository,
    reset_all_repositories,
)
from app.schemas import (
    ActivityMatchCreate,
    ActivityStatus,
    AuditEventCreate,
    AuditEventType,
    ConflictCreate,
    ConflictUpdate,
    EvidenceCreate,
    ExtractedProgressEventCreate,
    FieldReportCreate,
    FieldReportFormat,
    MatchStatus,
    ProgressEventResponse,
    ProgressStatus,
    ProjectCreate,
    ProjectUpdate,
    ReviewDecision,
    ReviewItemCreate,
    ReviewStatus,
    ScheduleActivityCreate,
    ScheduleActivityUpdate,
    ScheduleCreate,
    ScheduleUpdate,
    UserCreate,
    UserRole,
    UserUpdate,
    WBSCreate,
    WBSUpdate,
)


class TestProjectRepository:
    def test_project_crud(self):
        repo = InMemoryProjectRepository()
        proj = repo.create(ProjectCreate(name="Substation Expansion", code="PRJ-101", description="400kV Substation"))

        assert proj.id is not None
        assert proj.name == "Substation Expansion"
        assert proj.code == "PRJ-101"

        fetched = repo.get_by_id(proj.id)
        assert fetched is not None
        assert fetched.id == proj.id

        updated = repo.update(proj.id, ProjectUpdate(name="Substation Expansion Phase 1"))
        assert updated is not None
        assert updated.name == "Substation Expansion Phase 1"

        all_projs = repo.list_all()
        assert len(all_projs) == 1

        assert repo.delete(proj.id) is True
        assert repo.get_by_id(proj.id) is None
        assert len(repo.list_all()) == 0


class TestScheduleRepository:
    def test_schedule_crud(self):
        repo = InMemoryScheduleRepository()
        p_id = uuid4()
        sched = repo.create(ScheduleCreate(project_id=p_id, name="Baseline Master Schedule", version="v1.0"))

        assert sched.id is not None
        assert sched.project_id == p_id
        assert sched.version == "v1.0"

        by_proj = repo.list_by_project(p_id)
        assert len(by_proj) == 1

        updated = repo.update(sched.id, ScheduleUpdate(version="v1.1"))
        assert updated is not None
        assert updated.version == "v1.1"

        assert repo.delete(sched.id) is True
        assert len(repo.list_all()) == 0


class TestWBSRepository:
    def test_wbs_crud(self):
        repo = InMemoryWBSRepository()
        s_id = uuid4()
        wbs = repo.create(WBSCreate(schedule_id=s_id, wbs_code="1.1", wbs_name="Civils", level=1))

        assert wbs.id is not None
        assert wbs.wbs_code == "1.1"

        by_sched = repo.list_by_schedule(s_id)
        assert len(by_sched) == 1

        updated = repo.update(wbs.id, WBSUpdate(wbs_name="Civil Foundations"))
        assert updated is not None
        assert updated.wbs_name == "Civil Foundations"

        assert repo.delete(wbs.id) is True
        assert len(repo.list_all()) == 0


class TestActivityRepository:
    def test_activity_crud_and_lookup(self):
        repo = InMemoryActivityRepository()
        p_id = uuid4()
        s_id = uuid4()
        w_id = uuid4()

        act = repo.create(
            ScheduleActivityCreate(
                project_id=p_id,
                schedule_id=s_id,
                wbs_id=w_id,
                activity_code="ACT-001",
                name="Trench Excavation",
                discipline="Civil",
            )
        )

        assert act.id is not None
        assert act.activity_code == "ACT-001"

        by_code = repo.get_by_code("act-001")
        assert by_code is not None
        assert by_code.id == act.id

        by_proj = repo.list_by_project(p_id)
        assert len(by_proj) == 1

        updated = repo.update(act.id, ScheduleActivityUpdate(status=ActivityStatus.IN_PROGRESS, progress_percentage=50.0))
        assert updated is not None
        assert updated.status == ActivityStatus.IN_PROGRESS
        assert updated.progress_percentage == 50.0

        assert repo.delete(act.id) is True
        assert repo.get_by_id(act.id) is None


class TestFieldReportRepository:
    def test_field_report_crud(self):
        repo = InMemoryFieldReportRepository()
        p_id = uuid4()
        report = repo.create(
            FieldReportCreate(
                project_id=p_id,
                source_format=FieldReportFormat.TEXT,
                reporter_id="inspector_jack",
                raw_content="Excavation completed for Zone A.",
                discipline="Civil",
            )
        )

        assert report.id is not None
        assert report.reporter_id == "inspector_jack"

        by_proj = repo.list_by_project(p_id)
        assert len(by_proj) == 1

        assert repo.delete(report.id) is True
        assert len(repo.list_all()) == 0


class TestEvidenceRepository:
    def test_evidence_crud(self):
        repo = InMemoryEvidenceRepository()
        r_id = uuid4()
        ev = repo.create(
            EvidenceCreate(
                report_id=r_id,
                file_name="site1.jpg",
                file_url="/storage/site1.jpg",
                mime_type="image/jpeg",
                description="Photo of excavated trench",
            )
        )

        assert ev.id is not None
        assert ev.report_id == r_id
        assert ev.file_name == "site1.jpg"

        by_rep = repo.list_by_report(r_id)
        assert len(by_rep) == 1

        assert repo.delete(ev.id) is True
        assert len(repo.list_all()) == 0


class TestExtractedProgressEventRepository:
    def test_extracted_progress_crud(self):
        repo = InMemoryExtractedProgressEventRepository()
        r_id = uuid4()
        event = repo.create(
            ExtractedProgressEventCreate(
                report_id=r_id,
                raw_text="Excavated 50 meters of trenching.",
                extracted_progress_percentage=50.0,
                extracted_status="IN_PROGRESS",
                extraction_confidence=0.92,
            )
        )

        assert event.id is not None
        assert event.extraction_confidence == 0.92

        by_rep = repo.list_by_report(r_id)
        assert len(by_rep) == 1

        assert repo.delete(event.id) is True
        assert len(repo.list_all()) == 0


class TestActivityMatchRepository:
    def test_activity_match_crud(self):
        repo = InMemoryActivityMatchRepository()
        ev_id = uuid4()
        r_id = uuid4()
        act_id = uuid4()
        match = repo.create(
            ActivityMatchCreate(
                event_id=ev_id,
                report_id=r_id,
                field_report_id=r_id,
                activity_id=act_id,
                confidence_score=0.88,
                match_status=MatchStatus.AUTO_MATCHED,
            )
        )

        assert match.id is not None
        assert match.confidence_score == 0.88

        by_ev = repo.list_by_event(ev_id)
        assert len(by_ev) == 1

        assert repo.delete(match.id) is True
        assert len(repo.list_all()) == 0


class TestPlannerReviewRepository:
    def test_planner_review_crud_and_filters(self):
        repo = InMemoryPlannerReviewRepository()
        r_id = uuid4()
        review = repo.create(
            ReviewItemCreate(
                report_id=r_id,
                confidence_score=0.85,
                extracted_progress_percentage=60.0,
            )
        )

        assert review.id is not None
        assert review.status == ReviewStatus.PENDING

        pending = repo.list_all(status=ReviewStatus.PENDING)
        assert len(pending) == 1

        approved_list = repo.list_all(status=ReviewStatus.APPROVED)
        assert len(approved_list) == 0

        updated_review = review.model_copy(update={"status": ReviewStatus.APPROVED, "decision": ReviewDecision.APPROVED})
        repo.update(review.id, updated_review)

        assert repo.get_by_id(review.id).status == ReviewStatus.APPROVED
        assert len(repo.list_all(status=ReviewStatus.APPROVED)) == 1

        assert repo.delete(review.id) is True
        assert len(repo.list_all()) == 0


class TestConflictRepository:
    def test_conflict_crud_and_filters(self):
        repo = InMemoryConflictRepository()
        ev1 = uuid4()
        ev2 = uuid4()

        conflict = repo.create(
            ConflictCreate(
                event_id=ev1,
                conflicting_event_id=ev2,
                conflict_type="PROGRESS_OVERLAP",
                severity="HIGH",
                description="Conflicting progress reports for same activity.",
            )
        )

        assert conflict.id is not None
        assert conflict.resolution_status == "PENDING"

        by_ev = repo.list_all(event_id=ev1)
        assert len(by_ev) == 1

        updated = repo.update(
            conflict.id,
            ConflictUpdate(resolution_status="RESOLVED", resolved_by="planner_1", resolution_notes="Verified on site."),
        )
        assert updated.resolution_status == "RESOLVED"

        resolved_list = repo.list_all(resolution_status="RESOLVED")
        assert len(resolved_list) == 1

        assert repo.delete(conflict.id) is True
        assert len(repo.list_all()) == 0


class TestActualProgressRepository:
    def test_actual_progress_crud_and_review_map(self):
        repo = InMemoryActualProgressRepository()
        p_id = uuid4()
        a_id = uuid4()
        r_id = uuid4()
        prog_id = uuid4()

        prog_event = ProgressEventResponse(
            id=prog_id,
            activity_id=a_id,
            project_id=p_id,
            review_id=r_id,
            status=ProgressStatus.IN_PROGRESS,
            progress_percentage=75.0,
            timestamp=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )

        repo.create(prog_event)

        assert repo.get_by_id(prog_id) is not None
        assert repo.get_by_review_id(r_id) is not None
        assert repo.get_by_review_id(r_id).id == prog_id

        listed = repo.list_all(project_id=p_id)
        assert len(listed) == 1

        assert repo.delete(prog_id) is True
        assert repo.get_by_review_id(r_id) is None
        assert len(repo.list_all()) == 0


class TestAuditLogRepository:
    def test_audit_log_crud_and_filters(self):
        repo = InMemoryAuditLogRepository()
        p_id = uuid4()
        ent_id = uuid4()

        audit = repo.create(
            AuditEventCreate(
                project_id=p_id,
                event_type=AuditEventType.PROGRESS_UPDATED,
                entity_type="ProgressEvent",
                entity_id=ent_id,
                actor_id="planner_jack",
                actor_role="PLANNER",
                description="Updated actual progress to 75%",
            )
        )

        assert audit.id is not None
        assert audit.entity_type == "ProgressEvent"

        by_type = repo.list_all(entity_type="progressevent")
        assert len(by_type) == 1

        by_ent = repo.list_all(entity_id=ent_id)
        assert len(by_ent) == 1

        assert repo.delete(audit.id) is True
        assert len(repo.list_all()) == 0


class TestUserRepository:
    def test_user_crud(self):
        repo = InMemoryUserRepository()
        user = repo.create(
            UserCreate(
                username="lead_planner",
                email="lead@example.com",
                full_name="Lead Planner",
                role=UserRole.PLANNER,
            )
        )

        assert user.id is not None
        assert user.username == "lead_planner"

        by_uname = repo.get_by_username("LEAD_PLANNER")
        assert by_uname is not None
        assert by_uname.id == user.id

        updated = repo.update(user.id, UserUpdate(full_name="Senior Lead Planner"))
        assert updated is not None
        assert updated.full_name == "Senior Lead Planner"

        assert repo.delete(user.id) is True
        assert len(repo.list_all()) == 0


class TestRepositoryFactoryAndReset:
    def test_factory_accessors_and_reset(self):
        reset_all_repositories()

        proj_repo = get_project_repository()
        review_repo = get_planner_review_repository()
        conflict_repo = get_conflict_repository()

        proj_repo.create(ProjectCreate(name="Test Proj", code="TP-1"))
        review_repo.create(ReviewItemCreate(report_id=uuid4(), confidence_score=0.9))
        conflict_repo.create(
            ConflictCreate(
                event_id=uuid4(),
                conflicting_event_id=uuid4(),
                conflict_type="DUPLICATE",
                severity="LOW",
                description="Duplicate event conflict",
            )
        )

        assert len(proj_repo.list_all()) == 1
        assert len(review_repo.list_all()) == 1
        assert len(conflict_repo.list_all()) == 1

        reset_all_repositories()

        assert len(proj_repo.list_all()) == 0
        assert len(review_repo.list_all()) == 0
        assert len(conflict_repo.list_all()) == 0
