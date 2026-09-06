'use client';

import React from 'react';
import { FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card } from '../common/Card.jsx';

const mockExcelRows = [
  { row: 40, date: '2026-09-04', activity: 'Rebar placement Pier 14', qty: 28, unit: 'MT', status: 'Valid' },
  { row: 41, date: '2026-09-05', activity: 'Pier 14 M45 concrete pour lift 2', qty: 165, unit: 'm³', status: 'Valid' },
  { row: 42, date: '2026-09-05', activity: 'D-wall panel D22 trench excavation', qty: 120, unit: 'm³', status: 'Valid' },
  { row: 43, date: '2026-09-05', activity: 'Temporary power cable shifting', qty: 1, unit: 'Job', status: 'Warning - Unclear WBS' }
];

export function ExcelDataGrid() {
  return (
    <Card
      title="Excel Grid Ingest & Column Mapping Preview"
      subtitle="Sheet: Weekly_Site_Log_W36_Sheet1.xlsx (42 Rows Processed)"
      action={
        <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
          <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
          <span>Auto-Mapped 5 Columns</span>
        </div>
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono font-bold">
              <th className="p-2.5">Row</th>
              <th className="p-2.5">Date</th>
              <th className="p-2.5">Extracted Site Log Description</th>
              <th className="p-2.5 text-right">Quantity</th>
              <th className="p-2.5">Unit</th>
              <th className="p-2.5">Validation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono">
            {mockExcelRows.map((r) => (
              <tr key={r.row} className="hover:bg-slate-50 transition-all">
                <td className="p-2.5 text-slate-400 font-bold">{r.row}</td>
                <td className="p-2.5 text-slate-700">{r.date}</td>
                <td className="p-2.5 font-sans font-bold text-slate-900">{r.activity}</td>
                <td className="p-2.5 text-right font-bold text-blue-700">{r.qty}</td>
                <td className="p-2.5 text-slate-500">{r.unit}</td>
                <td className="p-2.5">
                  {r.status === 'Valid' ? (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3" /> Valid
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                      <AlertCircle className="w-3 h-3" /> WBS Alert
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
