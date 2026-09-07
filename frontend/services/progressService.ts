import { MOCK_DASHBOARD_DATA } from '@/mock/dashboard'
import { DisciplineProgress, ProgressSummary, ProgressTimelineItem } from '@/types/progress'

export const progressService = {
  async getProgressSummary(): Promise<ProgressSummary> {
    await new Promise((resolve) => setTimeout(resolve, 120))
    return { ...MOCK_DASHBOARD_DATA.overall_progress }
  },

  async getDisciplineProgress(): Promise<DisciplineProgress[]> {
    await new Promise((resolve) => setTimeout(resolve, 120))
    return [...MOCK_DASHBOARD_DATA.discipline_progress]
  },

  async getProgressTimeline(): Promise<ProgressTimelineItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    return [
      {
        id: 'prog-001',
        activity_id: 'act-001',
        activity_code: 'PIP-L5-024',
        activity_name: 'Spool 24-XX Erection & Alignment',
        discipline: 'Piping',
        location: 'Zone 2 - Distillation Unit',
        progress_percentage: 72,
        quantity_completed: 324,
        actual_start: '2026-08-18',
        progress_date: '2026-09-03',
        source_report_id: 'rep-084',
        source_report_title: 'DPR - 03 Sep (Shift A)',
        evidence_count: 2,
        validated_by_id: 'usr-pln-01',
        validated_by_name: 'Vikram Mehta (Planner)',
        notes: 'Piping spool fit-up completed and approved by QA inspection',
        created_at: '2026-09-03T18:00:00Z',
      },
      {
        id: 'prog-002',
        activity_id: 'act-002',
        activity_code: 'CIV-L5-102',
        activity_name: 'Compressor Foundation Concrete Pour',
        discipline: 'Civil',
        location: 'Zone 1 - Compressor Shed',
        progress_percentage: 100,
        quantity_completed: 280,
        actual_start: '2026-08-02',
        actual_finish: '2026-09-02',
        progress_date: '2026-09-02',
        source_report_id: 'rep-086',
        source_report_title: 'Excel DPR - Civil Daily Log #119',
        evidence_count: 1,
        validated_by_id: 'usr-pln-01',
        validated_by_name: 'Vikram Mehta (Planner)',
        notes: 'Monolithic concrete pour cured and passed 28-day cube strength test (38.5 MPa)',
        created_at: '2026-09-02T19:30:00Z',
      },
      {
        id: 'prog-003',
        activity_id: 'act-004',
        activity_code: 'ELE-L6-210',
        activity_name: 'Cable Tray Installation - 33kV Substation',
        discipline: 'Electrical',
        location: 'Zone 4 - Substation 3',
        progress_percentage: 60,
        quantity_completed: 510,
        actual_start: '2026-08-22',
        progress_date: '2026-09-01',
        source_report_id: 'rep-081',
        source_report_title: 'DPR - 01 Sep Electrical',
        evidence_count: 1,
        validated_by_id: 'usr-pln-01',
        validated_by_name: 'Vikram Mehta (Planner)',
        notes: 'GI cable trays anchored to ceiling vault with earthing bonding',
        created_at: '2026-09-01T17:00:00Z',
      },
    ]
  },
}
