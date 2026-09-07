CREATE TABLE activities (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    wbs_id UUID NOT NULL,

    activity_code VARCHAR(100) NOT NULL,

    name VARCHAR(200) NOT NULL,

    level INTEGER,

    discipline VARCHAR(100),

    planned_start DATE,

    planned_finish DATE,

    duration INTEGER,

    status VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_activities_wbs
        FOREIGN KEY (wbs_id)
        REFERENCES wbs(wbs_id)
);