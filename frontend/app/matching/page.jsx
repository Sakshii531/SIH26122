'use client';

import React, { useState, useEffect } from 'react';
import { aiService } from '../../services/aiService.js';
import { ExtractionResultCard } from '../../components/matching/ExtractionResultCard.jsx';
import { SemanticMatchCard } from '../../components/matching/SemanticMatchCard.jsx';
import { CandidateMatchPicker } from '../../components/matching/CandidateMatchPicker.jsx';
import { Cpu, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function MatchingPage() {
  const [items, setItems] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    aiService.getAllExtractedMatches().then(setItems);
  }, []);

  const activeItem = items[selectedIndex];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-cyan-400" />
            AI Extraction & Semantic Activity Matching Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Review parsed field entities, vector similarity scores, and schedule context matching
          </p>
        </div>
      </div>

      {/* Main Grid */}
      {activeItem ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <ExtractionResultCard event={activeItem.extractedEvent} />
            <SemanticMatchCard item={activeItem} />
          </div>

          <div className="space-y-6">
            <CandidateMatchPicker
              candidates={activeItem.alternateCandidates}
              selectedId={activeItem.primaryMatch.l6ActivityId}
            />

            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-slate-200">Ingested Site Report Items ({items.length})</h4>
              <div className="space-y-1.5">
                {items.map((it, idx) => (
                  <button
                    key={it.id}
                    onClick={() => setSelectedIndex(idx)}
                    className={`w-full text-left p-2.5 rounded-lg text-xs transition-all flex items-center justify-between ${
                      selectedIndex === idx
                        ? 'bg-cyan-950/80 border border-cyan-500 text-cyan-300'
                        : 'hover:bg-slate-800 text-slate-400'
                    }`}
                  >
                    <span className="truncate max-w-[180px]">{it.extractedEvent.extractedActivity}</span>
                    <span className="font-mono text-[10px] text-amber-400">{it.primaryMatch.totalConfidenceScore}%</span>
                  </button>
                ))}
              </div>

              <a
                href="/verification"
                className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md mt-4"
              >
                <span>Proceed to Planner Verification Queue</span>
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12 text-slate-400 text-xs">Loading AI matching engine results...</div>
      )}
    </div>
  );
}
