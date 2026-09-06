CREATE TABLE wbs (
    wbs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    schedule_id UUID NOT NULL,

    parent_wbs_id UUID,

    code VARCHAR(100) NOT NULL,

    name VARCHAR(200) NOT NULL,

    level INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_wbs_schedule
        FOREIGN KEY (schedule_id)
        REFERENCES schedules(schedule_id),

    CONSTRAINT fk_wbs_parent
        FOREIGN KEY (parent_wbs_id)
        REFERENCES wbs(wbs_id)
);