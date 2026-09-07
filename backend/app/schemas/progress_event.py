from __future__ import annotations

from app.schemas.actual_progress import (
    ActualProgressBase,
    ActualProgressCreate,
    ActualProgressResponse,
)

# Backward compatibility aliases for progress_event module
ProgressEventBase = ActualProgressBase
ProgressEventCreate = ActualProgressCreate
ProgressEventResponse = ActualProgressResponse
