INSERT INTO audit_logs (
    audit_id,
    user_id,
    entity_type,
    entity_id,
    action,
    details
)
VALUES
(
    'cccccccc-cccc-cccc-cccc-ccccccccccc1',
    'b6b4d178-5dda-4ff6-80c7-a0f847b851bc',
    'field_report',
    '55555555-5555-5555-5555-555555555555',
    'CREATE',
    'Field report submitted by supervisor.'
),
(
    'cccccccc-cccc-cccc-cccc-ccccccccccc2',
    'aa2b84bb-0665-4399-a827-fa5aba396d77',
    'planner_review',
    '99999999-9999-9999-9999-999999999991',
    'APPROVE',
    'Planner approved matched activity.'
),
(
    'cccccccc-cccc-cccc-cccc-ccccccccccc3',
    'aa2b84bb-0665-4399-a827-fa5aba396d77',
    'actual_progress',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'VALIDATE',
    'Actual progress validated by planner.'
); 