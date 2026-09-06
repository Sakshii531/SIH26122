'use client';

import React from 'react';
import { CheckSquare, CheckCircle2, XCircle, Edit3, ArrowUpRight, Filter } from 'lucide-react';
import { ConfidenceBadge } from '../common/ConfidenceBadge.jsx';
import { Button } from '../common/Button.jsx';

export function VerificationQueueTable({ items, onSelectReview, onQuickApprove, onQuickReject }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 font-mono">
              <th className="p-3">Source & Date</th>
              <th className="p-3">Extracted Field Site Log</th>
              <th className="p-3">Suggested Primavera L6 Match</th>
              <th className="p-3 text-center">Confidence</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-slate-800/50 transition-all">
                <td className="p-3">
                  <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                    {item.extractedEvent.sourceFileName}
                  </span>
                  <p className="text-[10px] text-slate-500 mt-1">{item.extractedEvent.sourceRefLocation}</p>
                </td>

                <td className="p-3 max-w-xs">
                  <p className="font-semibold text-slate-200 line-clamp-1">{item.extractedEvent.extractedActivity}</p>
                  <p className="text-[10px] font-mono text-amber-400">
                    Qty: {item.extractedEvent.quantity} {item.extractedEvent.unit}
                  </p>
                </td>

                <td className="p-3 max-w-xs">
                  <div className="flex items-center gap-1.5 text-xs">
                    <span className="font-mono font-bold text-amber-400">{item.primaryMatch.l6ActivityCode}</span>
                    <span className="font-medium text-slate-300 truncate">{item.primaryMatch.l6ActivityName}</span>
                  </div>
                  <p className="text-[10px] text-slate-400 truncate">{item.primaryMatch.wbsPath}</p>
                </td>

                <td className="p-3 text-center">
                  <ConfidenceBadge
                    score={item.primaryMatch.totalConfidenceScore}
                    rating={item.primaryMatch.confidenceRating}
                  />
                </td>

                <td className="p-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onQuickApprove(item.id)}
                      className="px-2.5 py-1 rounded bg-emerald-600/80 hover:bg-emerald-500 text-white font-medium text-xs transition-all shadow-xs flex items-center gap-1"
                      title="Approve match"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Approve</span>
                    </button>

                    <button
                      onClick={() => onSelectReview(item)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all flex items-center gap-1"
                    >
                      <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Review / Re-assign</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
