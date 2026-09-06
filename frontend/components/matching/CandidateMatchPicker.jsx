'use client';

import React from 'react';
import { Layers, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { ConfidenceBadge } from '../common/ConfidenceBadge.jsx';

export function CandidateMatchPicker({ candidates, selectedId, onSelect }) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
      <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
        <Layers className="w-4 h-4 text-cyan-400" />
        Alternative L6 Candidate Matches ({candidates.length})
      </h3>

      <div className="space-y-2">
        {candidates.map((cand) => {
          const isSelected = selectedId === cand.l6ActivityId;
          return (
            <div
              key={cand.l6ActivityId}
              onClick={() => onSelect && onSelect(cand)}
              className={`p-3 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                isSelected
                  ? 'bg-cyan-950/80 border-cyan-500 text-cyan-200'
                  : 'bg-slate-950/40 border-slate-800 hover:bg-slate-800'
              }`}
            >
              <div className="space-y-0.5 max-w-[80%]">
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-mono font-bold text-amber-400">{cand.l6ActivityCode}</span>
                  <span className="font-semibold text-slate-200 truncate">{cand.l6ActivityName}</span>
                </div>
                <p className="text-[10px] text-slate-400 truncate">{cand.wbsPath}</p>
              </div>

              <ConfidenceBadge score={cand.totalConfidenceScore} rating={cand.confidenceRating} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
