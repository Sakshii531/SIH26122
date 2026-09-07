'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Bell,
  CheckCheck,
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  Layers,
  TrendingUp,
  X,
  ExternalLink,
} from 'lucide-react'
import { usePlanner } from '@/context/PlannerContext'
import { Drawer } from '@/components/common/Drawer'
import { Button } from '@/components/common/Button'
import { formatDateTime } from '@/lib/utils'

interface NotificationDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationDrawer({ isOpen, onClose }: NotificationDrawerProps) {
  const router = useRouter()
  const {
    notifications,
    unreadNotificationsCount,
    markNotificationAsRead,
    markAllNotificationsAsRead,
  } = usePlanner()

  const handleNotificationClick = (id: string, linkUrl?: string) => {
    markNotificationAsRead(id)
    if (linkUrl) {
      onClose()
      router.push(linkUrl)
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Review':
        return <CheckCircle2 className="w-4 h-4 text-amber-600" />
      case 'Conflict':
        return <AlertTriangle className="w-4 h-4 text-rose-600" />
      case 'Evidence':
        return <FileCheck2 className="w-4 h-4 text-blue-600" />
      case 'Progress':
        return <TrendingUp className="w-4 h-4 text-emerald-600" />
      default:
        return <Layers className="w-4 h-4 text-slate-600" />
    }
  }

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title="System Notifications"
      subtitle={`${unreadNotificationsCount} unread execution alerts`}
      width="md"
      footer={
        <div className="flex items-center justify-between w-full">
          {unreadNotificationsCount > 0 ? (
            <Button
              size="sm"
              variant="secondary"
              onClick={markAllNotificationsAsRead}
              leftIcon={<CheckCheck className="w-3.5 h-3.5" />}
            >
              Mark All as Read
            </Button>
          ) : (
            <span className="text-xs text-slate-400">All notifications caught up</span>
          )}
          <Button size="sm" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
      }
    >
      <div className="space-y-3">
        {notifications.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-xs">
            No notifications logged at this time.
          </div>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => handleNotificationClick(n.id, n.link_url)}
              className={`p-3 rounded-lg border transition-all cursor-pointer ${
                !n.is_read
                  ? 'bg-blue-50/40 border-blue-200/80 hover:bg-blue-50/70 shadow-xs'
                  : 'bg-white border-slate-200/80 hover:bg-slate-50 opacity-80'
              }`}
            >
              <div className="flex items-start gap-2.5">
                <div className="mt-0.5 shrink-0">{getCategoryIcon(n.category)}</div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-1">
                    <span
                      className={`text-xs font-semibold ${
                        !n.is_read ? 'text-slate-900' : 'text-slate-700'
                      }`}
                    >
                      {n.title}
                    </span>
                    {!n.is_read && (
                      <span className="h-1.5 w-1.5 rounded-full bg-blue-600 shrink-0" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-600 mt-0.5 line-clamp-2">
                    {n.description}
                  </p>
                  <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 text-[10px] text-slate-400 font-mono">
                    <span>{formatDateTime(n.timestamp)}</span>
                    {n.link_url && (
                      <span className="text-blue-600 font-medium inline-flex items-center gap-0.5">
                        View <ExternalLink className="w-2.5 h-2.5" />
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Drawer>
  )
}
