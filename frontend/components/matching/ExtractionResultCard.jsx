'use client';

import React from 'react';
import { Cpu, FileText, Calendar, Truck, Users, Hash, Edit3 } from 'lucide-react';
import { Badge } from '../common/Badge.jsx';

export function ExtractionResultCard({ event, onEdit }) {
  if (!event) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-100">AI Entity Extraction Result</h3>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="cyan" icon={FileText}>
            {event.sourceFileName}
          </Badge>
          {onEdit && (
            <button
              onClick={onEdit}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-all text-xs flex items-center gap-1"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Entities</span>
            </button>
          )}
        </div>
      </div>

      {/* Raw Source Snippet */}
      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
        <span className="text-[10px] font-semibold text-slate-400 uppercase">Raw Source Log ({event.sourceRefLocation}):</span>
        <p className="text-slate-200 mt-1 italic">"{event.rawText}"</p>
      </div>

      {/* Structured Entity Grid */}
      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="p-2.5 rounded bg-slate-800/40 border border-slate-800">
          <span className="text-slate-400 font-medium">Extracted Activity:</span>
          <p className="font-semibold text-cyan-300 mt-0.5">{event.extractedActivity}</p>
        </div>

        <div className="p-2.5 rounded bg-slate-800/40 border border-slate-800">
          <span className="text-slate-400 font-medium">Quantity & Unit:</span>
          <p className="font-bold text-amber-400 font-mono mt-0.5">
            {event.quantity || 'N/A'} {event.unit || ''}
          </p>
        </div>

        <div className="p-2.5 rounded bg-slate-800/40 border border-slate-800">
          <span className="text-slate-400 font-medium flex items-center gap-1">
            <Truck className="w-3.5 h-3.5 text-cyan-400" /> Equipment Mentioned:
          </span>
          <p className="text-slate-300 mt-0.5 truncate">
            {event.equipmentUsed?.join(', ') || 'None listed'}
          </p>
        </div>

        <div className="p-2.5 rounded bg-slate-800/40 border border-slate-800">
          <span className="text-slate-400 font-medium flex items-center gap-1">
            <Users className="w-3.5 h-3.5 text-emerald-400" /> Workforce Count:
          </span>
          <p className="font-mono text-slate-200 mt-0.5">{event.workforceCount ? `${event.workforceCount} workers` : 'Not specified'}</p>
        </div>
      </div>
    </div>
  );
}
