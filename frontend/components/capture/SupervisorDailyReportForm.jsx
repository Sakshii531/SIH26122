'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  FileText,
  UploadCloud,
  Mic,
  File,
  CheckCircle2,
  Trash2,
  Play,
  Pause,
  RotateCcw,
  Square,
  Sparkles,
  Paperclip,
  Send,
  AlertCircle,
  Clock,
  HardHat,
  ChevronRight,
  Info
} from 'lucide-react';
import { captureService } from '../../services/captureService.js';
import { MOCK_FIELD_REPORTS } from '../../services/mock/mockFieldReports.js';

export function SupervisorDailyReportForm() {
  const router = useRouter();

  // ── 1. Text Report State ──
  const [textReport, setTextReport] = useState(
    'Poured 165 cum of M45 grade concrete at Pier 14 Lift 2 using 2 transit mixers and Putzmeister boom pump. Concrete slump verified at 140mm. 18 rebar fitters and 4 helpers on site. Weather clear and dry. Sub-base geotechnical soil inspection cleared by third-party engineer.'
  );
  const maxChars = 2000;

  // ── 2. Document Report State ──
  const [uploadedDocument, setUploadedDocument] = useState({
    name: 'DSR_Supervisor_MarcusVance_08Sep.pdf',
    size: '890 KB',
    type: 'PDF',
    uploadedAt: 'Today, 16:00 PM'
  });
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // ── 3. Voice Report State ──
  // 'idle' | 'recording' | 'recorded'
  const [voiceState, setVoiceState] = useState('recorded');
  const [isVoicePlaying, setIsVoicePlaying] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const recordingTimerRef = useRef(null);

  // ── 4. Form Submission State ──
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Recording timer tick
  useEffect(() => {
    if (voiceState === 'recording') {
      recordingTimerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
    }
    return () => {
      if (recordingTimerRef.current) clearInterval(recordingTimerRef.current);
    };
  }, [voiceState]);

  // Voice player simulated timer
  useEffect(() => {
    let playTimer;
    if (isVoicePlaying) {
      playTimer = setTimeout(() => {
        setIsVoicePlaying(false);
      }, 5000);
    }
    return () => clearTimeout(playTimer);
  }, [isVoicePlaying]);

  // Handle Drag & Drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      processSelectedFile(file);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const processSelectedFile = (file) => {
    const sizeInKB = Math.round(file.size / 1024);
    const sizeStr = sizeInKB > 1024 ? `${(sizeInKB / 1024).toFixed(1)} MB` : `${sizeInKB} KB`;
    const ext = file.name.split('.').pop()?.toUpperCase() || 'DOC';
    setUploadedDocument({
      name: file.name,
      size: sizeStr,
      type: ext,
      uploadedAt: 'Just now'
    });
  };

  const handleRemoveDocument = () => {
    setUploadedDocument(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Voice controls
  const handleStartRecording = () => {
    setRecordingSeconds(0);
    setVoiceState('recording');
  };

  const handleStopRecording = () => {
    setVoiceState('recorded');
    setIsVoicePlaying(false);
  };

  const handleReRecord = () => {
    setIsVoicePlaying(false);
    setRecordingSeconds(0);
    setVoiceState('recording');
  };

  const handleRemoveVoice = () => {
    setIsVoicePlaying(false);
    setVoiceState('idle');
    setRecordingSeconds(0);
  };

  const formatSeconds = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  // Handle Submit Report
  const handleSubmitReport = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate upload delay via captureService
    if (uploadedDocument) {
      await captureService.uploadDSR({ name: uploadedDocument.name });
    } else {
      await new Promise((r) => setTimeout(r, 600));
    }

    // Add new report to mock ledger
    const nextIdNum = String(MOCK_FIELD_REPORTS.length + 249).padStart(4, '0');
    const newReport = {
      id: `RPT-${nextIdNum}`,
      idPrefix: 'RPT-',
      idNum: nextIdNum,
      date: '08 Sep 2026',
      rawDate: '2026-09-08',
      activity: 'Pier 14 Concrete Lift 2 & Structural Pour',
      wbs: 'WBS: L5.03.04',
      wbsCode: 'L5.03.04',
      location: 'Pier 14 West',
      reportType: 'Daily Report',
      progress: 75,
      progressDelta: '+12% today',
      isComplete: false,
      status: 'Verified',
      statusTone: 'verified',
      evidenceCount: (uploadedDocument ? 1 : 0) + (voiceState === 'recorded' ? 1 : 0) + 1,
      isCurrentActive: true,
      supervisor: 'Marcus Vance (SV-8842)',
      shift: 'Day Shift (07:00 - 16:30)',
      crewSize: 22,
      weather: '32°C Clear Skies',
      equipment: 'Putzmeister Boom Pump (1x), Transit Mixers (2x)',
      summary: textReport || 'Daily progress logged by site supervisor.',
      evidenceFiles: [
        ...(uploadedDocument
          ? [{ name: uploadedDocument.name, type: 'document', size: uploadedDocument.size, time: '16:00 PM' }]
          : []),
        ...(voiceState === 'recorded'
          ? [{ name: 'AUDIO_REC_MarcusVance_08Sep.wav', type: 'audio', size: '1.8 MB', time: '16:20 PM' }]
          : []),
        { name: 'Site_Inspection_Pier14_Photo.jpg', type: 'image', size: '2.4 MB', time: '15:10 PM' }
      ],
      primaveraSync: {
        activityId: 'ACT-P14-LFT-02',
        baselineCode: 'BL-2026-08',
        lastUpdatedBy: 'Marcus Vance (Supervisor)',
        status: 'Synchronized'
      }
    };

    MOCK_FIELD_REPORTS.unshift(newReport);

    setIsSubmitting(false);
    setSubmitSuccess(true);

    setTimeout(() => {
      router.push('/');
    }, 1000);
  };

  return (
    <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fade-in pb-24">
      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-[#FA5A16]/10 text-[#FA5A16] border border-[#FA5A16]/20 font-mono">
              SUPERVISOR DISPATCH
            </span>
            <span className="text-xs text-slate-400 font-mono">Sector 4 · Field Unit</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Submit Daily Report
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Complete the single-entry field report below. All three sections submit together into the NIYOGEN ledger.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-bold text-slate-700 shadow-3xs flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-[#FA5A16]" />
            <span>08 Sep 2026</span>
          </div>
        </div>
      </div>

      {/* Submission Success Toast Banner */}
      {submitSuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border-2 border-emerald-500 text-emerald-900 flex items-center justify-between shadow-md animate-fade-in">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
            <div>
              <p className="text-sm font-bold">Daily Report Successfully Logged!</p>
              <p className="text-xs text-emerald-700">Committed to Field Operations Ledger. Redirecting to Reports...</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-800 bg-emerald-100 px-2 py-1 rounded">
            SYNCED
          </span>
        </div>
      )}

      <form onSubmit={handleSubmitReport} className="space-y-6">
        {/* ========================================================================= */}
        {/* 1. TEXT REPORT SECTION                                                    */}
        {/* ========================================================================= */}
        <section className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden transition-all hover:border-slate-300">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#FA5A16]/10 text-[#FA5A16] flex items-center justify-center shrink-0 font-bold">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-black text-slate-900 tracking-tight">1. Text Report</h2>
                <p className="text-xs text-slate-500 font-medium">
                  Direct field notes, work quantities, and physical site condition observations
                </p>
              </div>
            </div>

            <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider bg-white px-2.5 py-1 rounded-md border border-slate-200">
              Required
            </span>
          </div>

          <div className="p-5 space-y-3">
            <div>
              <label
                htmlFor="field-report-desc"
                className="block text-xs font-bold text-slate-700 mb-1"
              >
                Field-Report Description
              </label>
              <p className="text-[11px] text-slate-500 mb-2 leading-relaxed">
                Describe activities executed, concrete volumes or steel quantities placed, plant machines deployed, active crew sizes, and any site constraints.
              </p>
              <textarea
                id="field-report-desc"
                rows={6}
                value={textReport}
                onChange={(e) => setTextReport(e.target.value)}
                maxLength={maxChars}
                placeholder="Enter field report description here (e.g. Concrete poured at Pier 14 Lift 2, slump 140mm, 18 rebar fitters on site, zero incidents...)"
                className="w-full p-3.5 text-xs sm:text-sm bg-slate-50/70 hover:bg-slate-50 focus:bg-white border border-slate-200 focus:border-[#FA5A16] focus:ring-1 focus:ring-[#FA5A16]/30 rounded-xl text-slate-900 placeholder-slate-400 outline-none transition-all leading-relaxed font-sans resize-y"
              />
            </div>

            {/* Character Counter & Quick Helper */}
            <div className="flex items-center justify-between text-xs pt-1">
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Info className="w-3 h-3" /> Auto-parsed by NIYOGEN AI Activity Matcher
                </span>
              </div>
              <div className="font-mono text-xs font-bold">
                <span className={textReport.length > maxChars * 0.9 ? 'text-rose-600' : 'text-slate-500'}>
                  {textReport.length}
                </span>
                <span className="text-slate-400 font-normal"> / {maxChars} characters</span>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================================= */}
        {/* 2. DOCUMENT REPORT SECTION                                                */}
        {/* ========================================================================= */}
        <section className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden transition-all hover:border-slate-300">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 font-bold">
                <UploadCloud className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-black text-slate-900 tracking-tight">2. Document Report</h2>
                <p className="text-xs text-slate-500 font-medium">
                  Attach scanned Daily Site Report (DSR), subcontractor logs, or inspection certificates
                </p>
              </div>
            </div>

            <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider bg-white px-2.5 py-1 rounded-md border border-slate-200">
              PDF / DOC / DOCX
            </span>
          </div>

          <div className="p-5 space-y-4">
            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              accept=".pdf,.doc,.docx"
              className="hidden"
            />

            {/* Drag & Drop Area */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className={`border-2 border-dashed rounded-xl p-6 sm:p-8 text-center transition-all cursor-pointer select-none ${
                isDragging
                  ? 'border-[#FA5A16] bg-orange-50/40 scale-[0.99]'
                  : 'border-slate-300 hover:border-[#FA5A16] bg-slate-50/50 hover:bg-orange-50/20'
              }`}
            >
              <div className="w-12 h-12 rounded-xl bg-orange-100/70 text-[#FA5A16] flex items-center justify-center mx-auto mb-3 shadow-3xs">
                <UploadCloud className="w-6 h-6" />
              </div>
              <p className="text-xs sm:text-sm font-bold text-slate-800">
                Drag and drop your document here, or{' '}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current && fileInputRef.current.click();
                  }}
                  className="text-[#FA5A16] hover:underline font-extrabold cursor-pointer"
                >
                  Browse Files
                </button>
              </p>
              <p className="text-[11px] text-slate-500 mt-1 font-medium">
                Supports PDF, DOC, DOCX up to 25 MB
              </p>
            </div>

            {/* Uploaded Document Card */}
            {uploadedDocument ? (
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between gap-3 transition-all animate-fade-in">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-lg bg-orange-500 text-white flex flex-col items-center justify-center font-bold font-mono shrink-0 shadow-2xs">
                    <File className="w-4 h-4" />
                    <span className="text-[8px] uppercase">{uploadedDocument.type}</span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-900 truncate">
                      {uploadedDocument.name}
                    </p>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500 mt-0.5">
                      <span className="font-mono">{uploadedDocument.size}</span>
                      <span>•</span>
                      <span>{uploadedDocument.uploadedAt}</span>
                      <span>•</span>
                      <span className="inline-flex items-center gap-1 text-emerald-600 font-semibold text-[10px]">
                        <CheckCircle2 className="w-3 h-3" /> Ready
                      </span>
                    </div>
                  </div>
                </div>

                {/* Remove Document Button */}
                <button
                  type="button"
                  onClick={handleRemoveDocument}
                  title="Remove uploaded document"
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors shrink-0 cursor-pointer"
                  aria-label="Remove document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-500">
                <span>No document attached yet.</span>
                <button
                  type="button"
                  onClick={() =>
                    setUploadedDocument({
                      name: 'DSR_Supervisor_MarcusVance_08Sep.pdf',
                      size: '890 KB',
                      type: 'PDF',
                      uploadedAt: 'Today, 16:00 PM'
                    })
                  }
                  className="text-xs font-bold text-[#FA5A16] hover:underline cursor-pointer"
                >
                  Attach Sample DSR PDF
                </button>
              </div>
            )}
          </div>
        </section>

        {/* ========================================================================= */}
        {/* 3. VOICE REPORT SECTION                                                   */}
        {/* ========================================================================= */}
        <section className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden transition-all hover:border-slate-300">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0 font-bold">
                <Mic className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-black text-slate-900 tracking-tight">3. Voice Report</h2>
                <p className="text-xs text-slate-500 font-medium">
                  Record audio voice debrief with automated AI transcription and key term extraction
                </p>
              </div>
            </div>

            <span className="text-[10px] font-mono font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-md uppercase tracking-wider">
              ASR Transcription
            </span>
          </div>

          <div className="p-5 space-y-4">
            {/* Case A: IDLE State — Ready to record */}
            {voiceState === 'idle' && (
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-3">
                <p className="text-xs text-slate-600 font-medium max-w-md mx-auto">
                  Record a quick voice briefing directly from site. The AI engine extracts activity codes, concrete volumes, and contractor updates automatically.
                </p>

                <div className="flex flex-wrap items-center justify-center gap-3 pt-1">
                  <button
                    type="button"
                    onClick={handleStartRecording}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#FA5A16] hover:bg-[#e04e10] text-white font-bold text-xs shadow-sm hover:shadow transition-all cursor-pointer"
                  >
                    <Mic className="w-4 h-4" />
                    <span>Start Recording</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setVoiceState('recorded')}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-all cursor-pointer"
                  >
                    <span>Use Sample Voice Debrief</span>
                  </button>
                </div>
              </div>
            )}

            {/* Case B: RECORDING IN PROGRESS State */}
            {voiceState === 'recording' && (
              <div className="p-5 rounded-xl bg-[#18181B] text-white space-y-4 border border-slate-700 shadow-md animate-fade-in">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
                    </span>
                    <span className="text-xs font-bold text-rose-400 uppercase tracking-wider font-mono">
                      Recording in progress...
                    </span>
                  </div>

                  <div className="font-mono text-sm font-bold text-white bg-slate-800 px-3 py-1 rounded-md">
                    {formatSeconds(recordingSeconds)}
                  </div>
                </div>

                {/* Animated Waveform Visualizer */}
                <div className="flex items-center gap-1.5 h-12 px-2 bg-slate-900 rounded-lg overflow-hidden">
                  {Array.from({ length: 36 }).map((_, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-gradient-to-t from-[#FA5A16] to-amber-400 rounded-full animate-pulse"
                      style={{
                        height: `${Math.max(20, ((i * 7) % 85) + 15)}%`,
                        animationDuration: `${0.4 + (i % 5) * 0.15}s`
                      }}
                    />
                  ))}
                </div>

                {/* Stop Recording Control */}
                <div className="flex justify-center pt-1">
                  <button
                    type="button"
                    onClick={handleStopRecording}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md transition-all cursor-pointer"
                  >
                    <Square className="w-4 h-4 fill-current" />
                    <span>Stop Recording</span>
                  </button>
                </div>
              </div>
            )}

            {/* Case C: RECORDED State with Play, Re-record, Remove Controls */}
            {voiceState === 'recorded' && (
              <div className="space-y-3">
                {/* Audio Waveform Player Bar */}
                <div className="p-4 rounded-xl bg-[#18181B] text-white flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 shadow-md">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {/* Play / Pause Button */}
                    <button
                      type="button"
                      onClick={() => setIsVoicePlaying(!isVoicePlaying)}
                      className="w-10 h-10 rounded-full bg-[#FA5A16] hover:bg-[#e04e10] text-white flex items-center justify-center transition-all shadow-sm shrink-0 cursor-pointer"
                      aria-label={isVoicePlaying ? 'Pause audio' : 'Play audio'}
                    >
                      {isVoicePlaying ? (
                        <Pause className="w-4 h-4 fill-current" />
                      ) : (
                        <Play className="w-4 h-4 fill-current ml-0.5" />
                      )}
                    </button>

                    {/* Waveform Bars */}
                    <div className="flex-1 flex items-center gap-1 h-8 overflow-hidden">
                      {Array.from({ length: 32 }).map((_, i) => {
                        const heightPct = Math.max(25, Math.sin(i * 0.5) * 75 + 20);
                        const isActive = isVoicePlaying ? i <= 20 : i <= 14;
                        return (
                          <div
                            key={i}
                            className={`flex-1 rounded-full transition-all ${
                              isActive ? 'bg-[#FA5A16]' : 'bg-slate-700'
                            }`}
                            style={{ height: `${heightPct}%` }}
                          />
                        );
                      })}
                    </div>

                    <div className="text-right font-mono text-xs text-slate-300 shrink-0">
                      <span className="text-[#FA5A16] font-bold">
                        {isVoicePlaying ? '00:18' : '00:45'}
                      </span>{' '}
                      / 01:05
                    </div>
                  </div>

                  {/* Play, Re-record, Remove Action Controls */}
                  <div className="flex items-center gap-2 border-t sm:border-t-0 sm:border-l border-slate-700 pt-3 sm:pt-0 sm:pl-3 justify-end shrink-0">
                    <button
                      type="button"
                      onClick={handleReRecord}
                      title="Re-record voice memo"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Re-record</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleRemoveVoice}
                      title="Remove voice memo"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors cursor-pointer"
                      aria-label="Remove recording"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Transcribed Speech Snippet */}
                <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200/70 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-amber-950 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                      Speech-to-Text Live Transcript (Supervisor Er. Rajesh / Marcus)
                    </span>
                    <span className="text-[10px] font-mono font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded">
                      Confidence: 96%
                    </span>
                  </div>
                  <p className="text-slate-700 italic font-medium leading-relaxed">
                    "Poured 165 cum of M45 grade concrete at Pier 14 Lift 2 using 2 transit mixers and Putzmeister boom pump. Concrete slump verified at 140mm. Cubes casted for 7D and 28D compressive strength testing."
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ========================================================================= */}
        {/* 4. BOTTOM ACTION BAR WITH BOTTOM-RIGHT "SUBMIT REPORT" BUTTON            */}
        {/* ========================================================================= */}
        <div className="p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Left summary indicators */}
          <div className="flex items-center flex-wrap gap-4 text-xs text-slate-600">
            <span className="font-bold text-slate-900">Summary:</span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <CheckCircle2 className={`w-4 h-4 ${textReport.length > 0 ? 'text-emerald-600' : 'text-slate-300'}`} />
              Text Notes ({textReport.length} chars)
            </span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <CheckCircle2 className={`w-4 h-4 ${uploadedDocument ? 'text-emerald-600' : 'text-slate-300'}`} />
              Document ({uploadedDocument ? '1 file' : 'None'})
            </span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <CheckCircle2 className={`w-4 h-4 ${voiceState === 'recorded' ? 'text-emerald-600' : 'text-slate-300'}`} />
              Voice Memo ({voiceState === 'recorded' ? 'Recorded' : 'None'})
            </span>
          </div>

          {/* Right Action Button */}
          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <button
              type="button"
              onClick={() => {
                setTextReport('');
                setUploadedDocument(null);
                setVoiceState('idle');
              }}
              className="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-xs font-bold text-slate-600 transition-colors cursor-pointer"
            >
              Clear Form
            </button>

            <button
              type="submit"
              disabled={isSubmitting || textReport.trim().length === 0}
              className={`px-7 py-3 rounded-xl font-bold text-xs sm:text-sm text-white shadow-md flex items-center gap-2 transition-all cursor-pointer ${
                isSubmitting || textReport.trim().length === 0
                  ? 'bg-slate-300 cursor-not-allowed text-slate-500'
                  : 'bg-[#FA5A16] hover:bg-[#e04e10] hover:shadow-lg active:scale-95'
              }`}
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Submitting to Ledger...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Report</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
