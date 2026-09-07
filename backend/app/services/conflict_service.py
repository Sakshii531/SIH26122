from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate


class ConflictService:
    """In-memory service managing progress extraction conflicts."""

    _conflicts_db: Dict[UUID, ConflictResponse] = {}

    @classmethod
    def create_conflict(cls, payload: ConflictCreate) -> ConflictResponse:
        """Create a new conflict record."""
        conflict_id = uuid4()
        now = datetime.utcnow()

        conflict = ConflictResponse(
            id=conflict_id,
            event_id=payload.event_id,
            conflicting_event_id=payload.conflicting_event_id,
            conflict_type=payload.conflict_type,
            severity=payload.severity,
            description=payload.description,
            resolution_status=payload.resolution_status,
            resolved_by=payload.resolved_by,
            resolution_notes=payload.resolution_notes,
            metadata=payload.metadata,
            created_at=now,
            updated_at=now,
        )

        cls._conflicts_db[conflict_id] = conflict
        return conflict

    @classmethod
    def get_conflict(cls, conflict_id: UUID) -> ConflictResponse:
        """Retrieve a conflict record by UUID."""
        if conflict_id not in cls._conflicts_db:
            raise HTTPException(
                status_code=404,
                detail=f"Conflict record '{conflict_id}' not found.",
            )
        return cls._conflicts_db[conflict_id]

    @classmethod
    def update_conflict(cls, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        """Update a conflict record (e.g. resolve conflict)."""
        conflict = cls.get_conflict(conflict_id)
        now = datetime.utcnow()

        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = now

        updated = conflict.model_copy(update=updates)
        cls._conflicts_db[conflict_id] = updated
        return updated

    @classmethod
    def list_conflicts(
        cls,
        event_id: Optional[UUID] = None,
        resolution_status: Optional[str] = None,
    ) -> List[ConflictResponse]:
        """List conflicts with optional filtering."""
        items = list(cls._conflicts_db.values())
        if event_id is not None:
            items = [
                item for item in items if item.event_id == event_id or item.conflicting_event_id == event_id
            ]
        if resolution_status is not None:
            items = [item for item in items if item.resolution_status.upper() == resolution_status.upper()]
        return items

    @classmethod
    def clear_db(cls) -> None:
        """Reset in-memory store for testing isolation."""
        cls._conflicts_db.clear()
