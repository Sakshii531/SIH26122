# SIH26122 - Role Based Access Control (RBAC)

## Roles

The system contains two roles:

1. Supervisor
2. Planner

---

## Supervisor Permissions

### Allowed Actions

- View users
- View projects
- View schedules
- View WBS
- View activities
- Create field reports
- View field reports
- Upload evidence
- View evidence
- View extracted progress events
- View activity matches
- View planner reviews
- View conflicts
- View actual progress

### Restricted Actions

- Cannot create planner reviews
- Cannot update planner reviews
- Cannot validate actual progress
- Cannot resolve conflicts

---

## Planner Permissions

### Allowed Actions

- View users
- View projects
- View schedules
- View WBS
- View activities
- View field reports
- View evidence
- View extracted progress events
- View activity matches
- Create planner reviews
- Update planner reviews
- Create conflicts
- Update conflicts
- Resolve conflicts
- Create actual progress
- Update actual progress
- View audit logs

### Restricted Actions

- Cannot submit field reports
- Cannot upload evidence

---

## Audit Logs

- Audit logs are system-generated records.
- Audit logs maintain accountability and traceability.
- Planner can view audit logs.
- No user role can directly modify audit log records.

---

## Purpose

This RBAC model ensures that:

- Supervisors are responsible for field reporting and evidence submission.
- Planners are responsible for reviewing AI-generated matches, resolving conflicts, and validating project progress.
- Access is restricted according to project responsibilities and workflow requirements.