INSERT INTO extracted_progress_events (
    event_id,
    report_id,
    activity_description,
    discipline,
    location,
    actual_start,
    actual_finish,
    progress_value,
    status,
    extracted_text,
    extraction_status
)
VALUES
(
    '77777777-7777-7777-7777-777777777771',
    '55555555-5555-5555-5555-555555555555',
    'Excavation completed',
    'Civil',
    'Zone A',
    '2026-09-04',
    '2026-09-07',
    40,
    'In Progress',
    'Excavation work completed for 200 meters',
    'Success'
),
(
    '77777777-7777-7777-7777-777777777772',
    '55555555-5555-5555-5555-555555555555',
    'Soil compaction started',
    'Civil',
    'Zone A',
    '2026-09-07',
    NULL,
    10,
    'Started',
    'Soil compaction started',
    'Success'
);