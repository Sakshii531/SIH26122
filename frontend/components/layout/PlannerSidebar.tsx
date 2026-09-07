'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  CheckSquare,
  Layers,
  TrendingUp,
  AlertTriangle,
  FileCheck2,
  History,
  LogOut,
  Building2,
  HardHat,
  ChevronRight,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { usePlanner } from '@/context/PlannerContext'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: number
  badgeVariant?: 'amber' | 'rose' | 'blue' | 'neutral'
}

export function PlannerSidebar({ onCloseMobile }: { onCloseMobile?: () => void }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()
  const { pendingReviewsCount, openConflictsCount, pendingEvidenceCount } = usePlanner()

  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      href: '/planner/dashboard',
      icon: LayoutDashboard,
    },
    {
      label: 'Review Queue',
      href: '/planner/review-queue',
      icon: CheckSquare,
      badge: pendingReviewsCount,
      badgeVariant: 'amber',
    },
    {
      label: 'Activities & WBS',
      href: '/planner/activities',
      icon: Layers,
    },
    {
      label: 'Actual Progress',
      href: '/planner/progress',
      icon: TrendingUp,
    },
    {
      label: 'Conflicts',
      href: '/planner/conflicts',
      icon: AlertTriangle,
      badge: openConflictsCount,
      badgeVariant: 'rose',
    },
    {
      label: 'Evidence',
      href: '/planner/evidence',
      icon: FileCheck2,
      badge: pendingEvidenceCount,
      badgeVariant: 'blue',
    },
    {
      label: 'Audit Trail',
      href: '/planner/audit-logs',
      icon: History,
    },
  ]

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <aside className="flex flex-col h-full bg-[#FFFFFF] text-slate-700 border-r border-slate-200/90 w-64 select-none shadow-[1px_0_3px_0_rgba(0,0,0,0.02)]">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 bg-white">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white font-bold shadow-xs">
          <Building2 className="w-4 h-4" />
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
            SIH26122 Bridge
          </span>
          <span className="text-xs font-bold text-slate-900 truncate">
            Planning & Execution
          </span>
        </div>
      </div>

      {/* Project Selector Indicator */}
      <div className="px-3.5 py-3 border-b border-slate-100 bg-slate-50/60">
        <div className="rounded-lg bg-white p-2.5 border border-slate-200/80 shadow-xs text-xs">
          <div className="flex items-center gap-1.5 text-slate-500 font-medium mb-1">
            <HardHat className="w-3.5 h-3.5 text-amber-500 shrink-0" />
            <span className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">Active Project</span>
          </div>
          <p className="font-semibold text-slate-900 truncate text-xs">
            Refinery Expansion Unit 4
          </p>
          <div className="flex items-center justify-between text-[11px] text-slate-400 mt-0.5">
            <span>Schedule Rev C (P6)</span>
            <span className="text-emerald-600 font-medium">Synced</span>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-2.5 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Planner Control
        </div>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onCloseMobile}
              className={cn(
                'group relative flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                isActive
                  ? 'bg-blue-50/90 text-blue-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900'
              )}
            >
              {isActive && (
                <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-sm bg-blue-600" />
              )}
              <div className="flex items-center gap-2.5 min-w-0">
                <Icon
                  className={cn(
                    'w-4 h-4 shrink-0 transition-colors',
                    isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
                  )}
                />
                <span className="truncate">{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span
                  className={cn(
                    'px-1.5 py-0.2 text-[11px] font-bold rounded-full border shrink-0',
                    isActive
                      ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : item.badgeVariant === 'amber'
                      ? 'bg-amber-50 text-amber-800 border-amber-200'
                      : item.badgeVariant === 'rose'
                      ? 'bg-rose-50 text-rose-800 border-rose-200'
                      : 'bg-blue-50 text-blue-800 border-blue-200'
                  )}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* User Profile & Logout Footer */}
      <div className="p-3 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center justify-between p-2 rounded-lg bg-white border border-slate-200/80 shadow-xs mb-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-blue-700 font-bold text-xs shrink-0">
              {user?.full_name ? user.full_name.charAt(0) : 'P'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-slate-900 truncate">
                {user?.full_name || 'Vikram Mehta'}
              </p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="inline-block px-1.5 py-0.2 text-[9px] font-semibold bg-emerald-50 text-emerald-700 rounded border border-emerald-200">
                  Planner
                </span>
                <span className="text-[10px] text-slate-400 truncate">
                  {user?.discipline || 'Controls'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors border border-transparent hover:border-rose-100"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  )
}
