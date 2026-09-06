CREATE TABLE actual_progress (
    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    activity_id UUID NOT NULL,

    progress_value NUMERIC,

    progress_date DATE,

    actual_start DATE,

    actual_finish DATE,

    status VARCHAR(50),

    validated_by UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_progress_activity
        FOREIGN KEY (activity_id)
        REFERENCES activities(activity_id),

    CONSTRAINT fk_progress_user
        FOREIGN KEY (validated_by)
        REFERENCES users(user_id)
);