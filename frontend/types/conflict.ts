import { ConflictSeverity, ConflictType } from './database'

export interface ConflictItem {
  id: string
  project_id: string
  activity_id: string
  activity_code: string
  activity_name: string
  report_id?: string
  report_title?: string
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
  evidence_count?: number
}

export interface ResolveConflictPayload {
  conflict_id: string
  planner_id: string
  planner_name: string
  resolution_action: 'Accept Reported' | 'Maintain Existing' | 'Custom Adjustment'
  resolution_notes: string
  new_progress_percent?: number
}
