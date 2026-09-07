import { MOCK_ACTIVITIES, MOCK_WBS_NODES } from '@/mock/activities'
import { MOCK_EVIDENCE } from '@/mock/evidence'
import { ActivityDetail, ActivityFilterOptions } from '@/types/activity'
import { Activity, WBSNode } from '@/types/database'

let localActivities: Activity[] = [...MOCK_ACTIVITIES]

export const activityService = {
  async getActivities(options?: ActivityFilterOptions): Promise<Activity[]> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    let list = [...localActivities]

    if (!options) return list

    if (options.search) {
      const q = options.search.toLowerCase()
      list = list.filter(
        (a) =>
          a.activity_code.toLowerCase().includes(q) ||
          a.activity_name.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          a.location.toLowerCase().includes(q)
      )
    }

    if (options.discipline && options.discipline !== 'All') {
      list = list.filter((a) => a.discipline === options.discipline)
    }

    if (options.status && options.status !== 'All') {
      list = list.filter((a) => a.status === options.status)
    }

    if (options.wbs && options.wbs !== 'All') {
      list = list.filter((a) => a.wbs_code.startsWith(options.wbs as string))
    }

    if (options.level && options.level !== 'All') {
      list = list.filter((a) => a.level === options.level)
    }

    return list
  },

  async getActivityById(id: string): Promise<ActivityDetail | null> {
    await new Promise((resolve) => setTimeout(resolve, 120))
    const activity = localActivities.find((a) => a.id === id)
    if (!activity) return null

    const evidence = MOCK_EVIDENCE.filter((e) => e.activity_id === id)

    return {
      ...activity,
      parent_wbs_name: 'Piping & Fabrication Unit',
      reports: [],
      evidence: evidence,
      actual_progress_history: [
        {
          id: `prog-hist-1`,
          activity_id: activity.id,
          activity_code: activity.activity_code,
          activity_name: activity.activity_name,
          progress_percentage: activity.progress_percentage,
          progress_date: '2026-09-03',
          source_report_id: 'rep-084',
          source_report_title: 'DPR - 03 Sep (Shift A)',
          evidence_count: evidence.length,
          validated_by_id: 'usr-pln-01',
          validated_by_name: 'Vikram Mehta (Planner)',
          created_at: '2026-09-03T18:00:00Z',
        },
      ],
      open_conflicts_count: id === 'act-001' ? 1 : 0,
    }
  },

  async getWBSNodes(): Promise<WBSNode[]> {
    await new Promise((resolve) => setTimeout(resolve, 80))
    return [...MOCK_WBS_NODES]
  },
}
