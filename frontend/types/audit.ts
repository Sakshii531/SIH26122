import { AuditActionType, AuditLog, UserRole } from './database'

export interface AuditLogItem extends AuditLog {}

export interface AuditFilters {
  user_name?: string
  user_role?: UserRole
  action?: AuditActionType | 'All'
  entity?: string | 'All'
  date_from?: string
  date_to?: string
  search_query?: string
}
