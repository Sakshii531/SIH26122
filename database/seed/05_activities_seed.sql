INSERT INTO activities (
    activity_id,
    wbs_id,
    activity_code,
    name,
    level,
    discipline,
    planned_start,
    planned_finish,
    duration,
    status
)
VALUES
(
    '44444444-4444-4444-4444-444444444441',
    '33333333-3333-3333-3333-333333333331',
    'ACT-001',
    'Clear Site',
    1,
    'Civil',
    '2026-09-01',
    '2026-09-03',
    3,
    'Planned'
),
(
    '44444444-4444-4444-4444-444444444442',
    '33333333-3333-3333-3333-333333333333',
    'ACT-002',
    'Excavate Earth',
    2,
    'Civil',
    '2026-09-04',
    '2026-09-10',
    7,
    'In Progress'
),
(
    '44444444-4444-4444-4444-444444444443',
    '33333333-3333-3333-3333-333333333333',
    'ACT-003',
    'Compact Soil',
    2,
    'Civil',
    '2026-09-11',
    '2026-09-13',
    3,
    'Planned'
);