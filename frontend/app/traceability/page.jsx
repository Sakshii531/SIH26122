'use client';

import React from 'react';
import { TraceabilityViewer } from '../../components/audit/TraceabilityViewer.jsx';
import { FileSearch } from 'lucide-react';

export default function TraceabilityPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileSearch className="w-6 h-6 text-cyan-400" />
            Source-Document Traceability Matrix
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Trace approved Primavera P6 / MS Project updates back to raw PDF line items, Excel cells, or Audio timestamps
          </p>
        </div>
      </div>

      <TraceabilityViewer />
    </div>
  );
}
