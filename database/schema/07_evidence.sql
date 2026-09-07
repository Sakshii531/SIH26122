CREATE TABLE evidence (
    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    report_id UUID NOT NULL,

    evidence_type VARCHAR(100),

    file_url TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_evidence_report
        FOREIGN KEY (report_id)
        REFERENCES field_reports(report_id)
);