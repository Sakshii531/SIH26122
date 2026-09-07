import { MOCK_REVIEW_QUEUE } from '@/mock/reviews'
import {
  ApproveMatchPayload,
  CorrectMatchPayload,
  FlagConflictPayload,
  RejectMatchPayload,
  ReviewQueueItem,
} from '@/types/review'
import { auditService } from './auditService'

let localReviewQueue: ReviewQueueItem[] = [...MOCK_REVIEW_QUEUE]

export const reviewService = {
  async getPendingReviews(): Promise<ReviewQueueItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    return localReviewQueue.filter((item) => item.status === 'Needs Review')
  },

  async getAllReviews(): Promise<ReviewQueueItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    return [...localReviewQueue]
  },

  async getReviewById(id: string): Promise<ReviewQueueItem | null> {
    await new Promise((resolve) => setTimeout(resolve, 100))
    return localReviewQueue.find((item) => item.id === id) || null
  },

  async approveMatch(payload: ApproveMatchPayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const item = localReviewQueue.find((r) => r.id === payload.match_id)
    if (!item) return { success: false, error: 'Review item not found.' }

    item.status = 'Approved'

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: 'Planner User',
      user_role: 'Planner',
      action: 'Match Approved',
      entity: 'ActivityMatch',
      entity_id: payload.match_id,
      details: {
        suggested_code: item.suggested_activity_code,
        activity_name: item.suggested_activity_name,
        confidence: item.confidence_score,
        notes: payload.notes || 'Approved by planner',
      },
    })

    return { success: true }
  },

  async correctMatch(payload: CorrectMatchPayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const item = localReviewQueue.find((r) => r.id === payload.match_id)
    if (!item) return { success: false, error: 'Review item not found.' }

    const originalCode = item.suggested_activity_code
    item.suggested_activity_id = payload.corrected_activity_id
    item.suggested_activity_code = payload.corrected_activity_code
    item.suggested_activity_name = payload.corrected_activity_name
    item.status = 'Corrected'

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: 'Planner User',
      user_role: 'Planner',
      action: 'Match Corrected',
      entity: 'PlannerReview',
      entity_id: payload.match_id,
      details: {
        original_code: originalCode,
        corrected_code: payload.corrected_activity_code,
        corrected_name: payload.corrected_activity_name,
        notes: payload.notes || 'Manually corrected by planner',
      },
    })

    return { success: true }
  },

  async rejectMatch(payload: RejectMatchPayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const item = localReviewQueue.find((r) => r.id === payload.match_id)
    if (!item) return { success: false, error: 'Review item not found.' }

    item.status = 'Rejected'

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: 'Planner User',
      user_role: 'Planner',
      action: 'Match Rejected',
      entity: 'PlannerReview',
      entity_id: payload.match_id,
      details: {
        activity_code: item.suggested_activity_code,
        rejection_reason: payload.reason,
        notes: payload.notes || '',
      },
    })

    return { success: true }
  },

  async flagConflict(payload: FlagConflictPayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 200))
    const item = localReviewQueue.find((r) => r.id === payload.match_id)
    if (!item) return { success: false, error: 'Review item not found.' }

    item.status = 'Conflict'

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: 'Planner User',
      user_role: 'Planner',
      action: 'Conflict Created',
      entity: 'Conflict',
      entity_id: `conf-${Date.now()}`,
      details: {
        activity_code: item.suggested_activity_code,
        title: payload.conflict_title,
        severity: payload.severity,
        description: payload.conflict_description,
      },
    })

    return { success: true }
  },
}
