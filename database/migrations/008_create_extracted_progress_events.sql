CREATE TABLE extracted_progress_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_id UUID NOT NULL,

    activity_description TEXT,

    discipline VARCHAR(100),

    location VARCHAR(200),

    actual_start DATE,

    actual_finish DATE,

    progress_value NUMERIC,

    status VARCHAR(50),

    extracted_text TEXT,

    extraction_status VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_events_report
        FOREIGN KEY (report_id)
        REFERENCES field_reports(report_id)
);