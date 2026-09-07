import { ActivityDiscipline, ActualProgress } from './database'

export interface ProgressSummary {
  planned_progress: number
  actual_progress: number
  variance: number // actual - planned
  overall_status: 'On Track' | 'Delayed' | 'Critical Delay' | 'Ahead'
  last_updated: string
  total_activities: number
  completed_activities: number
  in_progress_activities: number
  delayed_activities: number
  blocked_activities: number
}

export interface DisciplineProgress {
  discipline: ActivityDiscipline
  total_activities: number
  planned_progress: number
  actual_progress: number
  variance: number
  status: 'Healthy' | 'Needs Attention' | 'Critical'
}

export interface WBSProgress {
  wbs_code: string
  wbs_name: string
  planned_progress: number
  actual_progress: number
  variance: number
  activities_count: number
}

export interface ProgressTimelineItem extends ActualProgress {
  discipline: ActivityDiscipline
  location: string
}
