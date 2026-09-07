CREATE TABLE conflicts (
    conflict_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    activity_id UUID NOT NULL,

    event_id UUID NOT NULL,

    conflict_type VARCHAR(100),

    description TEXT,

    status VARCHAR(50),

    resolution TEXT,

    resolved_by UUID,

    resolved_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_conflicts_activity
        FOREIGN KEY (activity_id)
        REFERENCES activities(activity_id),

    CONSTRAINT fk_conflicts_event
        FOREIGN KEY (event_id)
        REFERENCES extracted_progress_events(event_id),

    CONSTRAINT fk_conflicts_user
        FOREIGN KEY (resolved_by)
        REFERENCES users(user_id)
);