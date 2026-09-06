'use client';

import React, { useState } from 'react';
import { FileSearch, FileText, FileSpreadsheet, Mic, CheckCircle2, ExternalLink, ArrowRight } from 'lucide-react';
import { Card } from '../common/Card.jsx';
import { Badge } from '../common/Badge.jsx';

const mockTraceabilityLinks = [
  {
    id: 'TRACE-1049',
    l6Code: '1.2.4.1.B',
    l6Name: 'Pier 14 M45 Concrete Pouring & Curing (Lift 2)',
    approvedProgress: 65,
    sourceType: 'DSR_PDF',
    sourceFile: 'DSR_2026_09_05_Zone3_Pier14.pdf',
    location: 'Page 2, Section 3.2 (Shift B)',
    highlightedText: 'Poured 165 cum of M45 grade concrete at Pier 14 Lift 2 using 2 transit mixers and Putzmeister boom pump. Concrete slump verified at 140mm.',
    approvedBy: 'Er. V. K. Kulkarni (Chief Planner)',
    approvedAt: '2026-09-05 18:35:12 UTC'
  },
  {
    id: 'TRACE-2012',
    l6Code: '1.3.2.1.A',
    l6Name: 'Span 12-13 Precast Segment Stitch Concrete & Epoxy Jointing',
    approvedProgress: 40,
    sourceType: 'VOICE_MEMO',
    sourceFile: 'AUDIO_REC_ErRajesh_20260905_1645.wav',
    location: 'Timestamp 00:13 - 00:45',
    highlightedText: 'We completed epoxy gluing and stitch concreting for 3 precast segments on Span 12 to 13 today.',
    approvedBy: 'Er. V. K. Kulkarni (Chief Planner)',
    approvedAt: '2026-09-05 17:02:44 UTC'
  },
  {
    id: 'TRACE-3045',
    l6Code: '1.4.1.2.A',
    l6Name: 'BKC Underground Station Diaphragm Wall Panel Trenching (Panel D-22)',
    approvedProgress: 50,
    sourceType: 'EXCEL',
    sourceFile: 'Weekly_Site_Log_W36_Sheet1.xlsx',
    location: 'Sheet1, Row 42 (Cells B42:G42)',
    highlightedText: 'Excavated 120m3 of rock slurry for D-wall panel D22 at BKC underground station area using hydrofraise cutter.',
    approvedBy: 'Er. V. K. Kulkarni (Chief Planner)',
    approvedAt: '2026-09-05 19:10:00 UTC'
  }
];

export function TraceabilityViewer() {
  const [selectedLink, setSelectedLink] = useState(mockTraceabilityLinks[0]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left List of Approved Updates */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Approved Updates (Click to Trace)</h3>
        <div className="space-y-2">
          {mockTraceabilityLinks.map((item) => {
            const isSelected = selectedLink.id === item.id;
            return (
              <div
                key={item.id}
                onClick={() => setSelectedLink(item)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-cyan-950/80 border-cyan-500 text-cyan-200 shadow-md'
                    : 'bg-slate-900 border-slate-800 hover:bg-slate-800 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-mono font-bold text-amber-400">{item.l6Code}</span>
                  <span className="font-mono text-cyan-400 font-semibold">{item.approvedProgress}% Approved</span>
                </div>
                <p className="text-xs font-semibold text-slate-100 line-clamp-1">{item.l6Name}</p>
                <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                  <span className="truncate max-w-[140px] font-mono">{item.sourceFile}</span>
                  <span className="text-emerald-400 flex items-center gap-1 font-medium">
                    <CheckCircle2 className="w-3 h-3" /> Traced
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Traceability Source Document Inspector */}
      <div className="lg:col-span-2 space-y-4">
        <Card
          title={`Source Document Artifact Inspector`}
          subtitle={`Tracing L6 Activity ${selectedLink.l6Code} back to raw site evidence`}
          action={
            <Badge variant="cyan" icon={selectedLink.sourceType === 'DSR_PDF' ? FileText : selectedLink.sourceType === 'EXCEL' ? FileSpreadsheet : Mic}>
              {selectedLink.sourceType}
            </Badge>
          }
        >
          <div className="space-y-4 text-xs">
            {/* Header Details */}
            <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-slate-950 border border-slate-800">
              <div>
                <span className="text-slate-400 font-medium">Source Document Name:</span>
                <p className="font-mono text-cyan-300 font-semibold mt-0.5">{selectedLink.sourceFile}</p>
              </div>
              <div>
                <span className="text-slate-400 font-medium">Exact Evidence Coordinates:</span>
                <p className="font-mono text-amber-400 font-semibold mt-0.5">{selectedLink.location}</p>
              </div>
            </div>

            {/* Document Highlight Viewer Box */}
            <div className="space-y-2">
              <span className="text-slate-300 font-bold flex items-center gap-1.5">
                <FileSearch className="w-4 h-4 text-cyan-400" />
                Highlighted Source Document Passage:
              </span>
              <div className="p-4 rounded-xl bg-slate-950 border-2 border-cyan-500/40 text-slate-200 font-mono text-xs leading-relaxed shadow-inner">
                <p className="bg-cyan-950/80 text-cyan-200 p-2.5 rounded border border-cyan-700/60 font-medium">
                  "{selectedLink.highlightedText}"
                </p>
              </div>
            </div>

            {/* Audit Sign-off Details */}
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-slate-400">
              <span>Verified & Approved By: <strong className="text-slate-200">{selectedLink.approvedBy}</strong></span>
              <span>Timestamp: <strong className="text-mono text-slate-300">{selectedLink.approvedAt}</strong></span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
