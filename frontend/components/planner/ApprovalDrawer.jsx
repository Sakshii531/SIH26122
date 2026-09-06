'use client';

import React, { useState } from 'react';
import { X, CheckCircle2, XCircle, Edit3, ArrowRight, Layers, AlertCircle, FileText } from 'lucide-react';
import { ConfidenceBadge } from '../common/ConfidenceBadge.jsx';
import { ActivityReassignmentModal } from './ActivityReassignmentModal.jsx';

export function ApprovalDrawer({ item, onClose, onApprove, onOverride, onReject }) {
  if (!item) return null;

  const [notes, setNotes] = useState('');
  const [overrideProgress, setOverrideProgress] = useState(item.extractedEvent.quantity || 70);
  const [isReassignModalOpen, setIsReassignModalOpen] = useState(false);
  const [selectedL6Activity, setSelectedL6Activity] = useState(item.primaryMatch);

  return (
    <>
      <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/60 backdrop-blur-xs flex justify-end">
        <div className="w-full max-w-lg bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
            <div>
              <h2 className="font-bold text-slate-100 text-sm">Planner Verification & Match Review</h2>
              <p className="text-xs text-slate-400 mt-0.5">ID: {item.id}</p>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
            {/* Confidence Header */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 font-medium">AI Match Rating:</span>
              <ConfidenceBadge
                score={item.primaryMatch.totalConfidenceScore}
                rating={item.primaryMatch.confidenceRating}
              />
            </div>

            {/* Extracted Field Log */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-slate-400 font-medium">
                <span>Source Artifact Log:</span>
                <span className="font-mono text-cyan-400">{item.extractedEvent.sourceFileName}</span>
              </div>
              <p className="p-2.5 rounded bg-slate-900 text-slate-200 font-mono text-[11px] leading-relaxed">
                "{item.extractedEvent.rawText}"
              </p>
              <div className="flex justify-between text-slate-400 font-mono">
                <span>Extracted Qty: <strong className="text-amber-400">{item.extractedEvent.quantity} {item.extractedEvent.unit}</strong></span>
                <span>Workforce: <strong className="text-slate-200">{item.extractedEvent.workforceCount} workers</strong></span>
              </div>
            </div>

            {/* Target Primavera Activity */}
            <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-700/50 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-cyan-400 uppercase text-[10px]">Target Primavera L6 Activity</span>
                <button
                  onClick={() => setIsReassignModalOpen(true)}
                  className="px-2 py-0.5 rounded bg-cyan-900/60 hover:bg-cyan-800 text-cyan-300 font-semibold text-[10px] border border-cyan-700/60 flex items-center gap-1 transition-all"
                >
                  <Edit3 className="w-3 h-3" />
                  <span>Re-Assign Activity</span>
                </button>
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-amber-400 text-sm">{selectedL6Activity.l6ActivityCode}</span>
                  <span className="font-bold text-slate-100 text-xs">{selectedL6Activity.l6ActivityName}</span>
                </div>
                <p className="text-[11px] text-slate-400 truncate">{selectedL6Activity.wbsPath}</p>
              </div>
            </div>

            {/* Manual Progress Override Slider */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-slate-300 font-semibold">
                <span>Actual Physical Progress % Override:</span>
                <span className="font-mono text-cyan-400 text-sm">{overrideProgress}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={overrideProgress}
                onChange={(e) => setOverrideProgress(Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>

            {/* Planner Rationale Notes */}
            <div className="space-y-1">
              <label className="text-slate-300 font-semibold">Planner Verification Rationale / Audit Note:</label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Enter rationale for approval or re-assignment..."
                className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          {/* Drawer Actions Footer */}
          <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex gap-2">
            <button
              onClick={() => onReject(item.id, notes)}
              className="px-3 py-2 rounded-lg bg-rose-950/80 hover:bg-rose-900 text-rose-300 font-semibold text-xs border border-rose-800/80 transition-all flex items-center gap-1.5"
            >
              <XCircle className="w-4 h-4" />
              <span>Reject</span>
            </button>

            <button
              onClick={() => onOverride(item.id, { notes, newProgressPercent: overrideProgress, l6ActivityCode: selectedL6Activity.l6ActivityCode, l6ActivityName: selectedL6Activity.l6ActivityName })}
              className="flex-1 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-slate-950 font-semibold text-xs transition-all flex items-center justify-center gap-1.5 shadow-md"
            >
              <Edit3 className="w-4 h-4" />
              <span>Save & Override</span>
            </button>

            <button
              onClick={() => onApprove(item.id)}
              className="flex-1 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all flex items-center justify-center gap-1.5 shadow-md"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Approve Match</span>
            </button>
          </div>
        </div>
      </div>

      {/* Re-assignment Modal */}
      {isReassignModalOpen && (
        <ActivityReassignmentModal
          onClose={() => setIsReassignModalOpen(false)}
          onSelect={(act) => {
            setSelectedL6Activity(act);
            setIsReassignModalOpen(false);
          }}
        />
      )}
    </>
  );
}
