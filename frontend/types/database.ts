export type UserRole = 'Planner' | 'Supervisor' | 'Admin'

export interface User {
  id: string
  user_id: string // Auth user id mapping
  email: string
  full_name: string
  role: UserRole
  discipline?: string
  project_id?: string
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  code: string
  name: string
  description?: string
  location: string
  client: string
  contractor: string
  start_date: string
  end_date: string
  status: 'Active' | 'On Hold' | 'Completed'
  created_at: string
}

export interface Schedule {
  id: string
  project_id: string
  version: string
  source: 'Primavera P6' | 'MS Project' | 'Excel'
  baseline_date: string
  status: 'Active' | 'Superseded' | 'Draft'
  total_activities: number
  created_at: string
}

export interface WBSNode {
  id: string
  project_id: string
  code: string
  name: string
  level: number
  parent_id?: string | null
  discipline?: string
}

export type ActivityDiscipline =
  | 'Piping'
  | 'Civil'
  | 'Mechanical'
  | 'Electrical'
  | 'Instrumentation'
  | 'Structural'
  | 'HVAC'

export type ActivityStatus =
  | 'Not Started'
  | 'In Progress'
  | 'Completed'
  | 'Delayed'
  | 'Blocked'
  | 'Under Review'

export interface Activity {
  id: string
  project_id: string
  schedule_id: string
  wbs_id: string
  wbs_code: string
  activity_code: string // e.g. "PIP-L5-024"
  activity_name: string
  description: string
  discipline: ActivityDiscipline
  level: 'L5' | 'L6'
  unit_of_measure: string
  planned_quantity: number
  actual_quantity: number
  planned_start: string
  planned_finish: string
  actual_start?: string | null
  actual_finish?: string | null
  progress_percentage: number
  planned_progress_percentage: number
  status: ActivityStatus
  weightage: number // weight in project progress (0-100)
  location: string
  zone_area?: string
  created_at: string
  updated_at: string
}

export type ReportSourceType = 'Text' | 'Voice' | 'DPR' | 'Excel' | 'PDF' | 'Photo'

export interface FieldReport {
  id: string
  project_id: string
  submitted_by_id: string
  submitted_by_name: string
  report_date: string
  source_type: ReportSourceType
  file_name?: string
  raw_text: string
  transcription_text?: string
  status: 'Submitted' | 'Processing' | 'Extracted' | 'Matched' | 'Reviewed' | 'Rejected'
  created_at: string
}

export interface Evidence {
  id: string
  report_id: string
  activity_id?: string | null
  file_name: string
  file_type: 'Photo' | 'PDF' | 'Excel' | 'Document' | 'Voice' | 'Other'
  file_url: string
  file_size_bytes?: number
  uploaded_by_id: string
  uploaded_by_name: string
  uploaded_at: string
  caption?: string
  gps_coordinates?: string
  validation_status: 'Pending' | 'Verified' | 'Rejected'
  validation_notes?: string
  validated_by_name?: string
  validated_at?: string
}

export interface ExtractedProgressEvent {
  id: string
  report_id: string
  extracted_activity_desc: string
  discipline: ActivityDiscipline
  work_type: string
  location?: string
  reported_progress_percent?: number
  reported_quantity?: number
  actual_start?: string
  actual_finish?: string
  event_date: string
  raw_snippet: string
  created_at: string
}

export interface ActivityMatch {
  id: string
  extracted_event_id: string
  suggested_activity_id: string
  suggested_activity_code: string
  suggested_activity_name: string
  discipline: ActivityDiscipline
  confidence_score: number // 0 to 100
  match_reasoning: string
  is_high_confidence: boolean // >= 70%
  auto_linked: boolean
  status: 'Needs Review' | 'Approved' | 'Corrected' | 'Rejected' | 'Conflict'
  created_at: string
}

export interface PlannerReview {
  id: string
  match_id: string
  planner_id: string
  planner_name: string
  action: 'Approve' | 'Correct' | 'Reject' | 'Flag Conflict'
  original_suggested_activity_id: string
  corrected_activity_id?: string | null
  rejection_reason?: string | null
  review_notes?: string
  created_at: string
}

export type ConflictType =
  | 'Progress Mismatch'
  | 'Date Conflict'
  | 'Duplicate Activity'
  | 'Contradictory Report'
  | 'Schedule Mismatch'

export type ConflictSeverity = 'Critical' | 'High' | 'Medium' | 'Low'

export interface Conflict {
  id: string
  project_id: string
  activity_id: string
  activity_code: string
  activity_name: string
  report_id?: string
  conflict_type: ConflictType
  severity: ConflictSeverity
  title: string
  description: string
  reported_value: string
  current_system_value: string
  detected_at: string
  status: 'Open' | 'Under Review' | 'Resolved' | 'Rejected'
  resolution_notes?: string
  resolved_by_name?: string
  resolved_at?: string
}

export interface ActualProgress {
  id: string
  activity_id: string
  activity_code: string
  activity_name: string
  progress_percentage: number
  quantity_completed?: number
  actual_start?: string
  actual_finish?: string
  progress_date: string
  source_report_id: string
  source_report_title: string
  evidence_count: number
  validated_by_id: string
  validated_by_name: string
  notes?: string
  created_at: string
}

export type AuditActionType =
  | 'Report Submitted'
  | 'Activity Extracted'
  | 'Activity Matched'
  | 'Match Approved'
  | 'Match Corrected'
  | 'Match Rejected'
  | 'Conflict Created'
  | 'Conflict Resolved'
  | 'Evidence Verified'
  | 'Evidence Rejected'
  | 'Progress Updated'

export interface AuditLog {
  id: string
  timestamp: string
  user_id: string
  user_name: string
  user_role: UserRole
  action: AuditActionType
  entity: 'FieldReport' | 'ActivityMatch' | 'PlannerReview' | 'Conflict' | 'Evidence' | 'ActualProgress' | 'Activity'
  entity_id: string
  details: Record<string, any>
  ip_address?: string
}
