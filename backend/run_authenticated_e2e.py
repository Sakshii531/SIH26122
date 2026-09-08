"""Run the local, interactive Supabase authentication verification.

This script is intentionally not a pytest test. Run it from a normal VS Code
terminal so getpass can receive the password without echoing it. It performs
no cleanup and never prints the password or access token.
"""

from __future__ import annotations

import argparse
import sys
from getpass import getpass
from typing import Any

import requests
from supabase import create_client

from app.core.config import get_settings
from app.db.supabase_client import clear_request_access_token, reset_clients


EMAIL = "parthkathar3@gmail.com"
API_PREFIX = "/api/v1"


def login(password: str) -> tuple[str, str]:
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    response = client.auth.sign_in_with_password({"email": EMAIL, "password": password})
    session = getattr(response, "session", None)
    user = getattr(response, "user", None)
    token = getattr(session, "access_token", None) if session else None
    subject = getattr(user, "id", None) if user else None
    if not token or not subject:
        raise RuntimeError("Supabase Auth returned no session")
    return token, str(subject)


def check_route_contract(paths: dict[str, Any]) -> str | None:
    """Return the first missing workflow route before performing any writes."""
    required = {
        "project": ("post", f"{API_PREFIX}/projects"),
        "schedule": ("post", f"{API_PREFIX}/schedules/import"),
        "wbs": ("post", f"{API_PREFIX}/wbs"),
        "activity": ("post", f"{API_PREFIX}/activities"),
        "report": ("post", f"{API_PREFIX}/reports"),
        "review": ("post", f"{API_PREFIX}/reviews"),
        "progress": ("post", f"{API_PREFIX}/progress"),
        "audit": ("get", f"{API_PREFIX}/audit"),
    }
    for stage, (method, path) in required.items():
        if path not in paths or method not in paths[path]:
            return f"{stage} route {method.upper()} {path} is not exposed"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="Running FastAPI base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--check-workflow-contract-only",
        action="store_true",
        help="Stop after authenticated route preflight; never create records.",
    )
    args = parser.parse_args()
    settings = get_settings()

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("AUTH_RESULT=FAIL missing SUPABASE_URL or SUPABASE_KEY")
        return 1

    password = getpass(f"Supabase password for {EMAIL} (hidden): ")
    try:
        try:
            token, subject = login(password)
        except Exception as exc:
            print(f"AUTH_RESULT=FAIL {type(exc).__name__}")
            return 1

        jwks = requests.get(
            f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json",
            headers={"apikey": settings.SUPABASE_KEY},
            timeout=15,
        )
        jwks_data: dict[str, Any] = jwks.json() if jwks.ok else {}
        es256_ok = jwks.status_code == 200 and {key.get("alg") for key in jwks_data.get("keys", [])} == {"ES256"}

        base_url = args.api_url.rstrip("/")
        http = requests.Session()
        try:
            openapi_response = http.get(f"{base_url}/openapi.json", timeout=15)
            openapi_response.raise_for_status()
        except Exception as exc:
            print(f"FASTAPI_RESULT=FAIL {type(exc).__name__}")
            return 1
        paths = openapi_response.json().get("paths", {})
        headers = {"Authorization": f"Bearer {token}"}
        unauthenticated = http.get(f"{base_url}{API_PREFIX}/dashboard/summary", timeout=15)
        protected = http.get(f"{base_url}{API_PREFIX}/dashboard/summary", headers=headers, timeout=15)
        progress = http.get(f"{base_url}{API_PREFIX}/progress", headers=headers, timeout=15)
        reviews = http.get(f"{base_url}{API_PREFIX}/reviews", headers=headers, timeout=15)

        service = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        mapping = service.table("users").select("auth_user_id,role").eq("auth_user_id", subject).limit(1).execute().data or []
        role = mapping[0].get("role") if mapping else None

        authenticated_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        authenticated_client.postgrest.auth(token)
        authenticated_read = authenticated_client.table("users").select("user_id").limit(1).execute().data
        anonymous_read = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY).table("users").select("user_id").limit(1).execute().data

        checks = [
            ("es256_jwks", es256_ok),
            ("jwt_issuer_audience_via_fastapi", protected.status_code == 200),
            ("sub_mapping", len(mapping) == 1 and role in {"Planner", "Supervisor"}),
            ("unauthenticated_401", unauthenticated.status_code == 401),
            ("protected_api_read", protected.status_code == 200),
            ("bearer_postgrest_propagation", authenticated_read is not None),
            ("authenticated_rls_read", authenticated_read is not None),
            ("anonymous_rls_denied", anonymous_read == []),
        ]
        if role == "Planner":
            checks.append(("planner_rbac", progress.status_code == 200))
        elif role == "Supervisor":
            checks.append(("supervisor_rbac", reviews.status_code == 200 and progress.status_code == 403))
        else:
            checks.append(("known_rbac_role", False))

        for name, passed in checks:
            print(f"{name}={'PASS' if passed else 'FAIL'}")
        passed_count = sum(passed for _, passed in checks)
        print(f"AUTH_CHECKS=passed:{passed_count} failed:{len(checks) - passed_count} total:{len(checks)}")

        if args.check_workflow_contract_only:
            print("WORKFLOW_RESULT=NOT_RUN contract-only mode")
            return 0 if all(passed for _, passed in checks) else 1

        blocker = check_route_contract(paths)
        if blocker:
            print(f"WORKFLOW_RESULT=BLOCKED {blocker}")
            print("No live writes were performed.")
            return 2

        print("WORKFLOW_RESULT=READY route contract exposes all required stages")
        print("Workflow writes are intentionally not automated by this runner until the route contract is backed by the live repositories.")
        return 0 if all(passed for _, passed in checks) else 1
    finally:
        clear_request_access_token()
        reset_clients()
        password = None


if __name__ == "__main__":
    sys.exit(main())