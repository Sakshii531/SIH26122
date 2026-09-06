'use client';

import React from 'react';
import { ArrowRight, Layers, Sparkles, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { ConfidenceBadge } from '../common/ConfidenceBadge.jsx';

export function SemanticMatchCard({ item }) {
  if (!item) return null;

  const { extractedEvent, primaryMatch } = item;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      {/* Card Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-100">Vector & Contextual Semantic Match</h3>
        </div>
        <ConfidenceBadge
          score={primaryMatch.totalConfidenceScore}
          rating={primaryMatch.confidenceRating}
        />
      </div>

      {/* Matching Comparison Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
        {/* Left: Extracted Field Log */}
        <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
          <span className="text-[10px] font-semibold text-slate-400 uppercase">Extracted Site Log</span>
          <p className="text-xs font-bold text-slate-200">{extractedEvent.extractedActivity}</p>
          <p className="text-[11px] font-mono text-cyan-400">
            Qty: {extractedEvent.quantity} {extractedEvent.unit}
          </p>
        </div>

        {/* Right: Target Primavera L6 Activity */}
        <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-700/50 space-y-1.5">
          <div className="flex items-center justify-between text-[10px] font-semibold">
            <span className="text-cyan-400 uppercase">Target L6 Activity</span>
            <span className="font-mono text-amber-400">{primaryMatch.l6ActivityCode}</span>
          </div>
          <p className="text-xs font-bold text-slate-100">{primaryMatch.l6ActivityName}</p>
          <p className="text-[10px] text-slate-400 truncate">{primaryMatch.wbsPath}</p>
        </div>
      </div>

      {/* Match Scores Breakdown */}
      <div className="grid grid-cols-2 gap-3 text-xs pt-1">
        <div className="p-2 rounded bg-slate-800/40 border border-slate-800 flex items-center justify-between">
          <span className="text-slate-400">Vector Embedding Similarity:</span>
          <span className="font-mono font-bold text-cyan-400">{(primaryMatch.semanticSimilarityScore * 100).toFixed(0)}%</span>
        </div>
        <div className="p-2 rounded bg-slate-800/40 border border-slate-800 flex items-center justify-between">
          <span className="text-slate-400">WBS & Date Proximity Score:</span>
          <span className="font-mono font-bold text-emerald-400">{(primaryMatch.contextualScore * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Explainable AI Rationale */}
      <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs">
        <span className="text-slate-400 font-semibold">AI Match Rationale: </span>
        <span className="text-slate-300">{primaryMatch.matchingRationale}</span>
      </div>
    </div>
  );
}
