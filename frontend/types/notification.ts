export type NotificationCategory = 'Review' | 'Conflict' | 'Evidence' | 'Progress' | 'Schedule'

export interface NotificationItem {
  id: string
  title: string
  description: string
  category: NotificationCategory
  timestamp: string
  is_read: boolean
  link_url?: string
}
