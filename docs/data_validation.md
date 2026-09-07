# SIH26122 - Data Validation & Integrity

## Users

- user_id must be unique
- email must be unique
- email cannot be null
- name cannot be null
- role must be either Supervisor or Planner

---

## Projects

- project_id must be unique
- name cannot be null

---

## Schedules

- schedule_id must be unique
- project_id must reference an existing project
- name cannot be null

---

## WBS

- wbs_id must be unique
- schedule_id must reference an existing schedule
- parent_wbs_id must reference an existing WBS if provided
- code cannot be null
- name cannot be null
- level must be greater than or equal to 0

---

## Activities

- activity_id must be unique
- wbs_id must reference an existing WBS
- activity_code cannot be null
- name cannot be null
- duration must be greater than or equal to 0
- planned_finish should not be before planned_start

---

## Field Reports

- report_id must be unique
- project_id must reference an existing project
- submitted_by must reference an existing user

---

## Evidence

- evidence_id must be unique
- report_id must reference an existing field report

---

## Extracted Progress Events

- event_id must be unique
- report_id must reference an existing field report
- progress_value must be greater than or equal to 0

---

## Activity Matches

- match_id must be unique
- event_id must reference an existing extracted progress event
- activity_id must reference an existing activity
- confidence_score must be between 0 and 1

---

## Planner Reviews

- review_id must be unique
- match_id must reference an existing activity match
- reviewed_by must reference an existing user

---

## Conflicts

- conflict_id must be unique
- activity_id must reference an existing activity
- event_id must reference an existing extracted progress event

---

## Actual Progress

- progress_id must be unique
- activity_id must reference an existing activity
- progress_value must be greater than or equal to 0

---

## Audit Logs

- audit_id must be unique
- user_id must reference an existing user

---

## Integrity Rules

- All foreign key relationships must remain valid.
- Orphan records are not allowed.
- Duplicate primary keys are not allowed.
- Invalid role values are not allowed.
- Invalid date relationships should be rejected.