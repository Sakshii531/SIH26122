CREATE TABLE schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id UUID NOT NULL,

    name VARCHAR(200) NOT NULL,

    source_type VARCHAR(100) NOT NULL,

    baseline_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_schedules_project
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
);