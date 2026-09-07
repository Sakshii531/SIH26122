# SIH26122 - Audit Trail

## Purpose

The audit trail records important actions performed by users in the system to ensure accountability, traceability, and transparency.

---

## Audit Log Table

Table: audit_logs

Fields:

- audit_id
- user_id
- entity_type
- entity_id
- action
- details
- created_at

---

## Actions To Be Logged

### Field Reports

- Field report created
- Field report updated
- Field report status changed

### Evidence

- Evidence uploaded
- Evidence updated

### Activity Matches

- Activity match reviewed
- Activity match corrected

### Planner Reviews

- Planner review created
- Planner review updated

### Conflicts

- Conflict created
- Conflict resolved
- Conflict status updated

### Actual Progress

- Actual progress created
- Actual progress updated
- Progress validation completed

### User Actions

- User login
- User logout

---

## Audit Information Captured

For every audit record:

- User who performed the action
- Entity affected
- Entity identifier
- Action performed
- Additional details
- Timestamp of action

---

## Benefits

- Accountability
- Traceability
- Security monitoring
- Change history
- Project governance

---

## Notes

- Audit records are system generated.
- Audit records must not be manually edited.
- Audit records should be retained for the lifetime of the project.