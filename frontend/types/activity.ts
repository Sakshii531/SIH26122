import { Activity, ActivityDiscipline, ActivityStatus, ActualProgress, Evidence, FieldReport } from './database'

export interface ActivityFilterOptions {
  search?: string
  discipline?: ActivityDiscipline | 'All'
  status?: ActivityStatus | 'All'
  wbs?: string | 'All'
  level?: 'L5' | 'L6' | 'All'
}

export interface ActivityDetail extends Activity {
  parent_wbs_name?: string
  reports: FieldReport[]
  evidence: Evidence[]
  actual_progress_history: ActualProgress[]
  open_conflicts_count: number
}
