'use client'

import React, { useState } from 'react'
import {
  CheckSquare,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Edit3,
  AlertTriangle,
  Eye,
  FileText,
  Mic,
  FileSpreadsheet,
  Image as ImageIcon,
  Check,
  Building,
  Calendar,
  User,
  HelpCircle,
  ExternalLink,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { usePlanner } from '@/context/PlannerContext'
import { ReviewQueueItem, RejectionReason } from '@/types/review'
import { Activity } from '@/types/database'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'
import { Modal } from '@/components/common/Modal'
import { Drawer } from '@/components/common/Drawer'
import { EmptyState } from '@/components/common/EmptyState'
import {
  formatDate,
  getConfidenceBadgeProps,
  getDisciplineBadgeClass,
} from '@/lib/utils'

export default function ReviewQueuePage() {
  const { user } = useAuth()
  const {
    reviews,
    pendingReviewsCount,
    approveReview,
    correctReview,
    rejectReview,
    activities,
  } = usePlanner()

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDiscipline, setSelectedDiscipline] = useState<string>('All')
  const [selectedConfidence, setSelectedConfidence] = useState<string>('All')
  const [selectedStatus, setSelectedStatus] = useState<string>('All')

  // Modals / Drawers state
  const [selectedReview, setSelectedReview] = useState<ReviewQueueItem | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)

  // Action states
  const [approveConfirmItem, setApproveConfirmItem] = useState<ReviewQueueItem | null>(null)
  const [isApproving, setIsApproving] = useState(false)

  const [correctItem, setCorrectItem] = useState<ReviewQueueItem | null>(null)
  const [activitySearchQuery, setActivitySearchQuery] = useState('')
  const [selectedCorrectActivity, setSelectedCorrectActivity] = useState<Activity | null>(null)
  const [correctionNotes, setCorrectionNotes] = useState('')
  const [isCorrecting, setIsCorrecting] = useState(false)

  const [rejectItem, setRejectItem] = useState<ReviewQueueItem | null>(null)
  const [rejectReason, setRejectReason] = useState<RejectionReason>('Incorrect activity')
  const [rejectNotes, setRejectNotes] = useState('')
  const [isRejecting, setIsRejecting] = useState(false)

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 4000)
  }

  // Filter reviews
  const filteredReviews = reviews.filter((item) => {
    if (selectedStatus !== 'All' && item.status !== selectedStatus) return false
    if (selectedDiscipline !== 'All' && item.discipline !== selectedDiscipline) return false
    if (selectedConfidence === 'High' && item.confidence_score < 70) return false
    if (
      selectedConfidence === 'Medium' &&
      (item.confidence_score < 50 || item.confidence_score >= 70)
    )
      return false
    if (selectedConfidence === 'Low' && item.confidence_score >= 50) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchesText =
        item.report_title.toLowerCase().includes(q) ||
        item.extracted_activity_desc.toLowerCase().includes(q) ||
        item.suggested_activity_code.toLowerCase().includes(q) ||
        item.suggested_activity_name.toLowerCase().includes(q) ||
        item.submitted_by.toLowerCase().includes(q)
      if (!matchesText) return false
    }

    return true
  })

  // Handle Approve Action
  const handleApprove = async () => {
    if (!approveConfirmItem) return
    setIsApproving(true)
    try {
      const success = await approveReview(
        approveConfirmItem.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta'
      )
      if (success) {
        showNotification(
          `Match for ${approveConfirmItem.suggested_activity_code} approved successfully.`
        )
        setApproveConfirmItem(null)
        setIsDetailOpen(false)
      }
    } catch (err) {
      showNotification('Failed to approve match.', 'error')
    } finally {
      setIsApproving(false)
    }
  }

  // Handle Correct Action
  const handleCorrect = async () => {
    if (!correctItem || !selectedCorrectActivity) return
    setIsCorrecting(true)
    try {
      const success = await correctReview(
        correctItem.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta',
        selectedCorrectActivity,
        correctionNotes
      )
      if (success) {
        showNotification(
          `Match corrected to ${selectedCorrectActivity.activity_code} (${selectedCorrectActivity.activity_name}).`
        )
        setCorrectItem(null)
        setSelectedCorrectActivity(null)
        setCorrectionNotes('')
        setIsDetailOpen(false)
      }
    } catch (err) {
      showNotification('Failed to correct match.', 'error')
    } finally {
      setIsCorrecting(false)
    }
  }

  // Handle Reject Action
  const handleReject = async () => {
    if (!rejectItem) return
    setIsRejecting(true)
    try {
      const success = await rejectReview(
        rejectItem.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta',
        rejectReason,
        rejectNotes
      )
      if (success) {
        showNotification(
          `Match for ${rejectItem.suggested_activity_code} rejected. Reason: ${rejectReason}`
        )
        setRejectItem(null)
        setRejectNotes('')
        setIsDetailOpen(false)
      }
    } catch (err) {
      showNotification('Failed to reject match.', 'error')
    } finally {
      setIsRejecting(false)
    }
  }

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'Voice':
        return <Mic className="w-3.5 h-3.5 text-purple-600" />
      case 'Excel':
        return <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
      case 'PDF':
        return <FileText className="w-3.5 h-3.5 text-rose-600" />
      default:
        return <FileText className="w-3.5 h-3.5 text-blue-600" />
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
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
            )}
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

      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900">
            Planner Review Queue
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Validate semantic AI match proposals before updating official Primavera P6 L5/L6 activities
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            {pendingReviewsCount} Pending Validation
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <Check className="w-3.5 h-3.5 text-emerald-600" />
            {reviews.filter((r) => r.status === 'Approved').length} Approved
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search - spans 2 cols */}
          <div className="sm:col-span-2">
            <Input
              placeholder="Search DPRs, activity codes, descriptions, supervisors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="w-4 h-4" />}
            />
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="filter-select"
              aria-label="Filter by status"
            >
              <option value="All">All Statuses</option>
              <option value="Needs Review">Needs Review</option>
              <option value="Approved">Approved</option>
              <option value="Corrected">Corrected</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>

          {/* Discipline Filter */}
          <div>
            <select
              value={selectedDiscipline}
              onChange={(e) => setSelectedDiscipline(e.target.value)}
              className="filter-select"
              aria-label="Filter by discipline"
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
        </div>

        {/* Second filter row: Confidence */}
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">Confidence:</span>
          <select
            value={selectedConfidence}
            onChange={(e) => setSelectedConfidence(e.target.value)}
            className="filter-select w-auto min-w-[180px]"
            aria-label="Filter by confidence"
          >
            <option value="All">All Confidence Levels</option>
            <option value="High">High (≥ 70%)</option>
            <option value="Medium">Medium (50–69%)</option>
            <option value="Low">Low (&lt; 50%)</option>
          </select>
          {(searchQuery || selectedStatus !== 'All' || selectedDiscipline !== 'All' || selectedConfidence !== 'All') && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('')
                setSelectedStatus('All')
                setSelectedDiscipline('All')
                setSelectedConfidence('All')
              }}
              className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Review Queue Table */}
      {filteredReviews.length === 0 ? (
        <EmptyState
          title="No Reviews Found"
          description="There are currently no review items matching your active filter criteria."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('')
            setSelectedDiscipline('All')
            setSelectedConfidence('All')
            setSelectedStatus('All')
          }}
        />
      ) : (
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Report Source</th>
                  <th className="py-2.5 px-4">Extracted Work Description</th>
                  <th className="py-2.5 px-4">Discipline</th>
                  <th className="py-2.5 px-4">Suggested L5/L6 Activity</th>
                  <th className="py-2.5 px-4 text-center">Confidence</th>
                  <th className="py-2.5 px-4">Date</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredReviews.map((item) => {
                  const confBadge = getConfidenceBadgeProps(item.confidence_score)
                  return (
                    <tr
                      key={item.id}
                      className={`hover:bg-slate-50/70 transition-colors ${
                        item.status === 'Approved' ? 'bg-emerald-50/20' : ''
                      }`}
                    >
                      {/* Report / Source */}
                      <td className="py-3 px-4">
                        <div className="flex items-start gap-2">
                          <span className="mt-0.5">{getSourceIcon(item.report_source)}</span>
                          <div>
                            <span className="font-semibold text-slate-900 block truncate max-w-[160px]">
                              {item.report_title}
                            </span>
                            <span className="text-[11px] text-slate-400 block truncate max-w-[160px]">
                              {item.submitted_by}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Extracted Work */}
                      <td className="py-3 px-4">
                        <p className="text-slate-800 font-medium line-clamp-2 max-w-[220px]">
                          {item.extracted_activity_desc}
                        </p>
                        {item.reported_progress_percent !== undefined && (
                          <span className="text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.2 rounded border border-blue-100 mt-1 inline-block">
                            Reported: {item.reported_progress_percent}%
                          </span>
                        )}
                      </td>

                      {/* Discipline */}
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                            item.discipline
                          )}`}
                        >
                          {item.discipline}
                        </span>
                      </td>

                      {/* Suggested Activity */}
                      <td className="py-3 px-4">
                        <div>
                          <span className="font-mono font-bold text-slate-900">
                            {item.suggested_activity_code}
                          </span>
                          <p className="text-slate-600 text-[11px] truncate max-w-[180px]">
                            {item.suggested_activity_name}
                          </p>
                        </div>
                      </td>

                      {/* Confidence Score Badge */}
                      <td className="py-3 px-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${confBadge.className}`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${confBadge.dotColor}`} />
                          {confBadge.label}
                        </span>
                      </td>

                      {/* Date */}
                      <td className="py-3 px-4 text-slate-500 font-mono">
                        {formatDate(item.report_date)}
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        {item.status === 'Approved' ? (
                          <Badge variant="success">Approved</Badge>
                        ) : item.status === 'Corrected' ? (
                          <Badge variant="info">Corrected</Badge>
                        ) : item.status === 'Rejected' ? (
                          <Badge variant="danger">Rejected</Badge>
                        ) : (
                          <Badge variant="warning" dot dotColor="bg-amber-500">
                            Needs Review
                          </Badge>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => {
                              setSelectedReview(item)
                              setIsDetailOpen(true)
                            }}
                            leftIcon={<Eye className="w-3.5 h-3.5" />}
                          >
                            Review
                          </Button>

                          {item.status === 'Needs Review' && (
                            <>
                              <Button
                                size="sm"
                                variant="success"
                                onClick={() => setApproveConfirmItem(item)}
                                title="Approve match"
                              >
                                <Check className="w-3.5 h-3.5" />
                              </Button>

                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setCorrectItem(item)
                                  setSelectedCorrectActivity(null)
                                }}
                                title="Correct match"
                              >
                                <Edit3 className="w-3.5 h-3.5 text-blue-600" />
                              </Button>

                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setRejectItem(item)}
                                title="Reject match"
                              >
                                <XCircle className="w-3.5 h-3.5 text-rose-600" />
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Review Detail Drawer */}
      {selectedReview && (
        <Drawer
          isOpen={isDetailOpen}
          onClose={() => setIsDetailOpen(false)}
          title={`Review Match: ${selectedReview.suggested_activity_code}`}
          subtitle={`Submitted via ${selectedReview.report_source} on ${formatDate(
            selectedReview.report_date
          )}`}
          width="2xl"
          footer={
            selectedReview.status === 'Needs Review' ? (
              <div className="flex items-center gap-2 w-full justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setRejectItem(selectedReview)
                  }}
                  leftIcon={<XCircle className="w-4 h-4 text-rose-600" />}
                >
                  Reject Match
                </Button>
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      setCorrectItem(selectedReview)
                      setSelectedCorrectActivity(null)
                    }}
                    leftIcon={<Edit3 className="w-4 h-4 text-blue-600" />}
                  >
                    Correct Match
                  </Button>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={() => setApproveConfirmItem(selectedReview)}
                    leftIcon={<Check className="w-4 h-4" />}
                  >
                    Approve Match
                  </Button>
                </div>
              </div>
            ) : (
              <div className="w-full text-right text-xs text-slate-500">
                This match is marked as <strong>{selectedReview.status}</strong>.
              </div>
            )
          }
        >
          <div className="space-y-5 text-xs">
            {/* Step 1: Ingested Field Report */}
            <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
                  1. Ingested Field Report
                </span>
                <span className="text-slate-500 font-mono">
                  {formatDate(selectedReview.report_date)}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-slate-600">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Title:</span>
                  <span className="font-semibold text-slate-800">
                    {selectedReview.report_title}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Submitted By:</span>
                  <span className="font-semibold text-slate-800">
                    {selectedReview.submitted_by}
                  </span>
                </div>
              </div>
              <div className="mt-2 pt-2 border-t border-slate-200">
                <span className="text-slate-400 block text-[10px] uppercase mb-1">
                  Original Raw Text / Audio Transcript:
                </span>
                <p className="bg-white p-2.5 rounded-lg border border-slate-200 text-slate-800 font-mono text-[11px] leading-relaxed">
                  "{selectedReview.original_report_text}"
                </p>
              </div>
            </div>

            {/* Step 2: Extracted Progress Entities */}
            <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
                  2. Extracted Progress Entities
                </span>
                <span
                  className={`inline-block px-2 py-0.5 rounded text-[11px] border ${getDisciplineBadgeClass(
                    selectedReview.discipline
                  )}`}
                >
                  {selectedReview.discipline}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-slate-600">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Work Description:</span>
                  <span className="font-semibold text-slate-800">
                    {selectedReview.extracted_activity_desc}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase">Location:</span>
                  <span className="font-semibold text-slate-800">
                    {selectedReview.location}
                  </span>
                </div>
                {selectedReview.reported_progress_percent !== undefined && (
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase">Reported Progress:</span>
                    <span className="font-bold text-blue-600 text-sm font-mono">
                      {selectedReview.reported_progress_percent}%
                    </span>
                  </div>
                )}
                {selectedReview.reported_quantity !== undefined && (
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase">Quantity:</span>
                    <span className="font-semibold text-slate-800 font-mono">
                      {selectedReview.reported_quantity} units
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Step 3: AI Candidate Activity Match & Reasoning */}
            <div className="bg-blue-50/40 p-4 rounded-xl border border-blue-200 space-y-3">
              <div className="flex items-center justify-between border-b border-blue-200/60 pb-2">
                <span className="font-bold text-blue-950 uppercase tracking-wider text-[11px]">
                  3. Suggested Schedule Activity
                </span>
                <span
                  className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                    getConfidenceBadgeProps(selectedReview.confidence_score).className
                  }`}
                >
                  {getConfidenceBadgeProps(selectedReview.confidence_score).label}
                </span>
              </div>

              <div className="bg-white p-3 rounded-lg border border-blue-100 shadow-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-slate-900 text-sm">
                    {selectedReview.suggested_activity_code}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    WBS: {selectedReview.suggested_wbs_code}
                  </span>
                </div>
                <p className="font-semibold text-slate-800 text-xs">
                  {selectedReview.suggested_activity_name}
                </p>
                <p className="text-slate-500 text-[11px]">
                  Hierarchy: {selectedReview.suggested_wbs_name}
                </p>
              </div>

              <div>
                <span className="text-blue-950 font-semibold block mb-1 text-[11px]">
                  Matching Engine Reasoning:
                </span>
                <p className="text-slate-700 bg-white p-2.5 rounded-lg border border-blue-100 text-xs leading-relaxed">
                  {selectedReview.match_reasoning}
                </p>
              </div>
            </div>

            {/* Step 4: Attached Evidence */}
            {selectedReview.evidence_attachments.length > 0 && (
              <div className="bg-slate-50/80 p-4 rounded-xl border border-slate-200 space-y-2">
                <span className="font-bold text-slate-900 uppercase tracking-wider text-[11px] block border-b border-slate-200 pb-2">
                  4. Attached Field Evidence ({selectedReview.evidence_attachments.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                  {selectedReview.evidence_attachments.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center gap-2.5 shadow-xs"
                    >
                      {ev.file_type === 'Photo' ? (
                        <ImageIcon className="w-5 h-5 text-blue-600 shrink-0" />
                      ) : (
                        <FileText className="w-5 h-5 text-rose-600 shrink-0" />
                      )}
                      <div className="min-w-0 flex-1">
                        <span className="font-medium text-slate-800 block truncate">
                          {ev.file_name}
                        </span>
                        {ev.caption && (
                          <span className="text-[10px] text-slate-400 block truncate">
                            {ev.caption}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Drawer>
      )}

      {/* Approve Confirmation Modal */}
      {approveConfirmItem && (
        <Modal
          isOpen={Boolean(approveConfirmItem)}
          onClose={() => setApproveConfirmItem(null)}
          title="Approve Activity Match"
          subtitle="Confirm linkage of field progress report to planned schedule activity"
          footer={
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setApproveConfirmItem(null)}
              >
                Cancel
              </Button>
              <Button
                variant="success"
                size="sm"
                onClick={handleApprove}
                isLoading={isApproving}
              >
                Confirm Approval
              </Button>
            </>
          }
        >
          <div className="space-y-3 text-xs text-slate-600">
            <p>
              Are you sure you want to approve the AI match linking this report to activity{' '}
              <strong className="text-slate-900 font-mono">
                {approveConfirmItem.suggested_activity_code}
              </strong>
              ?
            </p>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
              <p>
                <strong>Activity:</strong> {approveConfirmItem.suggested_activity_name}
              </p>
              <p>
                <strong>Discipline:</strong> {approveConfirmItem.discipline}
              </p>
              <p>
                <strong>Confidence Score:</strong> {approveConfirmItem.confidence_score}%
              </p>
            </div>
            <p className="text-[11px] text-slate-500">
              Approving will immediately update the physical progress and record an entry in the system audit trail.
            </p>
          </div>
        </Modal>
      )}

      {/* Correct Match Modal (Searchable L5/L6 Activity Picker) */}
      {correctItem && (
        <Modal
          isOpen={Boolean(correctItem)}
          onClose={() => setCorrectItem(null)}
          title="Correct Activity Match"
          subtitle="Select the correct L5/L6 planned schedule activity to override the AI suggestion"
          maxWidth="2xl"
          footer={
            <>
              <Button variant="secondary" size="sm" onClick={() => setCorrectItem(null)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={!selectedCorrectActivity}
                onClick={handleCorrect}
                isLoading={isCorrecting}
              >
                Confirm Correction
              </Button>
            </>
          }
        >
          <div className="space-y-4 text-xs">
            {/* Current Suggestion Warning */}
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900">
              <span className="font-semibold block mb-0.5">Current AI Suggestion:</span>
              <span className="font-mono font-bold">{correctItem.suggested_activity_code}</span> —{' '}
              {correctItem.suggested_activity_name}
            </div>

            {/* Search Input for Activities */}
            <div>
              <Input
                label="Search L5/L6 Baseline Activities"
                placeholder="Search by code (e.g., PIP-L5, CIV-L5), name, or discipline..."
                value={activitySearchQuery}
                onChange={(e) => setActivitySearchQuery(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>

            {/* Activity Selection List */}
            <div className="max-h-60 overflow-y-auto space-y-2 border border-slate-200 rounded-lg p-2 bg-slate-50">
              {activities
                .filter((act) => {
                  if (!activitySearchQuery.trim()) return true
                  const q = activitySearchQuery.toLowerCase()
                  return (
                    act.activity_code.toLowerCase().includes(q) ||
                    act.activity_name.toLowerCase().includes(q) ||
                    act.discipline.toLowerCase().includes(q) ||
                    act.wbs_code.toLowerCase().includes(q)
                  )
                })
                .map((act) => {
                  const isSelected = selectedCorrectActivity?.id === act.id
                  return (
                    <div
                      key={act.id}
                      onClick={() => setSelectedCorrectActivity(act)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-blue-50 border-blue-600 ring-1 ring-blue-600 shadow-xs'
                          : 'bg-white border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-slate-900">
                            {act.activity_code}
                          </span>
                          <span
                            className={`px-1.5 py-0.2 rounded text-[10px] border ${getDisciplineBadgeClass(
                              act.discipline
                            )}`}
                          >
                            {act.discipline}
                          </span>
                        </div>
                        <span className="font-mono text-[11px] text-slate-500">
                          WBS: {act.wbs_code}
                        </span>
                      </div>
                      <p className="font-medium text-slate-800 text-xs mt-1">
                        {act.activity_name}
                      </p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{act.location}</p>
                    </div>
                  )
                })}
            </div>

            {/* Notes Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Correction Justification / Notes:
              </label>
              <textarea
                value={correctionNotes}
                onChange={(e) => setCorrectionNotes(e.target.value)}
                placeholder="Explain why this activity was chosen instead of the AI suggestion..."
                rows={2}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>
        </Modal>
      )}

      {/* Reject Modal */}
      {rejectItem && (
        <Modal
          isOpen={Boolean(rejectItem)}
          onClose={() => setRejectItem(null)}
          title="Reject Activity Match"
          subtitle="Specify reason for rejecting this AI match recommendation"
          footer={
            <>
              <Button variant="secondary" size="sm" onClick={() => setRejectItem(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={handleReject}
                isLoading={isRejecting}
              >
                Confirm Rejection
              </Button>
            </>
          }
        >
          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Rejection Reason:
              </label>
              <select
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value as RejectionReason)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-rose-500 focus:outline-none"
              >
                <option value="Incorrect activity">Incorrect activity</option>
                <option value="Insufficient evidence">Insufficient evidence</option>
                <option value="Duplicate report">Duplicate report</option>
                <option value="Invalid information">Invalid information</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Planner Comments (Optional):
              </label>
              <textarea
                value={rejectNotes}
                onChange={(e) => setRejectNotes(e.target.value)}
                placeholder="Add any remarks regarding the rejection..."
                rows={3}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-rose-500 focus:outline-none"
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
