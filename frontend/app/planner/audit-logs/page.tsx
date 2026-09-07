'use client'

import React, { useState } from 'react'
import {
  History,
  Search,
  Filter,
  User,
  Shield,
  FileText,
  Clock,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code,
  Tag,
} from 'lucide-react'
import { usePlanner } from '@/context/PlannerContext'
import { AuditLog, AuditActionType } from '@/types/database'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { EmptyState } from '@/components/common/EmptyState'
import { formatDateTime } from '@/lib/utils'

export default function AuditLogsPage() {
  const { auditLogs } = usePlanner()

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAction, setSelectedAction] = useState<string>('All')
  const [selectedEntity, setSelectedEntity] = useState<string>('All')

  // Expanded row for JSON inspection
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null)

  const filteredLogs = auditLogs.filter((l) => {
    if (selectedAction !== 'All' && l.action !== selectedAction) return false
    if (selectedEntity !== 'All' && l.entity !== selectedEntity) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matches =
        l.user_name.toLowerCase().includes(q) ||
        l.action.toLowerCase().includes(q) ||
        l.entity.toLowerCase().includes(q) ||
        l.entity_id.toLowerCase().includes(q) ||
        JSON.stringify(l.details).toLowerCase().includes(q)
      if (!matches) return false
    }

    return true
  })

  const getActionBadge = (action: AuditActionType) => {
    switch (action) {
      case 'Match Approved':
      case 'Evidence Verified':
      case 'Conflict Resolved':
        return <Badge variant="success">{action}</Badge>
      case 'Match Corrected':
      case 'Progress Updated':
        return <Badge variant="info">{action}</Badge>
      case 'Match Rejected':
      case 'Evidence Rejected':
        return <Badge variant="danger">{action}</Badge>
      case 'Conflict Created':
        return <Badge variant="warning">{action}</Badge>
      case 'Report Submitted':
      case 'Activity Extracted':
      case 'Activity Matched':
      default:
        return <Badge variant="neutral">{action}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            System Execution Audit Trail
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable chronological ledger of AI extractions, semantic matches, and human Planner validations
          </p>
        </div>
        <Badge variant="neutral">{auditLogs.length} Audit Events Logged</Badge>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search */}
          <div className="sm:col-span-2">
            <Input
              placeholder="Search user, action, entity ID, or details..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="w-4 h-4" />}
            />
          </div>

          {/* Action Filter */}
          <div>
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 focus:border-blue-600 focus:outline-none"
            >
              <option value="All">All Actions</option>
              <option value="Match Approved">Match Approved</option>
              <option value="Match Corrected">Match Corrected</option>
              <option value="Match Rejected">Match Rejected</option>
              <option value="Conflict Created">Conflict Created</option>
              <option value="Conflict Resolved">Conflict Resolved</option>
              <option value="Evidence Verified">Evidence Verified</option>
              <option value="Progress Updated">Progress Updated</option>
              <option value="Report Submitted">Report Submitted</option>
              <option value="Activity Matched">Activity Matched</option>
            </select>
          </div>

          {/* Entity Filter */}
          <div>
            <select
              value={selectedEntity}
              onChange={(e) => setSelectedEntity(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 focus:border-blue-600 focus:outline-none"
            >
              <option value="All">All Entities</option>
              <option value="FieldReport">FieldReport</option>
              <option value="ActivityMatch">ActivityMatch</option>
              <option value="PlannerReview">PlannerReview</option>
              <option value="Conflict">Conflict</option>
              <option value="Evidence">Evidence</option>
              <option value="ActualProgress">ActualProgress</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      {filteredLogs.length === 0 ? (
        <EmptyState
          title="No Audit Records Found"
          description="No audit trail events match the selected criteria."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('')
            setSelectedAction('All')
            setSelectedEntity('All')
          }}
        />
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Timestamp</th>
                  <th className="py-2.5 px-4">User / Actor</th>
                  <th className="py-2.5 px-4">Action</th>
                  <th className="py-2.5 px-4">Target Entity</th>
                  <th className="py-2.5 px-4">Entity ID</th>
                  <th className="py-2.5 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLogs.map((entry) => {
                  const isExpanded = expandedRowId === entry.id
                  return (
                    <React.Fragment key={entry.id}>
                      <tr
                        onClick={() => setExpandedRowId(isExpanded ? null : entry.id)}
                        className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                      >
                        {/* Timestamp */}
                        <td className="py-3 px-4 font-mono text-slate-600 whitespace-nowrap">
                          {formatDateTime(entry.timestamp)}
                        </td>

                        {/* User / Role */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1.5">
                            <span className="font-semibold text-slate-900">
                              {entry.user_name}
                            </span>
                            <span className="text-[10px] text-slate-400 font-medium">
                              ({entry.user_role})
                            </span>
                          </div>
                        </td>

                        {/* Action Badge */}
                        <td className="py-3 px-4">
                          {getActionBadge(entry.action)}
                        </td>

                        {/* Target Entity */}
                        <td className="py-3 px-4">
                          <span className="font-mono text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded text-[11px]">
                            {entry.entity}
                          </span>
                        </td>

                        {/* Entity ID */}
                        <td className="py-3 px-4 font-mono text-slate-500">
                          {entry.entity_id}
                        </td>

                        {/* Expansion Toggle */}
                        <td className="py-3 px-4 text-right text-slate-400">
                          <div className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium text-xs">
                            <span>{isExpanded ? 'Hide' : 'Inspect'}</span>
                            {isExpanded ? (
                              <ChevronDown className="w-3.5 h-3.5" />
                            ) : (
                              <ChevronRight className="w-3.5 h-3.5" />
                            )}
                          </div>
                        </td>
                      </tr>

                      {/* Expanded JSON Inspector */}
                      {isExpanded && (
                        <tr className="bg-slate-50/80">
                          <td colSpan={6} className="px-6 py-4">
                            <div className="p-3 bg-slate-900 text-slate-200 rounded-lg font-mono text-[11px] overflow-x-auto space-y-1 shadow-inner">
                              <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-1 mb-2">
                                <span className="font-sans font-semibold uppercase text-[10px]">
                                  Audit Payload & Context
                                </span>
                                <span>IP: {entry.ip_address || '127.0.0.1'}</span>
                              </div>
                              <pre>{JSON.stringify(entry.details, null, 2)}</pre>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
