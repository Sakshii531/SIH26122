'use client'

import React, { useState } from 'react'
import {
  Layers,
  Search,
  Filter,
  Eye,
  Calendar,
  Building,
  CheckCircle2,
  AlertTriangle,
  Clock,
  FileText,
  Image as ImageIcon,
  ChevronRight,
} from 'lucide-react'
import { usePlanner } from '@/context/PlannerContext'
import { Activity } from '@/types/database'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Drawer } from '@/components/common/Drawer'
import { EmptyState } from '@/components/common/EmptyState'
import {
  formatDate,
  formatPercent,
  getActivityStatusBadgeProps,
  getDisciplineBadgeClass,
} from '@/lib/utils'

export default function ActivitiesPage() {
  const { activities, evidenceList } = usePlanner()

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDiscipline, setSelectedDiscipline] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('All')
  const [selectedLevel, setSelectedLevel] = useState('All')

  // Selected Activity Detail
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null)

  // Filter list
  const filteredActivities = activities.filter((act) => {
    if (selectedDiscipline !== 'All' && act.discipline !== selectedDiscipline) return false
    if (selectedStatus !== 'All' && act.status !== selectedStatus) return false
    if (selectedLevel !== 'All' && act.level !== selectedLevel) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        act.activity_code.toLowerCase().includes(q) ||
        act.activity_name.toLowerCase().includes(q) ||
        act.wbs_code.toLowerCase().includes(q) ||
        act.location.toLowerCase().includes(q)
      )
    }

    return true
  })

  const linkedEvidence = selectedActivity
    ? evidenceList.filter((e) => e.activity_code === selectedActivity.activity_code)
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            L5/L6 Schedule Activities & WBS
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Work Breakdown Structure hierarchy, baseline targets, and validated physical progress
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="neutral">Schedule Rev C (P6)</Badge>
          <Badge variant="info">{activities.length} Total Activities</Badge>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search */}
          <div className="sm:col-span-2">
            <Input
              placeholder="Search code (PIP-L5), description, WBS, location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="w-4 h-4" />}
            />
          </div>

          {/* Discipline */}
          <div>
            <select
              value={selectedDiscipline}
              onChange={(e) => setSelectedDiscipline(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Disciplines</option>
              <option value="Piping">Piping</option>
              <option value="Civil">Civil</option>
              <option value="Mechanical">Mechanical</option>
              <option value="Electrical">Electrical</option>
              <option value="Instrumentation">Instrumentation</option>
              <option value="Structural">Structural</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Statuses</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
              <option value="Delayed">Delayed</option>
              <option value="Under Review">Under Review</option>
              <option value="Not Started">Not Started</option>
            </select>
          </div>
        </div>
      </div>

      {/* Activities Table */}
      {filteredActivities.length === 0 ? (
        <EmptyState
          title="No Activities Found"
          description="No schedule activities match your search and filter criteria."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('')
            setSelectedDiscipline('All')
            setSelectedStatus('All')
            setSelectedLevel('All')
          }}
        />
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Activity Code</th>
                  <th className="py-2.5 px-4">Activity Name & Scope</th>
                  <th className="py-2.5 px-4">WBS</th>
                  <th className="py-2.5 px-4">Discipline</th>
                  <th className="py-2.5 px-4">Planned Dates</th>
                  <th className="py-2.5 px-4">Actual Dates</th>
                  <th className="py-2.5 px-4">Progress</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredActivities.map((act) => {
                  const statusProps = getActivityStatusBadgeProps(act.status)
                  return (
                    <tr key={act.id} className="hover:bg-slate-50/70 transition-colors">
                      {/* Code */}
                      <td className="py-3 px-4 font-mono font-bold text-slate-900">
                        {act.activity_code}
                      </td>

                      {/* Name & Location */}
                      <td className="py-3 px-4">
                        <p className="font-semibold text-slate-800 line-clamp-1 max-w-[220px]">
                          {act.activity_name}
                        </p>
                        <p className="text-[11px] text-slate-400 truncate max-w-[220px]">
                          {act.location}
                        </p>
                      </td>

                      {/* WBS */}
                      <td className="py-3 px-4 font-mono text-slate-600">
                        {act.wbs_code}
                      </td>

                      {/* Discipline */}
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                            act.discipline
                          )}`}
                        >
                          {act.discipline}
                        </span>
                      </td>

                      {/* Planned Dates */}
                      <td className="py-3 px-4 font-mono text-slate-600 whitespace-nowrap">
                        <span>{formatDate(act.planned_start)}</span>
                        <span className="text-slate-400"> → </span>
                        <span>{formatDate(act.planned_finish)}</span>
                      </td>

                      {/* Actual Dates */}
                      <td className="py-3 px-4 font-mono text-slate-600 whitespace-nowrap">
                        {act.actual_start ? (
                          <>
                            <span>{formatDate(act.actual_start)}</span>
                            <span className="text-slate-400"> → </span>
                            <span>{formatDate(act.actual_finish) || 'Ongoing'}</span>
                          </>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>

                      {/* Progress */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-slate-900">
                            {formatPercent(act.progress_percentage)}
                          </span>
                          <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                            <div
                              className="h-full bg-blue-600 rounded-full"
                              style={{ width: `${act.progress_percentage}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border ${statusProps.className}`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${statusProps.dotColor}`} />
                          {statusProps.label}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-3 px-4 text-right">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => setSelectedActivity(act)}
                          leftIcon={<Eye className="w-3.5 h-3.5" />}
                        >
                          Details
                        </Button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Activity Detail Drawer */}
      {selectedActivity && (
        <Drawer
          isOpen={Boolean(selectedActivity)}
          onClose={() => setSelectedActivity(null)}
          title={`${selectedActivity.activity_code}: ${selectedActivity.activity_name}`}
          subtitle={`WBS ${selectedActivity.wbs_code} • Level ${selectedActivity.level}`}
          width="2xl"
        >
          <div className="space-y-5 text-xs">
            {/* Top Overview Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Discipline</span>
                <span className={`inline-block px-1.5 py-0.5 rounded text-[11px] border mt-1 ${getDisciplineBadgeClass(selectedActivity.discipline)}`}>
                  {selectedActivity.discipline}
                </span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Status</span>
                <span className="font-semibold text-slate-800 block mt-1">
                  {selectedActivity.status}
                </span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Actual Progress</span>
                <span className="font-bold text-blue-600 text-sm font-mono block mt-0.5">
                  {selectedActivity.progress_percentage}%
                </span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">Planned Weight</span>
                <span className="font-mono font-semibold text-slate-800 block mt-1">
                  {selectedActivity.weightage}%
                </span>
              </div>
            </div>

            {/* Description & Scope */}
            <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-2">
              <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] block border-b border-slate-200 pb-2">
                Scope & Location Details
              </span>
              <p className="text-slate-700 leading-relaxed text-xs">
                {selectedActivity.description}
              </p>
              <div className="grid grid-cols-2 gap-2 text-slate-600 pt-2 border-t border-slate-200">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Work Location:</span>
                  <span className="font-semibold text-slate-800">{selectedActivity.location}</span>
                </div>
                {selectedActivity.zone_area && (
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase">Zone / Area:</span>
                    <span className="font-semibold text-slate-800">{selectedActivity.zone_area}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Schedule Dates & Quantities */}
            <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-3">
              <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] block border-b border-slate-200 pb-2">
                Dates & Quantities
              </span>
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase">Baseline Schedule Dates</span>
                  <p className="font-mono text-slate-800 font-medium">
                    Start: {formatDate(selectedActivity.planned_start)}
                  </p>
                  <p className="font-mono text-slate-800 font-medium">
                    Finish: {formatDate(selectedActivity.planned_finish)}
                  </p>
                </div>
                <div className="space-y-1">
                  <span className="text-slate-400 block text-[10px] uppercase">Actual Execution Dates</span>
                  <p className="font-mono text-slate-800 font-medium">
                    Actual Start: {formatDate(selectedActivity.actual_start)}
                  </p>
                  <p className="font-mono text-slate-800 font-medium">
                    Actual Finish: {formatDate(selectedActivity.actual_finish) || 'Ongoing'}
                  </p>
                </div>
              </div>
              <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Planned Quantity: {selectedActivity.planned_quantity} {selectedActivity.unit_of_measure}</span>
                <span className="text-blue-600 font-semibold font-mono">Installed: {selectedActivity.actual_quantity} {selectedActivity.unit_of_measure}</span>
              </div>
            </div>

            {/* Attached Evidence */}
            {linkedEvidence.length > 0 && (
              <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-2">
                <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] block border-b border-slate-200 pb-2">
                  Linked Field Evidence ({linkedEvidence.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {linkedEvidence.map((ev) => (
                    <div key={ev.id} className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center gap-2 shadow-xs">
                      {ev.file_type === 'Photo' ? (
                        <ImageIcon className="w-4 h-4 text-blue-600 shrink-0" />
                      ) : (
                        <FileText className="w-4 h-4 text-rose-600 shrink-0" />
                      )}
                      <div className="min-w-0 flex-1">
                        <span className="font-medium text-slate-800 block truncate">{ev.file_name}</span>
                        <span className="text-[10px] text-emerald-600 font-medium">{ev.validation_status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Drawer>
      )}
    </div>
  )
}
