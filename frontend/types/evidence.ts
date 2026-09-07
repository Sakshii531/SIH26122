import { ActivityDiscipline, Evidence } from './database'

export interface EvidenceItem extends Evidence {
  report_title?: string
  activity_code?: string
  activity_name?: string
  discipline?: ActivityDiscipline
}

export interface VerifyEvidencePayload {
  evidence_id: string
  planner_id: string
  planner_name: string
  notes?: string
}

export interface RejectEvidencePayload {
  evidence_id: string
  planner_id: string
  planner_name: string
  reason: string
}
