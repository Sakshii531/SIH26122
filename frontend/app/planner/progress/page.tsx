'use client'

import React, { useEffect, useState } from 'react'
import {
  TrendingUp,
  Clock,
  Calendar,
  Layers,
  CheckCircle2,
  AlertCircle,
  TrendingDown,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react'
import { usePlanner } from '@/context/PlannerContext'
import { progressService } from '@/services/progressService'
import { ProgressTimelineItem } from '@/types/progress'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import {
  formatDate,
  formatPercent,
  formatVariance,
  getDisciplineBadgeClass,
} from '@/lib/utils'

export default function ProgressPage() {
  const { dashboardMetrics } = usePlanner()
  const [timeline, setTimeline] = useState<ProgressTimelineItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const time = await progressService.getProgressTimeline()
        setTimeline(time)
      } catch (err) {
        console.error('Failed to load progress timeline:', err)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

  const summary = dashboardMetrics.overall_progress
  const variance = formatVariance(summary.variance)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Project Physical Progress & S-Curve Variance
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time actual execution progress linked directly from field DPRs to Primavera P6 baseline schedule
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="warning" dot dotColor="bg-amber-500">
            Status: {summary.overall_status}
          </Badge>
          <Badge variant="neutral">Schedule Rev C</Badge>
        </div>
      </div>

      {/* Progress Metric Summary Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Planned Progress */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Baseline Planned
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 font-mono">
              {formatPercent(summary.planned_progress)}
            </span>
            <span className="text-xs text-slate-400 font-mono">Target</span>
          </div>
          <div className="mt-2.5 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-slate-400 rounded-full"
              style={{ width: `${summary.planned_progress}%` }}
            />
          </div>
        </div>

        {/* Actual Progress */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Actual Validated
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-blue-600 font-mono">
              {formatPercent(summary.actual_progress)}
            </span>
            <span className="text-xs text-slate-400 font-mono">Completed</span>
          </div>
          <div className="mt-2.5 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full"
              style={{ width: `${summary.actual_progress}%` }}
            />
          </div>
        </div>

        {/* Variance */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Schedule Variance
          </span>
          <div className="mt-2 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold font-mono ${
                variance.isPositive ? 'text-emerald-600' : 'text-rose-600'
              }`}
            >
              {variance.text}
            </span>
            <span className="text-xs text-slate-400">vs Baseline</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-500 truncate">
            {variance.isPositive ? 'Ahead of baseline schedule' : 'Behind planned schedule'}
          </p>
        </div>

        {/* Activity Breakdown Count */}
        <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-col justify-between">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Activity Status Counts
          </span>
          <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-semibold">Completed:</span>
              <span className="font-bold text-emerald-600 font-mono block">
                {summary.completed_activities} / {summary.total_activities}
              </span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-semibold">Delayed:</span>
              <span className="font-bold text-rose-600 font-mono block">
                {summary.delayed_activities}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Planned vs Actual Comparison Card */}
      <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle p-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              Discipline Physical Progress Comparisons
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Comparison of actual validated completion percentages against baseline targets
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-slate-300 inline-block" />
              <span className="text-slate-600 text-[11px]">Planned Baseline</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-sm bg-blue-600 inline-block" />
              <span className="text-slate-900 font-semibold text-[11px]">Actual Execution</span>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {dashboardMetrics.discipline_progress.map((d) => {
            const v = formatVariance(d.variance)
            return (
              <div key={d.discipline} className="space-y-2">
                <div className="flex items-center justify-between text-xs font-medium">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                        d.discipline
                      )}`}
                    >
                      {d.discipline}
                    </span>
                    <span className="text-slate-500 text-[11px]">
                      ({d.total_activities} activities)
                    </span>
                  </div>
                  <div className="flex items-center gap-4 font-mono text-[11px]">
                    <span className="text-slate-500">
                      Planned: <strong>{d.planned_progress}%</strong>
                    </span>
                    <span className="text-slate-900 font-bold">
                      Actual: <strong className="text-blue-600">{d.actual_progress}%</strong>
                    </span>
                    <span className={v.isPositive ? 'text-emerald-600' : 'text-rose-600'}>
                      {v.text}
                    </span>
                  </div>
                </div>

                {/* Comparative Double Bar */}
                <div className="space-y-1">
                  {/* Planned Bar */}
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-slate-300 rounded-full"
                      style={{ width: `${d.planned_progress}%` }}
                    />
                  </div>
                  {/* Actual Bar */}
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full"
                      style={{ width: `${d.actual_progress}%` }}
                    />
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Progress Execution Timeline Feed */}
      <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              Chronological Progress Timeline Feed
            </h3>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Auditable execution log of validated field reports updating schedule activities
            </p>
          </div>
          <Badge variant="neutral">{timeline.length} Validated Updates</Badge>
        </div>

        <div className="p-6">
          <div className="relative border-l-2 border-slate-200 ml-4 space-y-6">
            {timeline.map((item) => (
              <div key={item.id} className="relative pl-6">
                {/* Marker Node */}
                <div className="absolute -left-2 top-0.5 h-4 w-4 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                </div>

                {/* Timeline Card */}
                <div className="p-4 bg-slate-50/80 border border-slate-200 rounded-xl space-y-2 text-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-200/80 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-slate-900">
                        {item.activity_code}
                      </span>
                      <span
                        className={`inline-block px-1.5 py-0.2 rounded text-[10px] border ${getDisciplineBadgeClass(
                          item.discipline
                        )}`}
                      >
                        {item.discipline}
                      </span>
                      <span className="font-semibold text-slate-800">
                        {item.activity_name}
                      </span>
                    </div>
                    <span className="font-mono text-slate-500 text-[11px]">
                      {formatDate(item.progress_date)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-slate-600 pt-1">
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase">
                        Progress Value:
                      </span>
                      <span className="font-bold text-blue-600 font-mono text-xs">
                        {item.progress_percentage}% Physical
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase">
                        Source Report:
                      </span>
                      <span className="font-medium text-slate-800 truncate block">
                        {item.source_report_title}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px] uppercase">
                        Validated By:
                      </span>
                      <span className="font-medium text-slate-800">
                        {item.validated_by_name}
                      </span>
                    </div>
                  </div>

                  {item.notes && (
                    <p className="mt-2 text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200 text-[11px]">
                      {item.notes}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
