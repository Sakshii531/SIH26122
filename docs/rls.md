# SIH26122 - Row Level Security (RLS)

## field_reports

Supervisor:
- SELECT
- INSERT

Planner:
- SELECT

## evidence

Supervisor:
- SELECT
- INSERT

Planner:
- SELECT

## planner_reviews

Planner:
- SELECT
- INSERT
- UPDATE

Supervisor:
- SELECT

## conflicts

Planner:
- SELECT
- INSERT
- UPDATE

Supervisor:
- SELECT

## actual_progress

Planner:
- SELECT
- INSERT
- UPDATE

Supervisor:
- SELECT

## audit_logs

Planner:
- SELECT

Supervisor:
- No Access

## Read-Only Tables

Both Supervisor and Planner can SELECT:

- users
- projects
- schedules
- wbs
- activities
- extracted_progress_events
- activity_matches