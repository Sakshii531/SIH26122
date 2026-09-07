'use client'

import React, { useState } from 'react'
import { usePathname } from 'next/navigation'
import { Bell, Menu, ShieldCheck } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { usePlanner } from '@/context/PlannerContext'
import { NotificationDrawer } from './NotificationDrawer'

interface TopNavProps {
  onToggleMobile: () => void
}

export function PlannerTopNav({ onToggleMobile }: TopNavProps) {
  const pathname = usePathname()
  const { user } = useAuth()
  const { unreadNotificationsCount } = usePlanner()
  const [notificationOpen, setNotificationOpen] = useState(false)

  const getPageTitle = (path: string): { title: string; subtitle: string } => {
    if (path.includes('/review-queue')) {
      return {
        title: 'Review Queue',
        subtitle: 'Validate low-confidence AI matches and field execution reports',
      }
    }
    if (path.includes('/activities')) {
      return {
        title: 'L5/L6 Activities & WBS',
        subtitle: 'Baseline schedule activities, hierarchy and actual status tracking',
      }
    }
    if (path.includes('/progress')) {
      return {
        title: 'Actual Progress Tracking',
        subtitle: 'Planned vs Actual progress metrics, variance and discipline curves',
      }
    }
    if (path.includes('/conflicts')) {
      return {
        title: 'Conflict Resolution',
        subtitle: 'Detect and resolve execution discrepancies between DPRs and schedules',
      }
    }
    if (path.includes('/evidence')) {
      return {
        title: 'Evidence Validation',
        subtitle: 'Inspect supporting site photos, test certificates, and DPR documents',
      }
    }
    if (path.includes('/audit-logs')) {
      return {
        title: 'System Audit Trail',
        subtitle: 'Immutable record of AI extractions, matches, and Planner decisions',
      }
    }
    return {
      title: 'Planner Dashboard',
      subtitle: 'Review project progress, AI activity matches, and execution updates',
    }
  }

  const { title, subtitle } = getPageTitle(pathname)

  return (
    <>
      <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-slate-200/90 bg-white px-4 sm:px-6 shadow-subtle">
        {/* Left: Mobile menu toggle + Page titles */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobile}
            className="lg:hidden rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div>
            <h1 className="text-sm sm:text-base font-bold text-slate-900 leading-tight">
              {title}
            </h1>
            <p className="hidden sm:block text-[11px] text-slate-500">{subtitle}</p>
          </div>
        </div>

        {/* Right: Project context + Notification bell + User chip */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Bridge Verified status badge */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/80 text-[11px] font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Bridge Active</span>
          </div>

          {/* Functional Notification Bell */}
          <button
            onClick={() => setNotificationOpen(true)}
            className="relative rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            aria-label="Open system notifications"
            title={`${unreadNotificationsCount} unread notifications`}
          >
            <Bell className="w-4 h-4" />
            {unreadNotificationsCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-blue-600 px-1 text-[9px] font-bold text-white shadow-xs">
                {unreadNotificationsCount}
              </span>
            )}
          </button>

          {/* User Profile Chip */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-white font-bold text-xs">
              {user?.full_name ? user.full_name.charAt(0) : 'P'}
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-xs font-semibold text-slate-900 truncate">
                {user?.full_name || 'Vikram Mehta'}
              </p>
              <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                Lead Planner
              </p>
            </div>
          </div>
        </div>
      </header>

      <NotificationDrawer
        isOpen={notificationOpen}
        onClose={() => setNotificationOpen(false)}
      />
    </>
  )
}
