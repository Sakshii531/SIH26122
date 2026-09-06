'use client';

import React from 'react';
import { History, Cpu, CheckCircle2, Edit3, XCircle, Database, FileText } from 'lucide-react';
import { MOCK_AUDIT_LOGS } from '../../services/mock/mockAuditLogs.js';
import { Badge } from '../common/Badge.jsx';

const actionIcons = {
  AI_EXTRACTED: Cpu,
  SEMANTIC_MATCHED: Cpu,
  PLANNER_APPROVED: CheckCircle2,
  PLANNER_OVERRIDDEN: Edit3,
  REJECTED: XCircle,
  DB_COMMITTED: Database
};

const actionBadges = {
  AI_EXTRACTED: 'cyan',
  SEMANTIC_MATCHED: 'purple',
  PLANNER_APPROVED: 'green',
  PLANNER_OVERRIDDEN: 'amber',
  REJECTED: 'rose',
  DB_COMMITTED: 'blue'
};

export function AuditTimeline({ logs = MOCK_AUDIT_LOGS }) {
  return (
    <div className="space-y-4">
      <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
        {logs.map((log) => {
          const Icon = actionIcons[log.action] || History;
          const badgeVariant = actionBadges[log.action] || 'default';

          return (
            <div key={log.id} className="relative pl-6">
              {/* Timeline Icon Bullet */}
              <div className="absolute -left-3 top-0.5 w-6 h-6 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center text-cyan-400 shadow-md">
                <Icon className="w-3.5 h-3.5" />
              </div>

              {/* Log Entry Card */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 shadow-md space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-amber-400">{log.activityCode}</span>
                    <span className="font-semibold text-slate-100">{log.activityName}</span>
                  </div>
                  <Badge variant={badgeVariant}>{log.action}</Badge>
                </div>

                <p className="text-slate-300 leading-relaxed">{log.details}</p>

                <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 font-mono">
                  <span>Actor: <strong className="text-cyan-400">{log.actor}</strong></span>
                  <span>Source: {log.sourceDocument} ({log.sourceRefLocation})</span>
                  <span>{new Date(log.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
