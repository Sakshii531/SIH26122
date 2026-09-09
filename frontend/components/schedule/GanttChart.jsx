'use client';

import React, { useState } from 'react';
import { Calendar, Filter, ZoomIn, ZoomOut, Flag } from 'lucide-react';
import { MOCK_ALL_L6_ACTIVITIES } from '../../services/mock/mockSchedules.js';

const timelineDays = Array.from({ length: 30 }, (_, i) => i + 1);

export function GanttChart({ selectedActivity, onSelectActivity }) {
  const [showCriticalOnly, setShowCriticalOnly] = useState(false);

  const activities = showCriticalOnly
    ? MOCK_ALL_L6_ACTIVITIES.filter(a => a.isCriticalPath)
    : MOCK_ALL_L6_ACTIVITIES;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col h-[520px]">
      {/* Gantt Header Toolbar */}
      <div className="p-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-blue-600" />
            Primavera P6 Gantt Timeline
          </span>

          <label className="inline-flex items-center gap-2 cursor-pointer text-xs text-slate-700 font-medium">
            <input
              type="checkbox"
              checked={showCriticalOnly}
              onChange={(e) => setShowCriticalOnly(e.target.checked)}
              className="accent-rose-600 rounded"
            />
            <span>Highlight Critical Path</span>
          </label>
        </div>

        <div className="flex items-center gap-2">
          <button className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1">
            <ZoomIn className="w-3 h-3" />
            <span>Days</span>
          </button>
          <button className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1">
            <ZoomOut className="w-3 h-3" />
            <span>Weeks</span>
          </button>
        </div>
      </div>

      {/* Main Gantt Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Columns (Activity Names) */}
        <div className="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0">
          <div className="h-10 border-b border-slate-200 px-3 flex items-center text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-slate-50">
            Activity Code & Name
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {activities.map((act) => {
              const isSelected = selectedActivity?.id === act.id;
              return (
                <div
                  key={act.id}
                  onClick={() => onSelectActivity(act)}
                  className={`h-14 px-3 flex flex-col justify-center cursor-pointer transition-all ${
                    isSelected ? 'bg-blue-50 text-blue-900 font-semibold' : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-amber-700">{act.code}</span>
                    <span className="text-[10px] text-slate-500 font-mono font-bold">{act.actualProgressPercent}%</span>
                  </div>
                  <p className="text-xs font-semibold truncate text-slate-800">{act.name}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Timeline Grid */}
        <div className="flex-1 overflow-x-auto flex flex-col bg-slate-50/50">
          {/* Timeline Days Header */}
          <div className="h-10 border-b border-slate-200 flex bg-slate-50 min-w-[750px]">
            {timelineDays.map((d) => (
              <div
                key={d}
                className="w-8 h-full border-r border-slate-200 flex items-center justify-center text-[10px] font-mono font-bold text-slate-400"
              >
                {d}
              </div>
            ))}
          </div>

          {/* Timeline Activity Bars */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100 min-w-[750px]">
            {activities.map((act, idx) => {
              const startDay = Math.min(28, (idx * 4) + 1);
              const duration = 7;
              const actualWidth = (duration * (act.actualProgressPercent / 100)) * 32;

              return (
                <div key={act.id} className="h-14 relative flex items-center">
                  {/* Grid Lines */}
                  {timelineDays.map((d) => (
                    <div key={d} className="w-8 h-full border-r border-slate-100 shrink-0" />
                  ))}

                  {/* Planned Baseline Bar */}
                  <div
                    className="absolute h-3.5 rounded-full bg-slate-200 border border-slate-300 top-3"
                    style={{
                      left: `${startDay * 32}px`,
                      width: `${duration * 32}px`
                    }}
                  />

                  {/* Approved Actual Progress Bar */}
                  <div
                    className={`absolute h-3.5 rounded-full top-3 transition-all shadow-2xs ${
                      act.status === 'Completed'
                        ? 'bg-[#FA5A16]'
                        : act.status === 'Delayed'
                        ? 'bg-rose-600'
                        : 'bg-[#FA5A16]'
                    }`}
                    style={{
                      left: `${startDay * 32}px`,
                      width: `${actualWidth}px`
                    }}
                  />

                  {/* Milestone Marker */}
                  {act.isCriticalPath && (
                    <div
                      className="absolute top-2.5 text-rose-600"
                      style={{ left: `${(startDay + duration) * 32 - 12}px` }}
                      title="Critical Milestone Target"
                    >
                      <Flag className="w-4 h-4 fill-rose-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
