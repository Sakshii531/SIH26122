-- =========================================================
-- SIH26122 - Row Level Security
-- Migration 015
-- =========================================================

-- 1. Private schema for RLS helper functions
CREATE SCHEMA IF NOT EXISTS private;

-- 2. Return the role of the currently authenticated user
CREATE OR REPLACE FUNCTION private.current_user_role()
RETURNS TEXT
LANGUAGE SQL
SECURITY DEFINER
STABLE
SET search_path = ''
AS $$
    SELECT role
    FROM public.users
    WHERE auth_user_id = (SELECT auth.uid())
    LIMIT 1;
$$;

-- Only authenticated users may execute the helper
REVOKE ALL ON FUNCTION private.current_user_role() FROM PUBLIC;
GRANT USAGE ON SCHEMA private TO authenticated;
GRANT EXECUTE ON FUNCTION private.current_user_role() TO authenticated;


-- =========================================================
-- 3. ENABLE RLS ON ALL 13 TABLES
-- =========================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wbs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.field_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.extracted_progress_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.planner_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conflicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.actual_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;


-- =========================================================
-- 4. USERS
-- =========================================================

CREATE POLICY "users_select_own"
ON public.users
FOR SELECT
TO authenticated
USING (
    auth_user_id = (SELECT auth.uid())
);


-- =========================================================
-- 5. PROJECTS
-- Planner: full management
-- Supervisor: read access
-- =========================================================

CREATE POLICY "projects_select_authenticated"
ON public.projects
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "projects_insert_planner"
ON public.projects
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "projects_update_planner"
ON public.projects
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "projects_delete_planner"
ON public.projects
FOR DELETE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 6. SCHEDULES
-- Planner: full management
-- Supervisor: read access
-- =========================================================

CREATE POLICY "schedules_select_authenticated"
ON public.schedules
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "schedules_insert_planner"
ON public.schedules
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "schedules_update_planner"
ON public.schedules
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "schedules_delete_planner"
ON public.schedules
FOR DELETE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 7. WBS
-- Planner: full management
-- Supervisor: read access
-- =========================================================

CREATE POLICY "wbs_select_authenticated"
ON public.wbs
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "wbs_insert_planner"
ON public.wbs
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "wbs_update_planner"
ON public.wbs
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "wbs_delete_planner"
ON public.wbs
FOR DELETE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 8. ACTIVITIES
-- Planner: full management
-- Supervisor: read access
-- =========================================================

CREATE POLICY "activities_select_authenticated"
ON public.activities
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "activities_insert_planner"
ON public.activities
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "activities_update_planner"
ON public.activities
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "activities_delete_planner"
ON public.activities
FOR DELETE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 9. FIELD REPORTS
-- Supervisor: create/update own reports
-- Planner: read all
-- =========================================================

CREATE POLICY "field_reports_select_authenticated"
ON public.field_reports
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "field_reports_insert_supervisor"
ON public.field_reports
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Supervisor'
    AND submitted_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
);

CREATE POLICY "field_reports_update_supervisor_own"
ON public.field_reports
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Supervisor'
    AND submitted_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
)
WITH CHECK (
    submitted_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
);


-- =========================================================
-- 10. EVIDENCE
-- Authenticated users can read.
-- Supervisor can add evidence to reports.
-- =========================================================

CREATE POLICY "evidence_select_authenticated"
ON public.evidence
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "evidence_insert_supervisor"
ON public.evidence
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Supervisor'
);


-- =========================================================
-- 11. EXTRACTED PROGRESS EVENTS
-- Authenticated users can read.
-- AI/backend writes these using trusted server access.
-- =========================================================

CREATE POLICY "events_select_authenticated"
ON public.extracted_progress_events
FOR SELECT
TO authenticated
USING (true);


-- =========================================================
-- 12. ACTIVITY MATCHES
-- Authenticated users can read.
-- AI/backend manages matches.
-- =========================================================

CREATE POLICY "matches_select_authenticated"
ON public.activity_matches
FOR SELECT
TO authenticated
USING (true);


-- =========================================================
-- 13. PLANNER REVIEWS
-- Planner: read/create/update reviews.
-- =========================================================

CREATE POLICY "planner_reviews_select_authenticated"
ON public.planner_reviews
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "planner_reviews_insert_planner"
ON public.planner_reviews
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
    AND reviewed_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
);

CREATE POLICY "planner_reviews_update_planner_own"
ON public.planner_reviews
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
    AND reviewed_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
)
WITH CHECK (
    reviewed_by = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
);


-- =========================================================
-- 14. CONFLICTS
-- Authenticated users can read.
-- Planner can resolve conflicts.
-- =========================================================

CREATE POLICY "conflicts_select_authenticated"
ON public.conflicts
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "conflicts_update_planner"
ON public.conflicts
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 15. ACTUAL PROGRESS
-- Authenticated users can read.
-- Planner can validate/update progress.
-- =========================================================

CREATE POLICY "actual_progress_select_authenticated"
ON public.actual_progress
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "actual_progress_insert_planner"
ON public.actual_progress
FOR INSERT
TO authenticated
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);

CREATE POLICY "actual_progress_update_planner"
ON public.actual_progress
FOR UPDATE
TO authenticated
USING (
    (SELECT private.current_user_role()) = 'Planner'
)
WITH CHECK (
    (SELECT private.current_user_role()) = 'Planner'
);


-- =========================================================
-- 16. AUDIT LOGS
-- Authenticated users can read their own audit records.
-- Backend/service role should create audit records.
-- =========================================================

CREATE POLICY "audit_logs_select_own"
ON public.audit_logs
FOR SELECT
TO authenticated
USING (
    user_id = (
        SELECT user_id
        FROM public.users
        WHERE auth_user_id = (SELECT auth.uid())
        LIMIT 1
    )
);