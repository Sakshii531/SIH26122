'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  TrendingUp,
  CheckSquare,
  AlertTriangle,
  FileCheck2,
  Layers,
  ArrowRight,
  TrendingDown,
  CheckCircle2,
  Clock,
  ExternalLink,
  ShieldCheck,
  Building,
} from 'lucide-react'
import { usePlanner } from '@/context/PlannerContext'
import { progressService } from '@/services/progressService'
import { ProgressTimelineItem } from '@/types/progress'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { CardSkeleton, TableSkeleton } from '@/components/common/LoadingSkeleton'
import {
  formatDate,
  formatPercent,
  formatVariance,
  getDisciplineBadgeClass,
} from '@/lib/utils'

export default function PlannerDashboardPage() {
  const {
    dashboardMetrics,
    pendingReviewsCount,
    openConflictsCount,
    pendingEvidenceCount,
  } = usePlanner()

  const [recentActivity, setRecentActivity] = useState<ProgressTimelineItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const timelineData = await progressService.getProgressTimeline()
        setRecentActivity(timelineData)
      } catch (err) {
        console.error('Failed to load recent timeline:', err)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

  const { planned_progress, actual_progress, variance, overall_status } =
    dashboardMetrics.overall_progress
  const varianceFormatted = formatVariance(variance)

  return (
    <div className="space-y-6">
      {/* Top Banner / Project Context with Quick Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 bg-white border border-slate-200/90 rounded-xl shadow-subtle">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-slate-900">
              Refinery Expansion Unit 4 — Execution Control
            </h2>
            <Badge variant="warning" dot dotColor="bg-amber-500">
              {overall_status}
            </Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Baseline Schedule: Rev C (Primavera P6) • Active Project Ingestion Layer
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <Link href="/planner/review-queue">
            <Button
              size="sm"
              variant="primary"
              className="bg-blue-600 hover:bg-blue-700 border-blue-600 shadow-xs"
              rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Review Queue ({pendingReviewsCount})
            </Button>
          </Link>
          <Link href="/planner/progress">
            <Button size="sm" variant="secondary">
              View Schedule Curves
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Row — Dynamically Synchronized */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Project Progress & Variance */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Project Physical Progress
            </span>
            <TrendingUp className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900 font-mono">
                {formatPercent(actual_progress)}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                / {formatPercent(planned_progress)} planned
              </span>
            </div>
            <div className="mt-2.5 h-2 w-full bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all duration-500"
                style={{ width: `${actual_progress}%` }}
              />
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Schedule Variance</span>
            <span
              className={`font-mono font-semibold ${
                varianceFormatted.isPositive ? 'text-emerald-600' : 'text-rose-600'
              }`}
            >
              {varianceFormatted.text}
            </span>
          </div>
        </div>

        {/* Card 2: Pending Reviews */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Pending AI Matches
            </span>
            <CheckSquare className="w-4 h-4 text-amber-500" />
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900 font-mono">
                {pendingReviewsCount}
              </span>
              <span className="text-[11px] font-semibold text-amber-800 bg-amber-50 px-1.5 py-0.2 rounded border border-amber-200">
                Requires Review
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Low/Medium confidence match suggestions
            </p>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
            <Link
              href="/planner/review-queue"
              className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1"
            >
              Open Queue <ArrowRight className="w-3 h-3" />
            </Link>
            <span className="text-slate-400 font-mono">{pendingReviewsCount} items</span>
          </div>
        </div>

        {/* Card 3: Open Conflicts */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Open Conflicts
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900 font-mono">
                {openConflictsCount}
              </span>
              <span className="text-[11px] font-semibold text-rose-800 bg-rose-50 px-1.5 py-0.2 rounded border border-rose-200">
                Action Required
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Discrepancies between DPRs & baseline
            </p>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
            <Link
              href="/planner/conflicts"
              className="text-rose-600 hover:text-rose-800 font-medium inline-flex items-center gap-1"
            >
              Resolve Conflicts <ArrowRight className="w-3 h-3" />
            </Link>
            <span className="text-slate-400 font-mono">{openConflictsCount} open</span>
          </div>
        </div>

        {/* Card 4: Evidence Pending */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
              Evidence Pending QA
            </span>
            <FileCheck2 className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900 font-mono">
                {pendingEvidenceCount}
              </span>
              <span className="text-[11px] font-semibold text-slate-700 bg-slate-100 px-1.5 py-0.2 rounded border border-slate-200">
                Photos & Docs
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Site verification documents awaiting sign-off
            </p>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
            <Link
              href="/planner/evidence"
              className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1"
            >
              Inspect Evidence <ArrowRight className="w-3 h-3" />
            </Link>
            <span className="text-slate-400 font-mono">{pendingEvidenceCount} pending</span>
          </div>
        </div>
      </div>

      {/* Two Columns: Discipline Progress Breakdown & Confidence Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Discipline Progress Table */}
        <div className="lg:col-span-2 bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
          <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                Discipline-Wise Physical Progress
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Physical progress compared against Primavera baseline
              </p>
            </div>
            <Link
              href="/planner/progress"
              className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              Full Details <ExternalLink className="w-3 h-3" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Discipline</th>
                  <th className="py-2.5 px-4 text-center">Activities</th>
                  <th className="py-2.5 px-4">Planned</th>
                  <th className="py-2.5 px-4">Actual</th>
                  <th className="py-2.5 px-4">Variance</th>
                  <th className="py-2.5 px-4 text-right">Health Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {dashboardMetrics.discipline_progress.map((disc) => {
                  const v = formatVariance(disc.variance)
                  return (
                    <tr key={disc.discipline} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-4 font-medium text-slate-900">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                            disc.discipline
                          )}`}
                        >
                          {disc.discipline}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center text-slate-600 font-mono">
                        {disc.total_activities}
                      </td>
                      <td className="py-3 px-4 text-slate-600 font-mono font-medium">
                        {disc.planned_progress}%
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-slate-900">
                            {disc.actual_progress}%
                          </span>
                          <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                            <div
                              className="h-full bg-blue-600 rounded-full"
                              style={{ width: `${disc.actual_progress}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono font-semibold">
                        <span className={v.isPositive ? 'text-emerald-600' : 'text-rose-600'}>
                          {v.text}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        {disc.status === 'Healthy' ? (
                          <Badge variant="success" dot dotColor="bg-emerald-500">
                            Healthy
                          </Badge>
                        ) : disc.status === 'Needs Attention' ? (
                          <Badge variant="warning" dot dotColor="bg-amber-500">
                            Attention
                          </Badge>
                        ) : (
                          <Badge variant="danger" dot dotColor="bg-rose-500">
                            Critical
                          </Badge>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right 1 Col: AI Match Confidence Distribution */}
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                AI Matching Breakdown
              </h3>
              <Badge variant="neutral">Ingestion Pipeline</Badge>
            </div>
            <p className="text-[11px] text-slate-500 mb-4">
              Semantic matching confidence tiers across ingested DPRs
            </p>

            <div className="space-y-2.5">
              {/* High Confidence */}
              <div className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-100">
                <div className="flex items-center justify-between text-xs font-semibold text-emerald-900">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span>High Confidence (≥ 70%)</span>
                  </div>
                  <span className="font-mono text-emerald-800">
                    {dashboardMetrics.confidence_distribution.high}
                  </span>
                </div>
                <p className="mt-0.5 text-[10px] text-emerald-700">
                  Direct schedule linking applied
                </p>
              </div>

              {/* Medium Confidence */}
              <div className="p-2.5 rounded-lg bg-amber-50/60 border border-amber-100">
                <div className="flex items-center justify-between text-xs font-semibold text-amber-900">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    <span>Medium (50–69%)</span>
                  </div>
                  <span className="font-mono text-amber-800">
                    {dashboardMetrics.confidence_distribution.medium}
                  </span>
                </div>
                <p className="mt-0.5 text-[10px] text-amber-700">
                  Sent to Review Queue for confirmation
                </p>
              </div>

              {/* Low Confidence */}
              <div className="p-2.5 rounded-lg bg-rose-50/60 border border-rose-100">
                <div className="flex items-center justify-between text-xs font-semibold text-rose-900">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-rose-500" />
                    <span>Low (&lt; 50%)</span>
                  </div>
                  <span className="font-mono text-rose-800">
                    {dashboardMetrics.confidence_distribution.low}
                  </span>
                </div>
                <p className="mt-0.5 text-[10px] text-rose-700">
                  Ambiguous wording / manual override required
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100">
            <Link href="/planner/review-queue">
              <Button size="sm" variant="secondary" className="w-full">
                Review Pending Queue ({pendingReviewsCount})
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Actual Progress Timeline Table */}
      <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              Recent Validated Execution Events
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Actual progress events validated by Planner and written to audit trail
            </p>
          </div>
          <Link
            href="/planner/audit-logs"
            className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            Audit Trail <ExternalLink className="w-3 h-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-2.5 px-4">Activity</th>
                <th className="py-2.5 px-4">Discipline</th>
                <th className="py-2.5 px-4">Progress Recorded</th>
                <th className="py-2.5 px-4">Source Report</th>
                <th className="py-2.5 px-4">Validated By</th>
                <th className="py-2.5 px-4 text-right">Event Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentActivity.map((act) => (
                <tr key={act.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4">
                    <div>
                      <span className="font-mono font-bold text-slate-900">
                        {act.activity_code}
                      </span>
                      <p className="text-slate-600 font-medium text-xs mt-0.5">
                        {act.activity_name}
                      </p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                        act.discipline
                      )}`}
                    >
                      {act.discipline}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-blue-600">
                        {act.progress_percentage}%
                      </span>
                      {act.quantity_completed !== undefined && (
                        <span className="text-[11px] text-slate-500">
                          ({act.quantity_completed} units)
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-700">
                    <span className="font-medium">{act.source_report_title}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{act.validated_by_name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-500 font-mono">
                    {formatDate(act.progress_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
