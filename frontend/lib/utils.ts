import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { ActivityDiscipline, ActivityStatus, ConflictSeverity } from '@/types/database'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const CONFIDENCE_THRESHOLDS = {
  HIGH: 70,
  MEDIUM: 50,
} as const

export type ConfidenceTier = 'high' | 'medium' | 'low'

export function getConfidenceTier(score: number): ConfidenceTier {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH) return 'high'
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return 'medium'
  return 'low'
}

export function getConfidenceBadgeProps(score: number) {
  const tier = getConfidenceTier(score)
  switch (tier) {
    case 'high':
      return {
        label: `${score}% High`,
        className: 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-600/20',
        dotColor: 'bg-emerald-500',
      }
    case 'medium':
      return {
        label: `${score}% Medium`,
        className: 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-600/20',
        dotColor: 'bg-amber-500',
      }
    case 'low':
      return {
        label: `${score}% Low`,
        className: 'bg-rose-50 text-rose-700 border-rose-200 ring-rose-600/20',
        dotColor: 'bg-rose-500',
      }
  }
}

export function getDisciplineBadgeClass(discipline: ActivityDiscipline | string): string {
  switch (discipline) {
    case 'Piping':
      return 'bg-blue-50 text-blue-700 border-blue-200'
    case 'Civil':
      return 'bg-amber-50 text-amber-800 border-amber-200'
    case 'Mechanical':
      return 'bg-slate-100 text-slate-800 border-slate-300'
    case 'Electrical':
      return 'bg-yellow-50 text-yellow-800 border-yellow-200'
    case 'Instrumentation':
      return 'bg-cyan-50 text-cyan-800 border-cyan-200'
    case 'Structural':
      return 'bg-indigo-50 text-indigo-700 border-indigo-200'
    case 'HVAC':
      return 'bg-teal-50 text-teal-700 border-teal-200'
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200'
  }
}

export function getActivityStatusBadgeProps(status: ActivityStatus | string) {
  switch (status) {
    case 'Completed':
      return {
        label: 'Completed',
        className: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dotColor: 'bg-emerald-500',
      }
    case 'In Progress':
      return {
        label: 'In Progress',
        className: 'bg-blue-50 text-blue-700 border-blue-200',
        dotColor: 'bg-blue-500',
      }
    case 'Delayed':
      return {
        label: 'Delayed',
        className: 'bg-rose-50 text-rose-700 border-rose-200',
        dotColor: 'bg-rose-500',
      }
    case 'Blocked':
      return {
        label: 'Blocked',
        className: 'bg-red-50 text-red-800 border-red-200',
        dotColor: 'bg-red-600',
      }
    case 'Under Review':
      return {
        label: 'Under Review',
        className: 'bg-amber-50 text-amber-700 border-amber-200',
        dotColor: 'bg-amber-500',
      }
    case 'Not Started':
    default:
      return {
        label: 'Not Started',
        className: 'bg-gray-100 text-gray-700 border-gray-200',
        dotColor: 'bg-gray-400',
      }
  }
}

export function getConflictSeverityBadgeProps(severity: ConflictSeverity | string) {
  switch (severity) {
    case 'Critical':
      return {
        label: 'Critical',
        className: 'bg-red-100 text-red-800 border-red-300 font-semibold',
      }
    case 'High':
      return {
        label: 'High',
        className: 'bg-rose-50 text-rose-700 border-rose-200',
      }
    case 'Medium':
      return {
        label: 'Medium',
        className: 'bg-amber-50 text-amber-700 border-amber-200',
      }
    case 'Low':
    default:
      return {
        label: 'Low',
        className: 'bg-slate-100 text-slate-700 border-slate-200',
      }
  }
}

export function formatDate(dateString?: string | null): string {
  if (!dateString) return '—'
  try {
    const d = new Date(dateString)
    if (isNaN(d.getTime())) return dateString
    return d.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return dateString
  }
}

export function formatDateTime(dateString?: string | null): string {
  if (!dateString) return '—'
  try {
    const d = new Date(dateString)
    if (isNaN(d.getTime())) return dateString
    return d.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateString
  }
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`
}

export function formatVariance(variance: number): { text: string; isPositive: boolean; isNeutral: boolean } {
  const rounded = Math.round(variance * 10) / 10
  if (rounded === 0) {
    return { text: '0.0%', isPositive: true, isNeutral: true }
  }
  if (rounded > 0) {
    return { text: `+${rounded}%`, isPositive: true, isNeutral: false }
  }
  return { text: `${rounded}%`, isPositive: false, isNeutral: false }
}
