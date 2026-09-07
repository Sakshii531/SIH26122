import { DisciplineProgress, ProgressSummary, WBSProgress } from '@/types/progress'

export interface DashboardMetrics {
  overall_progress: ProgressSummary
  pending_reviews_count: number
  high_confidence_count: number
  open_conflicts_count: number
  activities_updated_count: number
  evidence_pending_count: number
  confidence_distribution: {
    high: number // count
    medium: number // count
    low: number // count
  }
  discipline_progress: DisciplineProgress[]
  wbs_progress: WBSProgress[]
}

export const MOCK_DASHBOARD_DATA: DashboardMetrics = {
  overall_progress: {
    planned_progress: 64,
    actual_progress: 58,
    variance: -6.0,
    overall_status: 'Delayed',
    last_updated: '2026-09-06T18:00:00Z',
    total_activities: 48,
    completed_activities: 14,
    in_progress_activities: 22,
    delayed_activities: 8,
    blocked_activities: 4,
  },
  pending_reviews_count: 5,
  high_confidence_count: 27,
  open_conflicts_count: 3,
  activities_updated_count: 18,
  evidence_pending_count: 4,
  confidence_distribution: {
    high: 27,
    medium: 12,
    low: 5,
  },
  discipline_progress: [
    {
      discipline: 'Civil',
      total_activities: 12,
      planned_progress: 88,
      actual_progress: 85,
      variance: -3.0,
      status: 'Healthy',
    },
    {
      discipline: 'Piping',
      total_activities: 14,
      planned_progress: 68,
      actual_progress: 59,
      variance: -9.0,
      status: 'Needs Attention',
    },
    {
      discipline: 'Mechanical',
      total_activities: 8,
      planned_progress: 55,
      actual_progress: 42,
      variance: -13.0,
      status: 'Critical',
    },
    {
      discipline: 'Electrical',
      total_activities: 8,
      planned_progress: 48,
      actual_progress: 52,
      variance: +4.0,
      status: 'Healthy',
    },
    {
      discipline: 'Instrumentation',
      total_activities: 6,
      planned_progress: 30,
      actual_progress: 25,
      variance: -5.0,
      status: 'Needs Attention',
    },
  ],
  wbs_progress: [
    {
      wbs_code: '1.1',
      wbs_name: 'Civil & Structural Works',
      planned_progress: 82,
      actual_progress: 79,
      variance: -3.0,
      activities_count: 12,
    },
    {
      wbs_code: '1.2',
      wbs_name: 'Piping & Fabrication',
      planned_progress: 68,
      actual_progress: 59,
      variance: -9.0,
      activities_count: 14,
    },
    {
      wbs_code: '1.3',
      wbs_name: 'Mechanical & Equipment',
      planned_progress: 55,
      actual_progress: 42,
      variance: -13.0,
      activities_count: 8,
    },
    {
      wbs_code: '1.4',
      wbs_name: 'Electrical & Power Distribution',
      planned_progress: 48,
      actual_progress: 52,
      variance: +4.0,
      activities_count: 8,
    },
    {
      wbs_code: '1.5',
      wbs_name: 'Instrumentation & Controls',
      planned_progress: 30,
      actual_progress: 25,
      variance: -5.0,
      activities_count: 6,
    },
  ],
}
