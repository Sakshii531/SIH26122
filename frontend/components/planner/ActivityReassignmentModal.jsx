'use client';

import React, { useState } from 'react';
import { X, Search, Layers, CheckCircle2 } from 'lucide-react';
import { MOCK_ALL_L6_ACTIVITIES } from '../../services/mock/mockSchedules.js';

export function ActivityReassignmentModal({ onClose, onSelect }) {
  const [query, setQuery] = useState('');

  const filtered = MOCK_ALL_L6_ACTIVITIES.filter(
    a => a.name.toLowerCase().includes(query.toLowerCase()) || a.code.toLowerCase().includes(query.toLowerCase()) || a.wbsPath.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-slate-100 text-sm">Re-Assign to Primavera L6 Activity</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-3 border-b border-slate-800 bg-slate-950">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by activity code, title or WBS path..."
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Activity List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {filtered.map((act) => (
            <div
              key={act.id}
              onClick={() => onSelect({ l6ActivityId: act.id, l6ActivityCode: act.code, l6ActivityName: act.name, wbsPath: act.wbsPath })}
              className="p-3 rounded-xl bg-slate-800/60 hover:bg-cyan-950/60 border border-slate-700/60 hover:border-cyan-500/60 cursor-pointer transition-all flex items-center justify-between text-xs"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-amber-400">{act.code}</span>
                  <span className="font-semibold text-slate-200">{act.name}</span>
                </div>
                <p className="text-[10px] text-slate-400 mt-0.5">{act.wbsPath}</p>
              </div>

              <button className="px-2.5 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-[11px] shadow-xs">
                Select
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
