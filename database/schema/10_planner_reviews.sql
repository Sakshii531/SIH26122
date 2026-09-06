CREATE TABLE planner_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    match_id UUID NOT NULL,

    reviewed_by UUID NOT NULL,

    corrected_activity_id UUID,

    decision VARCHAR(100),

    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_reviews_match
        FOREIGN KEY (match_id)
        REFERENCES activity_matches(match_id),

    CONSTRAINT fk_reviews_user
        FOREIGN KEY (reviewed_by)
        REFERENCES users(user_id),

    CONSTRAINT fk_reviews_activity
        FOREIGN KEY (corrected_activity_id)
        REFERENCES activities(activity_id)
);