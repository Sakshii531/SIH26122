'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { MOCK_REVIEW_QUEUE } from '@/mock/reviews'
import { MOCK_CONFLICTS } from '@/mock/conflicts'
import { MOCK_EVIDENCE } from '@/mock/evidence'
import { MOCK_ACTIVITIES } from '@/mock/activities'
import { MOCK_AUDIT_LOGS } from '@/mock/auditLogs'
import { MOCK_DASHBOARD_DATA, DashboardMetrics } from '@/mock/dashboard'
import { ReviewQueueItem, RejectionReason } from '@/types/review'
import { ConflictItem } from '@/types/conflict'
import { EvidenceItem } from '@/types/evidence'
import { Activity, AuditLog } from '@/types/database'
import { NotificationItem } from '@/types/notification'

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif-001',
    title: 'Pending AI Match Reviews',
    description: '5 low/medium confidence AI activity matches require Planner verification.',
    category: 'Review',
    timestamp: '2026-09-06T15:15:00Z',
    is_read: false,
    link_url: '/planner/review-queue',
  },
  {
    id: 'notif-002',
    title: 'Critical Conflict Flagged',
    description: 'Contradictory hydrotest outcome reported for utility steam header Loop 08.',
    category: 'Conflict',
    timestamp: '2026-09-05T19:00:00Z',
    is_read: false,
    link_url: '/planner/conflicts',
  },
  {
    id: 'notif-003',
    title: 'Field Evidence Uploaded',
    description: '4 new site photographs and laboratory test certificates awaiting QA validation.',
    category: 'Evidence',
    timestamp: '2026-09-04T18:50:00Z',
    is_read: false,
    link_url: '/planner/evidence',
  },
  {
    id: 'notif-004',
    title: 'Baseline Schedule Synced',
    description: 'Primavera P6 Rev C baseline schedule successfully ingested with 48 activities.',
    category: 'Schedule',
    timestamp: '2026-09-01T08:00:00Z',
    is_read: true,
    link_url: '/planner/activities',
  },
]

interface PlannerContextType {
  // Reviews
  reviews: ReviewQueueItem[]
  pendingReviewsCount: number
  approveReview: (matchId: string, plannerId: string, plannerName: string, notes?: string) => Promise<boolean>
  correctReview: (
    matchId: string,
    plannerId: string,
    plannerName: string,
    correctedActivity: Activity,
    notes?: string
  ) => Promise<boolean>
  rejectReview: (
    matchId: string,
    plannerId: string,
    plannerName: string,
    reason: RejectionReason,
    notes?: string
  ) => Promise<boolean>

  // Conflicts
  conflicts: ConflictItem[]
  openConflictsCount: number
  resolveConflict: (
    conflictId: string,
    plannerId: string,
    plannerName: string,
    resolutionAction: 'Accept Reported' | 'Maintain Existing' | 'Custom Adjustment',
    notes: string
  ) => Promise<boolean>

  // Evidence
  evidenceList: EvidenceItem[]
  pendingEvidenceCount: number
  verifyEvidence: (evidenceId: string, plannerId: string, plannerName: string, notes?: string) => Promise<boolean>
  rejectEvidence: (evidenceId: string, plannerId: string, plannerName: string, reason: string) => Promise<boolean>

  // Activities & Audit Logs
  activities: Activity[]
  auditLogs: AuditLog[]

  // Notifications
  notifications: NotificationItem[]
  unreadNotificationsCount: number
  markNotificationAsRead: (id: string) => void
  markAllNotificationsAsRead: () => void

  // Dashboard Aggregates
  dashboardMetrics: DashboardMetrics
}

const PlannerContext = createContext<PlannerContextType | undefined>(undefined)

export function PlannerProvider({ children }: { children: ReactNode }) {
  const [reviews, setReviews] = useState<ReviewQueueItem[]>(() => [...MOCK_REVIEW_QUEUE])
  const [conflicts, setConflicts] = useState<ConflictItem[]>(() => [...MOCK_CONFLICTS])
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>(() => [...MOCK_EVIDENCE])
  const [activities, setActivities] = useState<Activity[]>(() => [...MOCK_ACTIVITIES])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>(() => [...MOCK_AUDIT_LOGS])
  const [notifications, setNotifications] = useState<NotificationItem[]>(() => [...INITIAL_NOTIFICATIONS])

  // Derived dynamic counts - always perfectly synchronized
  const pendingReviewsCount = reviews.filter((r) => r.status === 'Needs Review').length
  const openConflictsCount = conflicts.filter((c) => c.status === 'Open').length
  const pendingEvidenceCount = evidenceList.filter((e) => e.validation_status === 'Pending').length
  const unreadNotificationsCount = notifications.filter((n) => !n.is_read).length

  // Dynamically computed dashboard metrics
  const dashboardMetrics: DashboardMetrics = {
    ...MOCK_DASHBOARD_DATA,
    pending_reviews_count: pendingReviewsCount,
    open_conflicts_count: openConflictsCount,
    evidence_pending_count: pendingEvidenceCount,
    confidence_distribution: {
      high: 27 + reviews.filter((r) => r.status === 'Approved').length,
      medium: reviews.filter((r) => r.status === 'Needs Review' && r.confidence_score >= 50).length,
      low: reviews.filter((r) => r.status === 'Needs Review' && r.confidence_score < 50).length,
    },
  }

  const approveReview = async (
    matchId: string,
    plannerId: string,
    plannerName: string,
    notes?: string
  ): Promise<boolean> => {
    const item = reviews.find((r) => r.id === matchId)
    if (!item) return false

    // Update review item state
    setReviews((prev) =>
      prev.map((r) => (r.id === matchId ? { ...r, status: 'Approved' } : r))
    )

    // Update corresponding activity progress
    if (item.reported_progress_percent !== undefined) {
      setActivities((prev) =>
        prev.map((a) =>
          a.activity_code === item.suggested_activity_code
            ? {
                ...a,
                progress_percentage: item.reported_progress_percent || a.progress_percentage,
                status:
                  item.reported_progress_percent === 100
                    ? 'Completed'
                    : a.status === 'Not Started'
                    ? 'In Progress'
                    : a.status,
                updated_at: new Date().toISOString(),
              }
            : a
        )
      )
    }

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Match Approved',
      entity: 'PlannerReview',
      entity_id: matchId,
      details: {
        suggested_code: item.suggested_activity_code,
        activity_name: item.suggested_activity_name,
        confidence: item.confidence_score,
        notes: notes || 'Approved by planner',
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const correctReview = async (
    matchId: string,
    plannerId: string,
    plannerName: string,
    correctedActivity: Activity,
    notes?: string
  ): Promise<boolean> => {
    const item = reviews.find((r) => r.id === matchId)
    if (!item) return false

    const originalCode = item.suggested_activity_code

    setReviews((prev) =>
      prev.map((r) =>
        r.id === matchId
          ? {
              ...r,
              suggested_activity_id: correctedActivity.id,
              suggested_activity_code: correctedActivity.activity_code,
              suggested_activity_name: correctedActivity.activity_name,
              suggested_wbs_code: correctedActivity.wbs_code,
              status: 'Corrected',
            }
          : r
      )
    )

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Match Corrected',
      entity: 'PlannerReview',
      entity_id: matchId,
      details: {
        original_code: originalCode,
        corrected_code: correctedActivity.activity_code,
        corrected_name: correctedActivity.activity_name,
        notes: notes || 'Manually corrected by planner',
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const rejectReview = async (
    matchId: string,
    plannerId: string,
    plannerName: string,
    reason: RejectionReason,
    notes?: string
  ): Promise<boolean> => {
    const item = reviews.find((r) => r.id === matchId)
    if (!item) return false

    setReviews((prev) =>
      prev.map((r) => (r.id === matchId ? { ...r, status: 'Rejected' } : r))
    )

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Match Rejected',
      entity: 'PlannerReview',
      entity_id: matchId,
      details: {
        activity_code: item.suggested_activity_code,
        rejection_reason: reason,
        notes: notes || '',
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const resolveConflict = async (
    conflictId: string,
    plannerId: string,
    plannerName: string,
    resolutionAction: 'Accept Reported' | 'Maintain Existing' | 'Custom Adjustment',
    notes: string
  ): Promise<boolean> => {
    const conf = conflicts.find((c) => c.id === conflictId)
    if (!conf) return false

    setConflicts((prev) =>
      prev.map((c) =>
        c.id === conflictId
          ? {
              ...c,
              status: 'Resolved',
              resolution_notes: notes,
              resolved_by_name: plannerName,
              resolved_at: new Date().toISOString(),
            }
          : c
      )
    )

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Conflict Resolved',
      entity: 'Conflict',
      entity_id: conflictId,
      details: {
        activity_code: conf.activity_code,
        conflict_type: conf.conflict_type,
        action: resolutionAction,
        notes: notes,
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const verifyEvidence = async (
    evidenceId: string,
    plannerId: string,
    plannerName: string,
    notes?: string
  ): Promise<boolean> => {
    const ev = evidenceList.find((e) => e.id === evidenceId)
    if (!ev) return false

    setEvidenceList((prev) =>
      prev.map((e) =>
        e.id === evidenceId
          ? {
              ...e,
              validation_status: 'Verified',
              validation_notes: notes || 'Verified by Planner',
              validated_by_name: plannerName,
              validated_at: new Date().toISOString(),
            }
          : e
      )
    )

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Evidence Verified',
      entity: 'Evidence',
      entity_id: evidenceId,
      details: {
        file_name: ev.file_name,
        activity_code: ev.activity_code,
        notes: notes || '',
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const rejectEvidence = async (
    evidenceId: string,
    plannerId: string,
    plannerName: string,
    reason: string
  ): Promise<boolean> => {
    const ev = evidenceList.find((e) => e.id === evidenceId)
    if (!ev) return false

    setEvidenceList((prev) =>
      prev.map((e) =>
        e.id === evidenceId
          ? {
              ...e,
              validation_status: 'Rejected',
              validation_notes: reason,
              validated_by_name: plannerName,
              validated_at: new Date().toISOString(),
            }
          : e
      )
    )

    // Add Audit Log
    const newLog: AuditLog = {
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      user_id: plannerId,
      user_name: plannerName,
      user_role: 'Planner',
      action: 'Evidence Rejected',
      entity: 'Evidence',
      entity_id: evidenceId,
      details: {
        file_name: ev.file_name,
        activity_code: ev.activity_code,
        reason: reason,
      },
    }
    setAuditLogs((prev) => [newLog, ...prev])

    return true
  }

  const markNotificationAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    )
  }

  const markAllNotificationsAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
  }

  return (
    <PlannerContext.Provider
      value={{
        reviews,
        pendingReviewsCount,
        approveReview,
        correctReview,
        rejectReview,
        conflicts,
        openConflictsCount,
        resolveConflict,
        evidenceList,
        pendingEvidenceCount,
        verifyEvidence,
        rejectEvidence,
        activities,
        auditLogs,
        notifications,
        unreadNotificationsCount,
        markNotificationAsRead,
        markAllNotificationsAsRead,
        dashboardMetrics,
      }}
    >
      {children}
    </PlannerContext.Provider>
  )
}

export function usePlanner() {
  const context = useContext(PlannerContext)
  if (!context) {
    throw new Error('usePlanner must be used within a PlannerProvider')
  }
  return context
}
