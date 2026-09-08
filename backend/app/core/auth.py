"""
Authentication and authorization for SIH26122 backend.

This module provides FastAPI dependencies for:
- JWT validation (Supabase-issued tokens)
- User context extraction
- Role-based access control (RBAC)

Architecture
------------
* Validates JWTs using the JWT_SECRET from Supabase
* Extracts user_id and role from the token payload
* Provides dependency functions for route protection
* Settings are injected via Depends(get_settings) so tests can override them

RBAC Roles (aligned with database RLS policies)
------------------------------------------------
* SUPERVISOR — Field staff; can create reports, view own data
* PLANNER — Engineering team; can review reports, update progress, manage schedules
* ADMIN — Full access to all operations

Usage in routes
---------------
    from app.core.auth import get_current_user, require_role

    @router.get("/protected")
    async def protected_endpoint(user: AuthUser = Depends(get_current_user)):
        return {"user_id": user.user_id, "role": user.role}

    @router.post("/admin-only")
    async def admin_endpoint(user: AuthUser = Depends(require_role("ADMIN"))):
        return {"message": "Admin operation"}
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.db.supabase_client import get_service_role_client

# ── Security scheme ───────────────────────────────────────────────────────────

security = HTTPBearer(auto_error=False)


# ── Data models ───────────────────────────────────────────────────────────────


class AuthUser(BaseModel):
    """Authenticated user context extracted from JWT."""

    user_id: str
    email: Optional[str] = None
    role: str = "USER"

    class Config:
        frozen = True


# ── Core dependency ───────────────────────────────────────────────────────────


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    settings: Settings = Depends(get_settings),
) -> AuthUser:
    """
    Extract and validate the current user from a JWT Bearer token.

    Settings are injected via Depends(get_settings) so tests can override
    them via app.dependency_overrides[get_settings] to supply a test JWT_SECRET
    without touching the lru_cache singleton.

    Raises
    ------
    HTTPException 401 — token missing, invalid, or expired
    HTTPException 500 — JWT_SECRET not configured on the server
    """
    # Production: validate JWT
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if not token or not token.strip():
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        if settings.DB_PROVIDER == "supabase":
            payload = _decode_supabase_token(token, settings)
        else:
            if not settings.JWT_SECRET:
                raise HTTPException(
                    status_code=500,
                    detail="JWT_SECRET is required for in_memory authentication",
                )
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing 'sub' claim")

    email: Optional[str] = payload.get("email")

    if settings.DB_PROVIDER == "supabase":
        role, mapped_email = _lookup_application_user(user_id)
        email = mapped_email or email
    else:
        role = _role_from_test_claims(payload)

    return AuthUser(user_id=user_id, email=email, role=role.upper())


@lru_cache(maxsize=1)
def _jwks_client(jwks_url: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(jwks_url)


def _decode_supabase_token(token: str, settings: Settings) -> dict:
    if not settings.SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL is not configured on server")

    jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    issuer = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=[settings.JWT_ALGORITHM],
            audience="authenticated",
            issuer=issuer,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase token: {exc}", headers={"WWW-Authenticate": "Bearer"})
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Unable to verify Supabase token: {exc}", headers={"WWW-Authenticate": "Bearer"})


def _lookup_application_user(auth_user_id: str) -> tuple[str, Optional[str]]:
    try:
        response = (
            get_service_role_client()
            .table("users")
            .select("auth_user_id,email,role")
            .eq("auth_user_id", auth_user_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to resolve authenticated user: {exc}")

    if not response.data:
        raise HTTPException(status_code=403, detail="Authenticated user is not provisioned in public.users")

    row = response.data[0]
    role = row.get("role")
    if role not in {"Planner", "Supervisor"}:
        raise HTTPException(status_code=403, detail="Authenticated user has no permitted application role")
    return role, row.get("email")


def _role_from_test_claims(payload: dict) -> str:
    role = "USER"
    if isinstance(payload.get("app_metadata"), dict):
        role = payload["app_metadata"].get("role", role)
    elif isinstance(payload.get("user_metadata"), dict):
        role = payload["user_metadata"].get("role", role)
    elif "role" in payload:
        role = payload["role"]
    return role


# ── Role-based dependencies ───────────────────────────────────────────────────


def require_role(*allowed_roles: str):
    """
    Dependency factory: user must have one of the allowed roles.

    Raises HTTPException 403 if the user's role is not in the allowed set.
    """
    allowed = {r.upper() for r in allowed_roles}

    async def check_role(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Insufficient permissions. "
                    f"Required role: {', '.join(sorted(allowed))}. "
                    f"Your role: {user.role}"
                ),
            )
        return user

    return check_role


# ── Convenience dependencies ──────────────────────────────────────────────────


async def require_supervisor(
    user: AuthUser = Depends(require_role("SUPERVISOR", "PLANNER", "ADMIN")),
) -> AuthUser:
    """Allow SUPERVISOR, PLANNER, or ADMIN."""
    return user


async def require_planner(
    user: AuthUser = Depends(require_role("PLANNER", "ADMIN")),
) -> AuthUser:
    """Allow PLANNER or ADMIN."""
    return user


async def require_admin(
    user: AuthUser = Depends(require_role("ADMIN")),
) -> AuthUser:
    """Allow ADMIN only."""
    return user
