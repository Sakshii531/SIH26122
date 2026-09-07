import { ActivityDiscipline, ReportSourceType } from './database'

export interface ReviewQueueItem {
  id: string // match_id
  extracted_event_id: string
  report_id: string
  report_title: string
  report_source: ReportSourceType
  report_date: string
  submitted_by: string
  original_report_text: string

  extracted_activity_desc: string
  discipline: ActivityDiscipline
  work_type: string
  location: string
  reported_progress_percent?: number
  reported_quantity?: number
  actual_start?: string
  actual_finish?: string

  suggested_activity_id: string
  suggested_activity_code: string
  suggested_activity_name: string
  suggested_wbs_code: string
  suggested_wbs_name: string
  confidence_score: number
  match_reasoning: string

  evidence_attachments: Array<{
    id: string
    file_name: string
    file_type: string
    file_url: string
    caption?: string
  }>

  status: 'Needs Review' | 'Approved' | 'Corrected' | 'Rejected' | 'Conflict'
  created_at: string
}

export type RejectionReason =
  | 'Incorrect activity'
  | 'Insufficient evidence'
  | 'Duplicate report'
  | 'Invalid information'
  | 'Other'

export interface ApproveMatchPayload {
  match_id: string
  planner_id: string
  notes?: string
}

export interface CorrectMatchPayload {
  match_id: string
  planner_id: string
  corrected_activity_id: string
  corrected_activity_code: string
  corrected_activity_name: string
  notes?: string
}

export interface RejectMatchPayload {
  match_id: string
  planner_id: string
  reason: RejectionReason
  notes?: string
}

export interface FlagConflictPayload {
  match_id: string
  planner_id: string
  conflict_title: string
  conflict_description: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
}
