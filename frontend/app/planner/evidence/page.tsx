'use client'

import React, { useState } from 'react'
import {
  FileCheck2,
  Image as ImageIcon,
  FileText,
  FileSpreadsheet,
  Mic,
  CheckCircle2,
  XCircle,
  Eye,
  Check,
  Building,
  Calendar,
  MapPin,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { usePlanner } from '@/context/PlannerContext'
import { EvidenceItem } from '@/types/evidence'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { Modal } from '@/components/common/Modal'
import { EmptyState } from '@/components/common/EmptyState'
import {
  formatDate,
  formatDateTime,
  getDisciplineBadgeClass,
} from '@/lib/utils'

export default function EvidencePage() {
  const { user } = useAuth()
  const {
    evidenceList,
    pendingEvidenceCount,
    verifyEvidence,
    rejectEvidence,
  } = usePlanner()

  // Filters
  const [selectedStatus, setSelectedStatus] = useState('All')
  const [selectedType, setSelectedType] = useState('All')

  // Selected Detail Modal
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null)
  const [verifyNotes, setVerifyNotes] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)

  const [rejectEvidenceItem, setRejectEvidenceItem] = useState<EvidenceItem | null>(null)
  const [rejectReason, setRejectReason] = useState('')
  const [isRejecting, setIsRejecting] = useState(false)

  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const filteredEvidence = evidenceList.filter((e) => {
    if (selectedStatus !== 'All' && e.validation_status !== selectedStatus) return false
    if (selectedType !== 'All' && e.file_type !== selectedType) return false
    return true
  })

  const handleVerify = async () => {
    if (!selectedEvidence) return
    setIsVerifying(true)
    try {
      const success = await verifyEvidence(
        selectedEvidence.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta',
        verifyNotes || 'Verified by Planner'
      )
      if (success) {
        showNotification(`Evidence ${selectedEvidence.file_name} verified successfully.`)
        setSelectedEvidence(null)
        setVerifyNotes('')
      }
    } catch (err) {
      showNotification('Failed to verify evidence.', 'error')
    } finally {
      setIsVerifying(false)
    }
  }

  const handleReject = async () => {
    if (!rejectEvidenceItem) return
    if (!rejectReason.trim()) {
      showNotification('Please specify a rejection reason.', 'error')
      return
    }

    setIsRejecting(true)
    try {
      const success = await rejectEvidence(
        rejectEvidenceItem.id,
        user?.id || 'usr-pln-01',
        user?.full_name || 'Vikram Mehta',
        rejectReason
      )
      if (success) {
        showNotification(`Evidence ${rejectEvidenceItem.file_name} rejected.`)
        setRejectEvidenceItem(null)
        setSelectedEvidence(null)
        setRejectReason('')
      }
    } catch (err) {
      showNotification('Failed to reject evidence.', 'error')
    } finally {
      setIsRejecting(false)
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Photo':
        return <ImageIcon className="w-4 h-4 text-blue-600" />
      case 'PDF':
        return <FileText className="w-4 h-4 text-rose-600" />
      case 'Excel':
        return <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
      case 'Voice':
        return <Mic className="w-4 h-4 text-purple-600" />
      default:
        return <FileText className="w-4 h-4 text-slate-600" />
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
            Field Evidence Inspection
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Inspect and validate supporting site photographs, QA/QC lab test certificates, and signed DPR documents
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            {pendingEvidenceCount} Pending Validation
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <Check className="w-3.5 h-3.5 text-emerald-600" />
            {evidenceList.filter((e) => e.validation_status === 'Verified').length} Verified
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-subtle flex flex-wrap items-center justify-between gap-4">
        {/* Status Filter Tabs */}
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">
            Validation:
          </span>
          <div className="flex items-center gap-1.5">
            {['All', 'Pending', 'Verified', 'Rejected'].map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedStatus === st
                    ? 'bg-slate-900 text-white font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Type Filter Tabs */}
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-semibold text-slate-500 uppercase">
            Type:
          </span>
          <div className="flex items-center gap-1.5">
            {['All', 'Photo', 'PDF', 'Excel'].map((tp) => (
              <button
                key={tp}
                onClick={() => setSelectedType(tp)}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedType === tp
                    ? 'bg-blue-600 text-white font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {tp}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Evidence Cards Grid */}
      {filteredEvidence.length === 0 ? (
        <EmptyState
          title="No Evidence Items Found"
          description="No evidence documents match your selected filters."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEvidence.map((ev) => (
            <div
              key={ev.id}
              className="bg-white border border-slate-200/90 rounded-xl shadow-subtle overflow-hidden flex flex-col justify-between hover:border-slate-300 transition-all"
            >
              <div>
                {/* Photo Preview or File Header */}
                {ev.file_type === 'Photo' && ev.file_url !== '#' ? (
                  <div className="relative h-40 w-full bg-slate-100 overflow-hidden border-b border-slate-100">
                    <img
                      src={ev.file_url}
                      alt={ev.file_name}
                      className="h-full w-full object-cover"
                    />
                    <span className="absolute top-2.5 left-2.5 px-2 py-0.5 rounded text-[10px] bg-slate-900/80 text-white backdrop-blur-xs font-mono">
                      Site Photograph
                    </span>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50/80 border-b border-slate-100 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center shadow-xs">
                      {getTypeIcon(ev.file_type)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <span className="font-semibold text-slate-900 block truncate text-xs">
                        {ev.file_name}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {ev.file_type} Document
                      </span>
                    </div>
                  </div>
                )}

                {/* Evidence Metadata Body */}
                <div className="p-4 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-slate-900">
                      {ev.activity_code || 'General Report'}
                    </span>
                    {ev.validation_status === 'Verified' ? (
                      <Badge variant="success">Verified</Badge>
                    ) : ev.validation_status === 'Rejected' ? (
                      <Badge variant="danger">Rejected</Badge>
                    ) : (
                      <Badge variant="warning" dot dotColor="bg-amber-500">
                        Pending
                      </Badge>
                    )}
                  </div>

                  <p className="font-medium text-slate-800 line-clamp-1">
                    {ev.activity_name || ev.report_title}
                  </p>

                  {ev.caption && (
                    <p className="text-slate-500 text-[11px] line-clamp-2">
                      "{ev.caption}"
                    </p>
                  )}

                  <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400 space-y-1">
                    <div className="flex justify-between">
                      <span>Uploaded By:</span>
                      <span className="text-slate-700 font-medium truncate max-w-[140px]">
                        {ev.uploaded_by_name}
                      </span>
                    </div>
                    <div className="flex justify-between font-mono">
                      <span>Date:</span>
                      <span className="text-slate-700">{formatDate(ev.uploaded_at)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-3 bg-slate-50/80 border-t border-slate-100 flex items-center justify-end gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setSelectedEvidence(ev)}
                  leftIcon={<Eye className="w-3.5 h-3.5" />}
                >
                  Inspect
                </Button>
                {ev.validation_status === 'Pending' && (
                  <Button
                    size="sm"
                    variant="success"
                    onClick={() => {
                      setSelectedEvidence(ev)
                      setVerifyNotes('')
                    }}
                    leftIcon={<Check className="w-3.5 h-3.5" />}
                  >
                    Verify
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Evidence Inspection Modal */}
      {selectedEvidence && (
        <Modal
          isOpen={Boolean(selectedEvidence)}
          onClose={() => setSelectedEvidence(null)}
          title={`Evidence Inspection: ${selectedEvidence.file_name}`}
          subtitle={`Linked to ${selectedEvidence.activity_code || 'Report'} • ${selectedEvidence.file_type}`}
          maxWidth="2xl"
          footer={
            selectedEvidence.validation_status === 'Pending' ? (
              <div className="flex items-center justify-between w-full">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRejectEvidenceItem(selectedEvidence)}
                  leftIcon={<XCircle className="w-4 h-4 text-rose-600" />}
                >
                  Reject Evidence
                </Button>
                <div className="flex items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setSelectedEvidence(null)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={handleVerify}
                    isLoading={isVerifying}
                    leftIcon={<Check className="w-4 h-4" />}
                  >
                    Verify & Confirm
                  </Button>
                </div>
              </div>
            ) : (
              <Button variant="secondary" size="sm" onClick={() => setSelectedEvidence(null)}>
                Close
              </Button>
            )
          }
        >
          <div className="space-y-4 text-xs">
            {/* Visual Preview if Photo */}
            {selectedEvidence.file_type === 'Photo' && selectedEvidence.file_url !== '#' && (
              <div className="rounded-lg overflow-hidden border border-slate-200 max-h-72 bg-black flex items-center justify-center">
                <img
                  src={selectedEvidence.file_url}
                  alt={selectedEvidence.file_name}
                  className="max-h-72 w-auto object-contain"
                />
              </div>
            )}

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-700">
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  Activity Code & Name:
                </span>
                <span className="font-bold text-slate-900 block font-mono mt-0.5">
                  {selectedEvidence.activity_code}
                </span>
                <span className="text-slate-600 text-[11px]">
                  {selectedEvidence.activity_name}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  Source Field Report:
                </span>
                <span className="font-medium text-slate-800 block mt-0.5">
                  {selectedEvidence.report_title}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  Uploaded By:
                </span>
                <span className="font-medium text-slate-800 block mt-0.5">
                  {selectedEvidence.uploaded_by_name}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                  Uploaded Timestamp:
                </span>
                <span className="font-mono text-slate-800 block mt-0.5">
                  {formatDateTime(selectedEvidence.uploaded_at)}
                </span>
              </div>
            </div>

            {selectedEvidence.gps_coordinates && (
              <div className="flex items-center gap-2 p-2.5 bg-blue-50/60 border border-blue-100 rounded-lg text-blue-900 text-xs">
                <MapPin className="w-4 h-4 text-blue-600 shrink-0" />
                <span>GPS Location Tag: {selectedEvidence.gps_coordinates}</span>
              </div>
            )}

            {selectedEvidence.validation_status === 'Pending' ? (
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Planner QA Notes (Optional):
                </label>
                <textarea
                  value={verifyNotes}
                  onChange={(e) => setVerifyNotes(e.target.value)}
                  placeholder="Add remarks regarding visual verification or laboratory test compliance..."
                  rows={2}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-blue-600 focus:outline-none"
                />
              </div>
            ) : (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                <span className="font-bold text-emerald-900 block">
                  Validation Status: {selectedEvidence.validation_status}
                </span>
                {selectedEvidence.validation_notes && (
                  <p className="text-emerald-800 text-xs mt-1">
                    "{selectedEvidence.validation_notes}"
                  </p>
                )}
                <span className="text-[11px] text-emerald-700 block mt-1">
                  Validated by {selectedEvidence.validated_by_name} on{' '}
                  {formatDate(selectedEvidence.validated_at)}
                </span>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Reject Evidence Modal */}
      {rejectEvidenceItem && (
        <Modal
          isOpen={Boolean(rejectEvidenceItem)}
          onClose={() => setRejectEvidenceItem(null)}
          title="Reject Evidence Document"
          subtitle="Document the technical or QA deficiency requiring rejection"
          footer={
            <>
              <Button variant="secondary" size="sm" onClick={() => setRejectEvidenceItem(null)}>
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
                Rejection Reason: <span className="text-rose-500">*</span>
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Explain why this evidence is invalid (e.g., blurred photograph, missing QA signatures, mismatched spool tags)..."
                rows={3}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-rose-500 focus:outline-none"
                required
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
