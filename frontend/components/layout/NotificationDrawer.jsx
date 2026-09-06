'use client';

import React from 'react';
import { X, AlertTriangle, ArrowRight, ShieldAlert, CheckCircle } from 'lucide-react';
import { MOCK_EXTRACTIONS_AND_MATCHES } from '../../services/mock/mockExtractions.js';
import { ConfidenceBadge } from '../common/ConfidenceBadge.jsx';

export function NotificationDrawer({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white border-l border-slate-200 h-full flex flex-col shadow-2xl animate-fade-in">
        {/* Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            <h2 className="font-bold text-slate-900 text-sm">Planner Action Inbox (4 Pending)</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <p className="text-xs text-slate-500 mb-2">
            Site report updates awaiting planner verification before updating Primavera P6 / MS Project:
          </p>

          {MOCK_EXTRACTIONS_AND_MATCHES.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 hover:border-blue-300 transition-all space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 font-semibold">
                  {item.extractedEvent.sourceFileName}
                </span>
                <ConfidenceBadge
                  score={item.primaryMatch.totalConfidenceScore}
                  rating={item.primaryMatch.confidenceRating}
                />
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-800 line-clamp-2">
                  "{item.extractedEvent.rawText}"
                </p>
              </div>

              <div className="p-2 rounded-lg bg-white border border-slate-200 text-[11px]">
                <span className="text-slate-500 font-medium">Suggested L6 Match: </span>
                <span className="font-mono text-amber-600 font-bold">{item.primaryMatch.l6ActivityCode}</span>
                <p className="text-[11px] text-slate-800 font-semibold line-clamp-1">{item.primaryMatch.l6ActivityName}</p>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] text-slate-500 font-mono">Qty: {item.extractedEvent.quantity} {item.extractedEvent.unit}</span>
                <a
                  href="/verification"
                  onClick={onClose}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 transition-all"
                >
                  <span>Verify in Queue</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <a
            href="/verification"
            onClick={onClose}
            className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs flex items-center justify-center gap-2 transition-all shadow-xs"
          >
            <span>Open Full Verification Queue</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
