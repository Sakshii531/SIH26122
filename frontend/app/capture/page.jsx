'use client';

import React, { useState } from 'react';
import { DropzoneUploader } from '../../components/capture/DropzoneUploader.jsx';
import { ExcelDataGrid } from '../../components/capture/ExcelDataGrid.jsx';
import { AudioWaveformPlayer } from '../../components/capture/AudioWaveformPlayer.jsx';
import { FileSpreadsheet, FileText, Mic, Sparkles } from 'lucide-react';

export default function CapturePage() {
  const [activeFormat, setActiveFormat] = useState('DSR'); // 'DSR' | 'EXCEL' | 'VOICE'

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileSpreadsheet className="w-6 h-6 text-cyan-400" />
            Multi-Format Data Capture & Ingestion Layer
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Ingest daily text site reports (PDF), Excel spreadsheets, or site engineer audio recordings
          </p>
        </div>

        {/* Format Selector Pills */}
        <div className="flex bg-slate-900 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setActiveFormat('DSR')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeFormat === 'DSR' ? 'bg-cyan-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Daily Site Report (PDF)</span>
          </button>
          <button
            onClick={() => setActiveFormat('EXCEL')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeFormat === 'EXCEL' ? 'bg-cyan-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Excel Spreadsheet</span>
          </button>
          <button
            onClick={() => setActiveFormat('VOICE')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeFormat === 'VOICE' ? 'bg-cyan-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Mic className="w-3.5 h-3.5" />
            <span>Voice Memo Audio</span>
          </button>
        </div>
      </div>

      {/* Main Drag & Drop Zone */}
      <DropzoneUploader />

      {/* Active Format Detail Views */}
      {activeFormat === 'EXCEL' ? (
        <ExcelDataGrid />
      ) : activeFormat === 'VOICE' ? (
        <AudioWaveformPlayer />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Daily Site Report (DSR) Live OCR & Text Parser Preview
            </h3>
            <span className="text-xs font-mono text-cyan-400">DSR_2026_09_05_Zone3_Pier14.pdf</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed space-y-2">
            <p className="text-slate-400">// Extracted Document Text Segment (Shift B Log):</p>
            <p className="p-3 bg-slate-900/60 rounded border border-slate-800 text-slate-200">
              "Poured 165 cum of M45 grade concrete at Pier 14 Lift 2 using 2 transit mixers and Putzmeister boom pump. Concrete slump verified at 140mm. Cubes casted for 7D and 28D compressive strength testing."
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
