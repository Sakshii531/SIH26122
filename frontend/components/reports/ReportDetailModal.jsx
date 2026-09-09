'use client';

import React from 'react';
import {
  X,
  FileText,
  Calendar,
  MapPin,
  Clock,
  HardHat,
  Truck,
  CloudSun,
  Paperclip,
  CheckCircle2,
  AlertCircle,
  Clock3,
  ExternalLink,
  ShieldCheck,
  Cpu,
  Eye,
  FileDown
} from 'lucide-react';

export function ReportDetailModal({ report, isOpen, onClose }) {
  if (!isOpen || !report) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-xs animate-fade-in">
      <div
        className="bg-white w-full max-w-3xl rounded-xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-8 bg-[#FA5A16] rounded-full" />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-black text-slate-900 font-mono-num tracking-tight">
                  {report.id}
                </h2>
                <span className="text-xs text-slate-400 font-medium">•</span>
                <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                  {report.reportType}
                </span>
                {report.status === 'Verified' && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    Verified
                  </span>
                )}
                {report.status === 'Under Review' && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    Under Review
                  </span>
                )}
                {report.status === 'Requires Attention' && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                    Requires Attention
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {report.activity} • <span className="font-mono text-slate-600">{report.wbs}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-all cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Progress & Quick Stats Banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">Reported Progress</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-black text-slate-900 font-mono-num">{report.progress}%</span>
                {report.progressDelta && (
                  <span className="text-xs font-bold text-emerald-600">{report.progressDelta}</span>
                )}
              </div>
              <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden mt-2">
                <div
                  className={`h-full ${report.progress === 100 ? 'bg-emerald-600' : 'bg-[#FA5A16]'}`}
                  style={{ width: `${report.progress}%` }}
                />
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">Date & Shift</span>
              <div className="mt-1">
                <p className="text-xs font-bold text-slate-800">{report.date}</p>
                <p className="text-[11px] text-slate-500 mt-0.5 truncate">{report.shift}</p>
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">Location & Sector</span>
              <div className="mt-1">
                <p className="text-xs font-bold text-slate-800 truncate">{report.location}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Sector 4 Zone</p>
              </div>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-400 block uppercase">Supervisor</span>
              <div className="mt-1">
                <p className="text-xs font-bold text-slate-800">{report.supervisor}</p>
                <p className="text-[11px] text-slate-500 mt-0.5">{report.crewSize} Crew Members</p>
              </div>
            </div>
          </div>

          {/* Site Conditions & Equipment */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50/60 border border-slate-200">
              <CloudSun className="w-4 h-4 text-amber-500 shrink-0" />
              <div>
                <span className="font-semibold text-slate-500 block text-[11px]">Site Weather</span>
                <span className="font-medium text-slate-800">{report.weather}</span>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50/60 border border-slate-200">
              <Truck className="w-4 h-4 text-[#FA5A16] shrink-0" />
              <div className="min-w-0">
                <span className="font-semibold text-slate-500 block text-[11px]">Active Plant & Equipment</span>
                <span className="font-medium text-slate-800 truncate block">{report.equipment}</span>
              </div>
            </div>
          </div>

          {/* Supervisor Summary */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#FA5A16]" />
              Field Surveillance Record & Notes
            </h3>
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed">
              {report.summary}
            </div>
          </div>

          {/* Primavera P6 Synchronisation Bridge */}
          {report.primaveraSync && (
            <div className="p-4 rounded-lg bg-orange-50/40 border border-orange-200/80 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-[#FA5A16]" />
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Primavera Schedule Sync & AI Match
                  </h4>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#FA5A16] text-white">
                  {report.primaveraSync.confidence}% Confidence
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-[11px] text-slate-500 block">Activity ID</span>
                  <span className="font-mono font-bold text-slate-800">{report.primaveraSync.activityId}</span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500 block">Planned Early Finish</span>
                  <span className="font-bold text-slate-800">{report.primaveraSync.plannedEarlyFinish}</span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500 block">Schedule Variance</span>
                  <span className="font-bold text-emerald-700">{report.primaveraSync.scheduleVariance}</span>
                </div>
              </div>
            </div>
          )}

          {/* Attached Evidence Files */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Paperclip className="w-4 h-4 text-slate-500" />
                Attached Evidence Files ({report.evidenceFiles?.length || 0})
              </h3>
              <span className="text-[11px] text-slate-400 font-medium">Read-Only Digital Ledger</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {report.evidenceFiles?.map((file, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-white border border-slate-200 hover:border-slate-300 transition-all flex items-center justify-between gap-3 text-xs"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-7 h-7 rounded bg-slate-100 flex items-center justify-center text-slate-500 shrink-0 font-bold text-[10px]">
                      {file.type === 'image' ? 'IMG' : file.type === 'audio' ? 'AUD' : 'DOC'}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-slate-800 truncate" title={file.name}>
                        {file.name}
                      </p>
                      <p className="text-[10px] text-slate-400 font-mono">
                        {file.size} • {file.time}
                      </p>
                    </div>
                  </div>
                  <button
                    className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-all cursor-pointer"
                    title="Preview file"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5 text-slate-500">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Cryptographically Verified Audit Signature</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-700 font-semibold hover:bg-slate-50 transition-all cursor-pointer"
            >
              Close
            </button>
            <a
              href="/traceability"
              className="px-4 py-1.5 rounded-lg bg-[#FA5A16] hover:bg-[#E44E0E] text-white font-semibold transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
            >
              <span>Audit Traceability</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
