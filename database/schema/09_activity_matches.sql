CREATE TABLE activity_matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    event_id UUID NOT NULL,

    activity_id UUID NOT NULL,

    confidence_score NUMERIC,

    match_status VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_matches_event
        FOREIGN KEY (event_id)
        REFERENCES extracted_progress_events(event_id),

    CONSTRAINT fk_matches_activity
        FOREIGN KEY (activity_id)
        REFERENCES activities(activity_id)
);