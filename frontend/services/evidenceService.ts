import { MOCK_EVIDENCE } from '@/mock/evidence'
import { EvidenceItem, RejectEvidencePayload, VerifyEvidencePayload } from '@/types/evidence'
import { auditService } from './auditService'

let localEvidence: EvidenceItem[] = [...MOCK_EVIDENCE]

export const evidenceService = {
  async getEvidenceList(filterStatus?: string, filterType?: string): Promise<EvidenceItem[]> {
    await new Promise((resolve) => setTimeout(resolve, 120))
    let list = [...localEvidence]

    if (filterStatus && filterStatus !== 'All') {
      list = list.filter((e) => e.validation_status === filterStatus)
    }

    if (filterType && filterType !== 'All') {
      list = list.filter((e) => e.file_type === filterType)
    }

    return list
  },

  async getEvidenceById(id: string): Promise<EvidenceItem | null> {
    await new Promise((resolve) => setTimeout(resolve, 80))
    return localEvidence.find((e) => e.id === id) || null
  },

  async verifyEvidence(payload: VerifyEvidencePayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 180))
    const item = localEvidence.find((e) => e.id === payload.evidence_id)
    if (!item) return { success: false, error: 'Evidence not found.' }

    item.validation_status = 'Verified'
    item.validation_notes = payload.notes || 'Verified by planner'
    item.validated_by_name = payload.planner_name
    item.validated_at = new Date().toISOString()

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: payload.planner_name,
      user_role: 'Planner',
      action: 'Evidence Verified',
      entity: 'Evidence',
      entity_id: payload.evidence_id,
      details: {
        file_name: item.file_name,
        activity_code: item.activity_code,
        notes: payload.notes || '',
      },
    })

    return { success: true }
  },

  async rejectEvidence(payload: RejectEvidencePayload): Promise<{ success: boolean; error?: string }> {
    await new Promise((resolve) => setTimeout(resolve, 180))
    const item = localEvidence.find((e) => e.id === payload.evidence_id)
    if (!item) return { success: false, error: 'Evidence not found.' }

    item.validation_status = 'Rejected'
    item.validation_notes = payload.reason
    item.validated_by_name = payload.planner_name
    item.validated_at = new Date().toISOString()

    await auditService.logAction({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: payload.planner_id,
      user_name: payload.planner_name,
      user_role: 'Planner',
      action: 'Evidence Rejected',
      entity: 'Evidence',
      entity_id: payload.evidence_id,
      details: {
        file_name: item.file_name,
        activity_code: item.activity_code,
        reason: payload.reason,
      },
    })

    return { success: true }
  },
}
