from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


class UserRole(str, Enum):
    """User role classification."""

    ADMIN = "ADMIN"
    PLANNER = "PLANNER"
    SUPERVISOR = "SUPERVISOR"
    SYSTEM = "SYSTEM"


class UserBase(BaseModel):
    """Base fields for a User entity."""

    username: str = Field(..., description="Unique username", min_length=1, max_length=100)
    email: str = Field(..., description="User email address", min_length=3, max_length=255)
    full_name: Optional[str] = Field(None, description="User full display name")
    role: UserRole = Field(default=UserRole.PLANNER, description="User system role")
    is_active: bool = Field(default=True, description="Account active status")


class UserCreate(UserBase):
    """Schema for creating a User."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a User."""

    username: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=3, max_length=255)
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for User responses."""

    id: UUID = Field(default_factory=uuid4, description="Unique user UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def user_id(self) -> UUID:
        """ER diagram terminology alias for user ID."""
        return self.id

    model_config = ConfigDict(from_attributes=True)
