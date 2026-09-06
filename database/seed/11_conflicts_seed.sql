INSERT INTO conflicts (
    conflict_id,
    activity_id,
    event_id,
    conflict_type,
    description,
    status,
    resolution,
    resolved_by,
    resolved_at
)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '44444444-4444-4444-4444-444444444443',
    '77777777-7777-7777-7777-777777777772',
    'Progress Mismatch',
    'Extracted progress may not fully match planned activity.',
    'Resolved',
    'Reviewed and accepted by planner.',
    'aa2b84bb-0665-4399-a827-fa5aba396d77',
    NOW()
);