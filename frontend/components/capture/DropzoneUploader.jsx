'use client';

import React, { useState } from 'react';
import { UploadCloud, FileText, FileSpreadsheet, Mic, CheckCircle2, RefreshCw } from 'lucide-react';
import { captureService } from '../../services/captureService.js';

export function DropzoneUploader({ onUploadComplete }) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  const handleSimulatedUpload = async (type) => {
    setIsUploading(true);
    setUploadSuccess(null);

    let result;
    if (type === 'DSR') {
      result = await captureService.uploadDSR({ name: 'DSR_2026_09_05_Zone3_Pier14.pdf' });
    } else if (type === 'EXCEL') {
      result = await captureService.uploadExcel({ name: 'Weekly_Site_Log_W36_Sheet1.xlsx' });
    } else {
      result = await captureService.uploadVoice({ name: 'AUDIO_REC_ErRajesh_20260905_1645.wav' });
    }

    setIsUploading(false);
    setUploadSuccess({ type, result });
    if (onUploadComplete) {
      onUploadComplete(result);
    }
  };

  return (
    <div className="bg-white border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-8 text-center transition-all shadow-xs">
      {isUploading ? (
        <div className="py-8 space-y-3">
          <RefreshCw className="w-10 h-10 text-blue-600 animate-spin mx-auto" />
          <h3 className="text-sm font-bold text-slate-900">Parsing Site Artifact & Running AI NLP Extraction...</h3>
          <p className="text-xs text-slate-500">Scanning activity descriptions, quantities, dates & equipment notes</p>
        </div>
      ) : uploadSuccess ? (
        <div className="py-6 space-y-3">
          <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">Daily Log Ingested & Extracted Successfully!</h3>
          <p className="text-xs text-slate-600">File: <span className="font-mono text-blue-600 font-bold">{uploadSuccess.result.fileName}</span></p>
          <div className="pt-2 flex justify-center gap-3">
            <button
              onClick={() => setUploadSuccess(null)}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs text-slate-700 font-semibold cursor-pointer"
            >
              Upload Another File
            </button>
            <a
              href="/matching"
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-xs"
            >
              Inspect AI Semantic Matches →
            </a>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 mx-auto">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div>
            <h3 className="text-base font-bold text-slate-900">Upload Daily Site Evidence Artifact</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-lg mx-auto">
              Drag & drop Daily Site Reports (PDF), Excel Spreadsheets (.xlsx), or Site Engineer Voice Memos (.wav/.mp3)
            </p>
          </div>

          {/* Quick Demo Triggers */}
          <div className="pt-2 flex flex-wrap justify-center gap-3">
            <button
              onClick={() => handleSimulatedUpload('DSR')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-xs text-slate-800 font-bold transition-all cursor-pointer shadow-2xs hover:scale-105"
            >
              <FileText className="w-4 h-4 text-blue-600" />
              <span>Simulate DSR PDF Upload</span>
            </button>

            <button
              onClick={() => handleSimulatedUpload('EXCEL')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 text-xs text-slate-800 font-bold transition-all cursor-pointer shadow-2xs hover:scale-105"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
              <span>Simulate Excel Upload</span>
            </button>

            <button
              onClick={() => handleSimulatedUpload('VOICE')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-50 hover:bg-amber-50 border border-slate-200 hover:border-amber-300 text-xs text-slate-800 font-bold transition-all cursor-pointer shadow-2xs hover:scale-105"
            >
              <Mic className="w-4 h-4 text-amber-600" />
              <span>Simulate Voice Recording</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
