from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository contract defining standard CRUD operations."""

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Retrieve an entity by its UUID."""
        pass

    @abstractmethod
    def list_all(self) -> List[T]:
        """List all entities."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Create or replace an entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its UUID."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all entities from the repository (testing isolation)."""
        pass
