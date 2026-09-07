from __future__ import annotations

from app.schemas.audit_log import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogResponse,
)

# Backward compatibility aliases for audit_event module
AuditEventBase = AuditLogBase
AuditEventCreate = AuditLogCreate
AuditEventResponse = AuditLogResponse
