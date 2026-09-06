'use client';

import React from 'react';
import { X, Layers, Calendar, CheckCircle2, Clock, FileText, ArrowUpRight } from 'lucide-react';
import { Badge } from '../common/Badge.jsx';
import { Button } from '../common/Button.jsx';

export function L5L6ActivityDetail({ activity, onClose }) {
  if (!activity) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
      {/* Title Header */}
      <div className="flex items-start justify-between pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              {activity.code}
            </span>
            <Badge variant={activity.discipline === 'Civil' ? 'cyan' : 'purple'}>
              {activity.discipline}
            </Badge>
          </div>
          <h2 className="text-base font-bold text-slate-900 mt-1">{activity.name}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{activity.wbsPath}</p>
        </div>

        {onClose && (
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-700 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Progress Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg bg-blue-50/60 border border-blue-100">
          <p className="text-[10px] font-bold text-blue-700 uppercase">Approved Actual Progress</p>
          <p className="text-xl font-bold text-blue-900 font-mono mt-1">{activity.actualProgressPercent}%</p>
          <div className="w-full bg-blue-200 rounded-full h-1.5 mt-2 overflow-hidden">
            <div className="bg-blue-600 h-full rounded-full" style={{ width: `${activity.actualProgressPercent}%` }} />
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
          <p className="text-[10px] font-bold text-slate-500 uppercase">Planned Baseline Progress</p>
          <p className="text-xl font-bold text-slate-700 font-mono mt-1">{activity.plannedProgressPercent}%</p>
          <div className="w-full bg-slate-200 rounded-full h-1.5 mt-2 overflow-hidden">
            <div className="bg-slate-500 h-full rounded-full" style={{ width: `${activity.plannedProgressPercent}%` }} />
          </div>
        </div>
      </div>

      {/* Dates Grid */}
      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
          <span className="text-slate-500 font-medium">Planned Start:</span>
          <span className="font-mono text-slate-800 font-bold">{activity.plannedStart}</span>
        </div>
        <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
          <span className="text-slate-500 font-medium">Planned Finish:</span>
          <span className="font-mono text-slate-800 font-bold">{activity.plannedFinish}</span>
        </div>
        <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
          <span className="text-slate-500 font-medium">Actual Start:</span>
          <span className="font-mono text-emerald-700 font-bold">{activity.actualStart || 'Not Started'}</span>
        </div>
        <div className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
          <span className="text-slate-500 font-medium">Target Volume:</span>
          <span className="font-mono text-slate-800 font-bold">{activity.baselineQuantity} {activity.unitOfMeasure}</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="pt-2 border-t border-slate-100 flex gap-2">
        <a
          href="/traceability"
          className="flex-1 py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
        >
          <FileText className="w-4 h-4 text-blue-600" />
          <span>View Source Document</span>
        </a>
        <a
          href="/verification"
          className="flex-1 py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-xs"
        >
          <span>Verify Update</span>
          <ArrowUpRight className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}
