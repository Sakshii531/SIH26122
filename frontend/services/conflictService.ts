import { MOCK_CONFLICTS } from '@/mock/conflicts'
import { ConflictItem, ResolveConflictPayload } from '@/types/conflict'
import { auditService } from './auditService'

let localConflicts: ConflictItem[] = [...MOCK_CONFLICTS]

export const conflictService = {
  async getConflicts(statusFilter?: string): Promise<ConflictItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 120))
    if (!statusFilter || statusFilter === 'All') return [...localConflicts]
    return localConflicts.filter((c) => c.status === statusFilter)
  },

  async getConflictById(id: string): Promise<ConflictItem | null> {
    await new Promise((resolve) => setTimeout(resolve, 80))
    return localConflicts.find((c) => c.id === id) || null
  },

  async resolveConflict(payload: ResolveConflictPayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const conflict = localConflicts.find((c) => c.id === payload.conflict_id)
    if (!conflict) return { success: false, error: 'Conflict record not found.' }

    conflict.status = 'Resolved'
    conflict.resolution_notes = payload.resolution_notes
    conflict.resolved_by_name = payload.planner_name
    conflict.resolved_at = new Date().toISOString()

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: payload.planner_name,
      user_role: 'Planner',
      action: 'Conflict Resolved',
      entity: 'Conflict',
      entity_id: payload.conflict_id,
      details: {
        activity_code: conflict.activity_code,
        conflict_type: conflict.conflict_type,
        action: payload.resolution_action,
        notes: payload.resolution_notes,
      },
    })

    return { success: true }
  },
}
