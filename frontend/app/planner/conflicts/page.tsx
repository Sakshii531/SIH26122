'use client'

import React, { useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  Filter,
  Eye,
  Check,
  Building,
  Calendar,
  Layers,
  ArrowRight,
  HelpCircle,
  FileText,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { usePlanner } from '@/context/PlannerContext'
import { ConflictItem } from '@/types/conflict'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Modal } from '@/components/common/Modal'
import { EmptyState } from '@/components/common/EmptyState'
import {
  formatDate,
  formatDateTime,
  getConflictSeverityBadgeProps,
} from '@/lib/utils'

export default function ConflictsPage() {
  const { user } = useAuth()
  const { conflicts, openConflictsCount, resolveConflict } = usePlanner()

  // Filter
  const [statusFilter, setStatusFilter] = useState('All')

  // Resolution Modal
  const [selectedConflict, setSelectedConflict] = useState<ConflictItem | null>(null)
  const [resolutionAction, setResolutionAction] = useState<'Accept Reported' | 'Maintain Existing' | 'Custom Adjustment'>('Accept Reported')
  const [resolutionNotes, setResolutionNotes] = useState('')
  const [isResolving, setIsResolving] = useState(false)
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const filteredConflicts = conflicts.filter((c) => {
    if (statusFilter !== 'All' && c.status !== statusFilter) return false
    return true
  })

  const handleResolve = async () => {
    if (!selectedConflict) return
    if (!resolutionNotes.trim()) {
      showNotification('Please enter resolution notes explaining the decision.', 'error')
      return
    }

    setIsResolving(true)
    try {
      const success = await resolveConflict(
        selectedConflict.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta',
        resolutionAction,
        resolutionNotes
      )
      if (success) {
        showNotification(`Conflict for ${selectedConflict.activity_code} resolved successfully.`)
        setSelectedConflict(null)
        setResolutionNotes('')
      }
    } catch (err) {
      showNotification('Failed to resolve conflict.', 'error')
    } finally {
      setIsResolving(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`p-3.5 rounded-lg flex items-center justify-between shadow-card border ${
            notification.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
              : 'bg-rose-50 text-rose-900 border-rose-200'
          }`}
        >
          <div className="flex items-center gap-2 text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{notification.message}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-[11px] font-semibold hover:underline text-slate-600"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Execution Conflict Resolution
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Identify and resolve discrepancies between field progress reports, baseline schedules, and QA inspections
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            {openConflictsCount} Open Conflicts
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <Check className="w-3.5 h-3.5 text-emerald-600" />
            {conflicts.filter((c) => c.status === 'Resolved').length} Resolved
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">
            Filter Status:
          </span>
          <div className="flex items-center gap-1.5">
            {['All', 'Open', 'Resolved'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  statusFilter === st
                    ? 'bg-slate-900 text-white font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Conflicts Table */}
      {filteredConflicts.length === 0 ? (
        <EmptyState
          title="No Conflicts Found"
          description="There are currently no active execution conflicts matching the filter criteria."
        />
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Conflict Description</th>
                  <th className="py-2.5 px-4">Related Activity</th>
                  <th className="py-2.5 px-4">Conflict Type</th>
                  <th className="py-2.5 px-4">Severity</th>
                  <th className="py-2.5 px-4">Detected</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredConflicts.map((conf) => {
                  const sevProps = getConflictSeverityBadgeProps(conf.severity)
                  return (
                    <tr
                      key={conf.id}
                      className={`hover:bg-slate-50/70 transition-colors ${
                        conf.status === 'Resolved' ? 'bg-emerald-50/20' : ''
                      }`}
                    >
                      {/* Conflict Issue */}
                      <td className="py-3 px-4">
                        <span className="font-bold text-slate-900 block line-clamp-1 max-w-[240px]">
                          {conf.title}
                        </span>
                        <p className="text-slate-500 text-[11px] line-clamp-2 max-w-[240px] mt-0.5">
                          {conf.description}
                        </p>
                      </td>

                      {/* Related Activity */}
                      <td className="py-3 px-4">
                        <span className="font-mono font-bold text-slate-900">
                          {conf.activity_code}
                        </span>
                        <p className="text-slate-600 text-[11px] truncate max-w-[180px]">
                          {conf.activity_name}
                        </p>
                      </td>

                      {/* Type */}
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[11px] bg-slate-100 text-slate-700 border border-slate-200 font-medium">
                          {conf.conflict_type}
                        </span>
                      </td>

                      {/* Severity */}
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[11px] border ${sevProps.className}`}
                        >
                          {sevProps.label}
                        </span>
                      </td>

                      {/* Detected */}
                      <td className="py-3 px-4 font-mono text-slate-500">
                        {formatDate(conf.detected_at)}
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        {conf.status === 'Resolved' ? (
                          <Badge variant="success">Resolved</Badge>
                        ) : (
                          <Badge variant="danger" dot dotColor="bg-rose-500">
                            Open
                          </Badge>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <Button
                          size="sm"
                          variant={conf.status === 'Open' ? 'primary' : 'secondary'}
                          onClick={() => {
                            setSelectedConflict(conf)
                            setResolutionNotes(conf.resolution_notes || '')
                          }}
                          leftIcon={conf.status === 'Open' ? <Check className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        >
                          {conf.status === 'Open' ? 'Resolve' : 'View'}
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

      {/* Conflict Resolution Modal */}
      {selectedConflict && (
        <Modal
          isOpen={Boolean(selectedConflict)}
          onClose={() => setSelectedConflict(null)}
          title={`Resolve Conflict: ${selectedConflict.activity_code}`}
          subtitle={`Type: ${selectedConflict.conflict_type} • Severity: ${selectedConflict.severity}`}
          maxWidth="xl"
          footer={
            selectedConflict.status === 'Open' ? (
              <>
                <Button variant="secondary" size="sm" onClick={() => setSelectedConflict(null)}>
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleResolve}
                  isLoading={isResolving}
                >
                  Confirm Resolution
                </Button>
              </>
            ) : (
              <Button variant="secondary" size="sm" onClick={() => setSelectedConflict(null)}>
                Close
              </Button>
            )
          }
        >
          <div className="space-y-4 text-xs">
            {/* Conflict Description */}
            <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-lg space-y-1">
              <span className="font-bold text-rose-900 block">{selectedConflict.title}</span>
              <p className="text-rose-800 leading-relaxed">{selectedConflict.description}</p>
            </div>

            {/* Comparison Values */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  Field Reported Value:
                </span>
                <p className="font-bold text-slate-900 font-mono mt-1">
                  {selectedConflict.reported_value}
                </p>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  System Baseline / QA Value:
                </span>
                <p className="font-bold text-slate-900 font-mono mt-1">
                  {selectedConflict.current_system_value}
                </p>
              </div>
            </div>

            {selectedConflict.status === 'Open' ? (
              <>
                {/* Resolution Decision Options */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                    Select Planner Resolution Action:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { id: 'Accept Reported', label: 'Accept Reported' },
                      { id: 'Maintain Existing', label: 'Maintain Existing' },
                      { id: 'Custom Adjustment', label: 'Custom Adjustment' },
                    ].map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => setResolutionAction(opt.id as any)}
                        className={`p-2 rounded-lg border text-center font-medium transition-all text-xs ${
                          resolutionAction === opt.id
                            ? 'bg-blue-50 border-blue-600 text-blue-900 font-bold ring-1 ring-blue-600'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Resolution Notes */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                    Resolution Justification & Audit Notes: <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="Document the technical justification, QA reconciliation, or management approval..."
                    rows={3}
                    className="w-full rounded-lg border border-slate-300 p-2.5 text-xs focus:border-blue-600 focus:outline-none"
                    required
                  />
                </div>
              </>
            ) : (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg space-y-1">
                <span className="font-bold text-emerald-900 block">Resolution Logged</span>
                <p className="text-emerald-800">{selectedConflict.resolution_notes}</p>
                <div className="text-[11px] text-emerald-700 pt-1 border-t border-emerald-200 flex justify-between">
                  <span>Resolved By: {selectedConflict.resolved_by_name}</span>
                  <span>{formatDate(selectedConflict.resolved_at)}</span>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
