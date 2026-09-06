'use client';

import React from 'react';
import { AuditTimeline } from '../../components/audit/AuditTimeline.jsx';
import { History, Search, Download } from 'lucide-react';
import { Card } from '../../components/common/Card.jsx';

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <History className="w-6 h-6 text-cyan-400" />
            Immutable Audit Trail & Historical Execution Archive
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Complete timestamped audit logs of all AI extractions, semantic matches, planner verifications, and DB commits
          </p>
        </div>

        <button className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1.5 border border-slate-700">
          <Download className="w-4 h-4" />
          <span>Export Audit Log CSV</span>
        </button>
      </div>

      <Card title="Chronological Audit Timeline">
        <AuditTimeline />
      </Card>
    </div>
  );
}
