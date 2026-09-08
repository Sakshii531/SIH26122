from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException

from app.repositories.factory import get_conflict_repository
from app.schemas.conflict import ConflictCreate, ConflictResponse, ConflictUpdate


class ConflictService:
    """Service managing progress extraction conflicts via repository layer."""

    @classmethod
    def create_conflict(cls, payload: ConflictCreate) -> ConflictResponse:
        """Create a new conflict record."""
        repo = get_conflict_repository()
        return repo.create(payload)

    @classmethod
    def get_conflict(cls, conflict_id: UUID) -> ConflictResponse:
        """Retrieve a conflict record by UUID."""
        repo = get_conflict_repository()
        conflict = repo.get_by_id(conflict_id)
        if not conflict:
            raise HTTPException(
                status_code=404,
                detail=f"Conflict record '{conflict_id}' not found.",
            )
        return conflict

    @classmethod
    def update_conflict(cls, conflict_id: UUID, payload: ConflictUpdate) -> ConflictResponse:
        """Update a conflict record (e.g. resolve conflict)."""
        repo = get_conflict_repository()
        # Verify existence first to return proper 404
        cls.get_conflict(conflict_id)
        return repo.update(conflict_id, payload)

    @classmethod
    def list_conflicts(
        cls,
        event_id: Optional[UUID] = None,
        resolution_status: Optional[str] = None,
    ) -> List[ConflictResponse]:
        """List conflicts with optional filtering."""
        repo = get_conflict_repository()
        return repo.list_all(event_id=event_id, resolution_status=resolution_status)

    @classmethod
    def clear_db(cls) -> None:
        """Reset repository store for testing isolation."""
        repo = get_conflict_repository()
        try:
            repo.clear()
        except NotImplementedError:
            pass
