CREATE TABLE field_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id UUID NOT NULL,

    submitted_by UUID NOT NULL,

    report_type VARCHAR(100),

    report_date DATE,

    raw_text TEXT,

    status VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_reports_project
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id),

    CONSTRAINT fk_reports_user
        FOREIGN KEY (submitted_by)
        REFERENCES users(user_id)
);