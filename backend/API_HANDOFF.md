# SIH26122 Backend API Handoff

## Base URL and authentication

- Local base URL: `http://127.0.0.1:8000`
- API prefix: `/api/v1`
- OpenAPI: `/openapi.json`; interactive docs: `/docs`
- Liveness: `/health`; API status: `/api/v1/status`
- Protected routes require `Authorization: Bearer <Supabase access token>`.
- Deployment must use `DB_PROVIDER=supabase` with the Supabase URL, publishable/anon key, and service-role key supplied through the deployment environment. Never expose the service-role key to clients.
- Supabase tokens are validated with ES256 JWKS, issuer `<SUPABASE_URL>/auth/v1`, and audience `authenticated`.
- The JWT `sub` must map to `public.users.auth_user_id`. The mapped application role must be `Planner` or `Supervisor`.

## Permissions

- `Planner`: schedule import, project creation, progress reads/writes, review decisions, conflicts, and planner-protected operations.
- `Supervisor`: field-report submission, review reads/creation, and supervisor-protected operations.
- Both roles can use routes explicitly protected by general authentication.
- Unauthenticated requests return `401`; authenticated users without the required role return `403`.

## Major endpoints

- `GET /health`, `GET /api/v1/status`: public liveness/status.
- `GET /api/v1/projects`, `GET /api/v1/projects/{project_id}`: authenticated project reads.
- `POST /api/v1/projects`: Planner-protected project creation. Payload follows `ProjectCreate` (`name`, `code`, optional `description`, `location`).
- `POST /api/v1/schedules/import`: Planner-protected CSV/XLS/XLSX schedule import. Uses multipart `file` and optional `project_id`.
- `GET /api/v1/wbs`: Planner-protected read endpoint; currently returns the implemented read shape only.
- `GET /api/v1/activities`: Planner-protected activity read endpoint; supports optional project/schedule/WBS filters.
- `POST /api/v1/reports`: Supervisor-protected structured field report. Payload follows `FieldReportCreate`.
- `POST /api/v1/reports/upload`: Supervisor-protected multipart field-report upload.
- `POST /api/v1/reports/{report_id}/extraction`: protected extraction contract.
- `POST /api/v1/reports/{report_id}/matching`: protected activity-matching contract.
- `GET /api/v1/reviews`, `GET /api/v1/reviews/{review_id}`: Supervisor-protected review reads.
- `POST /api/v1/reviews`: Supervisor-protected review creation; payload follows `ReviewItemCreate`.
- `POST /api/v1/reviews/{review_id}/decision`: Planner-protected approval, rejection, or modification; payload follows `ReviewDecisionRequest`.
- `GET /api/v1/progress`, `GET /api/v1/progress/{progress_id}`: Planner-protected progress reads.
- `POST /api/v1/progress`: Planner-protected progress creation from a finalized review; payload follows `ProgressFromReviewCreate`.
- `GET/POST /api/v1/conflicts` and conflict update routes: Planner-protected conflict operations.
- `GET /api/v1/dashboard/summary`, `/dashboard/activities`, `/dashboard/recent-activity`, and project summary: authenticated dashboard reads.
- `GET /api/v1/audit`, `GET /api/v1/audit/{audit_id}`: authenticated audit reads.

## Uploads and errors

- Maximum upload size is configured by `MAX_UPLOAD_SIZE_MB` and defaults to 50 MB in the example configuration.
- Report upload formats are constrained by declared format: PDF/DOC/DOCX, TXT, XLS/XLSX/CSV, audio formats, and JPG/JPEG/PNG/WEBP as applicable.
- Schedule imports accept CSV, XLS, and XLSX.
- Uploads are bounded before full content processing; filenames are reduced to safe basename components and null bytes are removed.
- Typical errors: `400` invalid or empty input, `401` missing/invalid/expired authentication, `403` insufficient role or unmapped user, `404` missing record, `413` oversized upload, and `422` schema validation failure.
- Authentication and infrastructure failures return generic messages; passwords, tokens, service-role keys, stack traces, and raw database exception details are not API response data.

## Known limitations

- `POST /api/v1/wbs` is not exposed.
- `POST /api/v1/activities` is not exposed.
- The complete relational `Project -> Schedule -> WBS -> Activity` live workflow has not been verified.
- Schedule import currently supplies the implemented activity-ingestion path; it does not establish a verified complete relational hierarchy through those missing endpoints.
- These limitations are reported as-is and are not bypassed by this handoff.

## Verification status

- Deterministic backend suite: 268 passed.
- Safe Supabase/security/repository suite: 35 passed.
- Real authenticated Supabase E2E `9/9` result: not independently recorded in the repository handoff; run the local authenticated runner with a real user password before claiming that status.
