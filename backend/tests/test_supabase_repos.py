from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest

from app.core.config import get_settings
from app.repositories.factory import (
    get_activity_match_repository,
    get_activity_repository,
    get_actual_progress_repository,
    get_audit_log_repository,
    get_conflict_repository,
    get_evidence_repository,
    get_extracted_progress_event_repository,
    get_field_report_repository,
    get_planner_review_repository,
    get_project_repository,
    get_schedule_repository,
    get_user_repository,
    get_wbs_repository,
    reset_all_repositories,
)
from app.repositories.in_memory import InMemoryProjectRepository
from app.repositories.supabase_repos import (
    SupabaseActivityMatchRepository,
    SupabaseActivityRepository,
    SupabaseActualProgressRepository,
    SupabaseAuditLogRepository,
    SupabaseConflictRepository,
    SupabaseEvidenceRepository,
    SupabaseExtractedProgressEventRepository,
    SupabaseFieldReportRepository,
    SupabasePlannerReviewRepository,
    SupabaseProjectRepository,
    SupabaseScheduleRepository,
    SupabaseUserRepository,
    SupabaseWBSRepository,
)
from app.schemas.activity import ScheduleActivityCreate, ScheduleActivityResponse, ScheduleActivityUpdate
from app.schemas.activity_match import ActivityMatchCreate, ActivityMatchResponse
from app.schemas.audit_log import AuditEventCreate, AuditEventResponse
from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate
from app.schemas.enums import ProgressStatus, ReviewStatus
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.schemas.extracted_progress_event import ExtractedProgressEventCreate, ExtractedProgressEventResponse
from app.schemas.field_report import FieldReportCreate, FieldReportResponse
from app.schemas.progress_event import ProgressEventResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.review_workflow import ReviewItemCreate, ReviewItemResponse
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.wbs import WBSCreate, WBSResponse, WBSUpdate


def create_mock_client():
    client = MagicMock()
    builder = MagicMock()
    client.table.return_value = builder
    builder.select.return_value = builder
    builder.insert.return_value = builder
    builder.upsert.return_value = builder
    builder.update.return_value = builder
    builder.delete.return_value = builder
    builder.eq.return_value = builder
    builder.ilike.return_value = builder
    builder.or_.return_value = builder
    return client, builder


# 1. Projects
def test_supabase_project_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseProjectRepository(client=client)

    p_id = str(uuid4())
    row_data = {
        "id": p_id,
        "name": "Project Alpha",
        "code": "PA-001",
        "description": "Test description",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    # create
    created = repo.create(ProjectCreate(name="Project Alpha", code="PA-001", description="Test description"))
    assert str(created.id) == p_id
    assert created.name == "Project Alpha"

    # get_by_id
    item = repo.get_by_id(uuid4())
    assert item is not None
    assert item.name == "Project Alpha"

    # list_all
    items = repo.list_all()
    assert len(items) == 1

    # update
    updated = repo.update(uuid4(), ProjectUpdate(name="Updated Alpha"))
    assert updated is not None

    # save
    saved = repo.save(created)
    assert saved.id == created.id

    # delete
    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    # clear
    with pytest.raises(NotImplementedError):
        repo.clear()


# 2. Schedules
def test_supabase_schedule_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseScheduleRepository(client=client)

    s_id = str(uuid4())
    p_id = str(uuid4())
    row_data = {
        "id": s_id,
        "project_id": p_id,
        "name": "Schedule 1",
        "version": "v1.0",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(ScheduleCreate(project_id=p_id, name="Schedule 1", version="v1.0"))
    assert str(created.id) == s_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    list_proj = repo.list_by_project(uuid4())
    assert len(list_proj) == 1

    list_all = repo.list_all()
    assert len(list_all) == 1

    updated = repo.update(uuid4(), ScheduleUpdate(name="Sched Updated"))
    assert updated is not None

    saved = repo.save(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 3. WBS
def test_supabase_wbs_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseWBSRepository(client=client)

    w_id = str(uuid4())
    s_id = str(uuid4())
    row_data = {
        "id": w_id,
        "schedule_id": s_id,
        "wbs_code": "1.1",
        "wbs_name": "Earthworks",
        "level": 1,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(WBSCreate(schedule_id=s_id, wbs_code="1.1", wbs_name="Earthworks", level=1))
    assert str(created.id) == w_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    list_sched = repo.list_by_schedule(uuid4())
    assert len(list_sched) == 1

    list_all = repo.list_all()
    assert len(list_all) == 1

    updated = repo.update(uuid4(), WBSUpdate(wbs_name="Updated Earthworks"))
    assert updated is not None

    saved = repo.save(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 4. Activities
def test_supabase_activity_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseActivityRepository(client=client)

    a_id = str(uuid4())
    p_id = str(uuid4())
    s_id = str(uuid4())
    w_id = str(uuid4())
    row_data = {
        "id": a_id,
        "project_id": p_id,
        "schedule_id": s_id,
        "wbs_id": w_id,
        "activity_code": "ACT-100",
        "name": "Excavation",
        "discipline": "Civil",
        "status": "NOT_STARTED",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        ScheduleActivityCreate(
            project_id=p_id,
            schedule_id=s_id,
            wbs_id=w_id,
            activity_code="ACT-100",
            name="Excavation",
            discipline="Civil",
        )
    )
    assert str(created.id) == a_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_code = repo.get_by_code("ACT-100")
    assert by_code is not None

    by_proj = repo.list_by_project(uuid4())
    assert len(by_proj) == 1

    all_items = repo.list_all()
    assert len(all_items) == 1

    updated = repo.update(uuid4(), ScheduleActivityUpdate(name="Deep Excavation"))
    assert updated is not None

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 5. Field Reports
def test_supabase_field_report_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseFieldReportRepository(client=client)

    fr_id = str(uuid4())
    p_id = str(uuid4())
    reporter_id = str(uuid4())
    row_data = {
        "id": fr_id,
        "project_id": p_id,
        "source_format": "TEXT",
        "reporter_id": reporter_id,
        "raw_content": "Report details",
        "created_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        FieldReportCreate(project_id=p_id, source_format="TEXT", raw_content="Report details", reporter_id=reporter_id)
    )
    assert str(created.id) == fr_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_proj = repo.list_by_project(uuid4())
    assert len(by_proj) == 1

    all_items = repo.list_all()
    assert len(all_items) == 1

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 6. Evidence
def test_supabase_evidence_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseEvidenceRepository(client=client)

    e_id = str(uuid4())
    r_id = str(uuid4())
    row_data = {
        "id": e_id,
        "report_id": r_id,
        "file_name": "site.jpg",
        "file_url": "http://example.com/site.jpg",
        "created_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(EvidenceCreate(report_id=r_id, file_name="site.jpg", file_url="http://example.com/site.jpg"))
    assert str(created.id) == e_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_rep = repo.list_by_report(uuid4())
    assert len(by_rep) == 1

    all_items = repo.list_all()
    assert len(all_items) == 1

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 7. Extracted Progress Events
def test_supabase_extracted_progress_event_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseExtractedProgressEventRepository(client=client)

    ev_id = str(uuid4())
    r_id = str(uuid4())
    row_data = {
        "id": ev_id,
        "report_id": r_id,
        "extracted_activity_name": "Concrete poured",
        "extracted_quantity": 50.0,
        "extraction_confidence": 0.9,
        "created_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        ExtractedProgressEventCreate(
            report_id=r_id,
            extracted_activity_name="Concrete poured",
            extracted_quantity=50.0,
            extraction_confidence=0.9,
        )
    )
    assert str(created.id) == ev_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_rep = repo.list_by_report(uuid4())
    assert len(by_rep) == 1

    all_items = repo.list_all()
    assert len(all_items) == 1

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 8. Activity Matches
def test_supabase_activity_match_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseActivityMatchRepository(client=client)

    m_id = str(uuid4())
    e_id = str(uuid4())
    r_id = str(uuid4())
    a_id = str(uuid4())
    row_data = {
        "id": m_id,
        "event_id": e_id,
        "report_id": r_id,
        "field_report_id": r_id,
        "activity_id": a_id,
        "schedule_activity_id": a_id,
        "confidence_score": 0.95,
        "match_status": "AUTO_MATCHED",
        "created_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        ActivityMatchCreate(
            event_id=e_id,
            report_id=r_id,
            activity_id=a_id,
            confidence_score=0.95,
        )
    )
    assert str(created.id) == m_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_evt = repo.list_by_event(uuid4())
    assert len(by_evt) == 1

    all_items = repo.list_all()
    assert len(all_items) == 1

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 9. Planner Reviews
def test_supabase_planner_review_repo_crud():
    client, builder = create_mock_client()
    repo = SupabasePlannerReviewRepository(client=client)

    rv_id = str(uuid4())
    r_id = str(uuid4())
    a_id = str(uuid4())
    row_data = {
        "id": rv_id,
        "report_id": r_id,
        "schedule_activity_id": a_id,
        "matched_activity_code": "ACT-100",
        "confidence_score": 0.9,
        "status": "PENDING",
        "created_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        ReviewItemCreate(
            report_id=r_id,
            schedule_activity_id=a_id,
            matched_activity_code="ACT-100",
            confidence_score=0.9,
        )
    )
    assert str(created.id) == rv_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    all_items = repo.list_all(status=ReviewStatus.PENDING)
    assert len(all_items) == 1

    updated = repo.update(uuid4(), created)
    assert updated.id == created.id

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 10. Conflicts
def test_supabase_conflict_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseConflictRepository(client=client)

    c_id = str(uuid4())
    e1_id = str(uuid4())
    e2_id = str(uuid4())
    row_data = {
        "id": c_id,
        "event_id": e1_id,
        "conflicting_event_id": e2_id,
        "conflict_type": "QUANTITY_MISMATCH",
        "severity": "HIGH",
        "description": "Conflict detected",
        "resolution_status": "OPEN",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        ConflictCreate(
            event_id=e1_id,
            conflicting_event_id=e2_id,
            conflict_type="QUANTITY_MISMATCH",
            severity="HIGH",
            description="Conflict detected",
        )
    )
    assert str(created.id) == c_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    all_items = repo.list_all(event_id=uuid4(), resolution_status="OPEN")
    assert len(all_items) == 1

    updated = repo.update(uuid4(), ConflictUpdate(resolution_status="RESOLVED"))
    assert updated is not None

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 11. Actual Progress
def test_supabase_actual_progress_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseActualProgressRepository(client=client)

    ap_id = str(uuid4())
    rv_id = str(uuid4())
    a_id = str(uuid4())
    p_id = str(uuid4())
    row_data = {
        "id": ap_id,
        "review_id": rv_id,
        "activity_id": a_id,
        "schedule_activity_id": a_id,
        "project_id": p_id,
        "quantity": 100.0,
        "unit_of_measure": "m3",
        "status": "IN_PROGRESS",
        "progress_percentage": 50.0,
        "event_date": "2026-01-01",
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    resp_model = ProgressEventResponse.model_validate(row_data)

    created = repo.create(resp_model)
    assert str(created.id) == ap_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_rv = repo.get_by_review_id(uuid4())
    assert by_rv is not None

    all_items = repo.list_all(project_id=uuid4(), status=ProgressStatus.IN_PROGRESS)
    assert len(all_items) == 1

    saved = repo.save(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 12. Audit Logs
def test_supabase_audit_log_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseAuditLogRepository(client=client)

    al_id = str(uuid4())
    p_id = str(uuid4())
    e_id = str(uuid4())
    row_data = {
        "id": al_id,
        "project_id": p_id,
        "event_type": "PROGRESS_UPDATED",
        "entity_type": "Project",
        "entity_id": e_id,
        "description": "Project created",
        "timestamp": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(
        AuditEventCreate(
            project_id=p_id,
            event_type="PROGRESS_UPDATED",
            entity_type="Project",
            entity_id=e_id,
            description="Project created",
        )
    )
    assert str(created.id) == al_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    all_items = repo.list_all(entity_type="Project", entity_id=uuid4())
    assert len(all_items) == 1

    saved = repo.save_item(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# 13. Users
def test_supabase_user_repo_crud():
    client, builder = create_mock_client()
    repo = SupabaseUserRepository(client=client)

    u_id = str(uuid4())
    row_data = {
        "id": u_id,
        "username": "johndoe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "PLANNER",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
    }
    builder.execute.return_value = MagicMock(data=[row_data])

    created = repo.create(UserCreate(username="johndoe", email="john@example.com", full_name="John Doe", role="PLANNER"))
    assert str(created.id) == u_id

    item = repo.get_by_id(uuid4())
    assert item is not None

    by_uname = repo.get_by_username("johndoe")
    assert by_uname is not None

    all_items = repo.list_all()
    assert len(all_items) == 1

    updated = repo.update(uuid4(), UserUpdate(full_name="John Updated"))
    assert updated is not None

    saved = repo.save(created)
    assert saved.id == created.id

    builder.execute.return_value = MagicMock(data=[row_data])
    assert repo.delete(uuid4()) is True

    with pytest.raises(NotImplementedError):
        repo.clear()


# Test Factory Branching
def test_factory_switching(monkeypatch):
    reset_all_repositories()

    # Default should be in_memory
    settings = get_settings()
    monkeypatch.setattr(settings, "DB_PROVIDER", "in_memory")
    repo = get_project_repository()
    assert isinstance(repo, InMemoryProjectRepository)

    # Switch to supabase
    monkeypatch.setattr(settings, "DB_PROVIDER", "supabase")
    reset_all_repositories()

    with patch("app.repositories.supabase_repos.get_supabase_client") as mock_get_client:
        mock_client, _ = create_mock_client()
        mock_get_client.return_value = mock_client

        repo_sup = get_project_repository()
        assert isinstance(repo_sup, SupabaseProjectRepository)

        # Confirm 13 getter functions return Supabase instances
        assert isinstance(get_schedule_repository(), SupabaseScheduleRepository)
        assert isinstance(get_wbs_repository(), SupabaseWBSRepository)
        assert isinstance(get_activity_repository(), SupabaseActivityRepository)
        assert isinstance(get_field_report_repository(), SupabaseFieldReportRepository)
        assert isinstance(get_evidence_repository(), SupabaseEvidenceRepository)
        assert isinstance(get_extracted_progress_event_repository(), SupabaseExtractedProgressEventRepository)
        assert isinstance(get_activity_match_repository(), SupabaseActivityMatchRepository)
        assert isinstance(get_planner_review_repository(), SupabasePlannerReviewRepository)
        assert isinstance(get_conflict_repository(), SupabaseConflictRepository)
        assert isinstance(get_actual_progress_repository(), SupabaseActualProgressRepository)
        assert isinstance(get_audit_log_repository(), SupabaseAuditLogRepository)
        assert isinstance(get_user_repository(), SupabaseUserRepository)

    # Switch back to in_memory
    monkeypatch.setattr(settings, "DB_PROVIDER", "in_memory")
    reset_all_repositories()
    assert isinstance(get_project_repository(), InMemoryProjectRepository)
