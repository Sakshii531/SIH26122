import { MOCK_AUDIT_LOGS } from '@/mock/auditLogs'
import { AuditFilters } from '@/types/audit'
import { AuditLog } from '@/types/database'

let localAuditLogs: AuditLog[] = [...MOCK_AUDIT_LOGS]

export const auditService = {
  async getAuditLogs(filters?: AuditFilters): Promise<AuditLog[]> {
    await new Promise((resolve) => setTimeout(resolve, 150))
    let logs = [...localAuditLogs]

    if (!filters) return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

    if (filters.action && filters.action !== 'All') {
      logs = logs.filter((l) => l.action === filters.action)
    }

    if (filters.entity && filters.entity !== 'All') {
      logs = logs.filter((l) => l.entity === filters.entity)
    }

    if (filters.user_role) {
      logs = logs.filter((l) => l.user_role === filters.user_role)
    }

    if (filters.search_query) {
      const q = filters.search_query.toLowerCase()
      logs = logs.filter(
        (l) =>
          l.user_name.toLowerCase().includes(q) ||
          l.action.toLowerCase().includes(q) ||
          l.entity_id.toLowerCase().includes(q) ||
          JSON.stringify(l.details).toLowerCase().includes(q)
      )
    }

    return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  },

  async logAction(entry: AuditLog): Promise<void> {
    localAuditLogs.unshift(entry)
  },
}
