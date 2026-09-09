'use client';

import React from 'react';
import { SCurveChart } from '../../../components/analytics/SCurveChart.jsx';
import { DisciplineProgressChart } from '../../../components/analytics/DisciplineProgressChart.jsx';
import { DailyOutputChart } from '../../../components/analytics/DailyOutputChart.jsx';
import { LineChart, AlertTriangle, TrendingUp, ShieldCheck } from 'lucide-react';
import { MOCK_DELAY_HEATMAP } from '../../../services/mock/mockAuditLogs.js';
import { Card } from '../../../components/common/Card.jsx';
import { Badge } from '../../../components/common/Badge.jsx';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <LineChart className="w-6 h-6 text-cyan-400" />
            Planned vs Actual Progress Analytics & S-Curves
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time physical progress tracking, schedule variance, output rates and delay heatmaps
          </p>
        </div>
      </div>

      {/* S-Curve Chart */}
      <SCurveChart />

      {/* Grid Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DisciplineProgressChart />
        <DailyOutputChart />
      </div>

      {/* Active Delays & Heatmap */}
      <Card
        title="Schedule Delay Risk Heatmap & Root Cause Breakdown"
        subtitle="Activities with active negative variance against baseline schedule"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {MOCK_DELAY_HEATMAP.map((item, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border space-y-2 ${
                item.level === 'HIGH'
                  ? 'bg-rose-950/40 border-rose-800 text-rose-200'
                  : item.level === 'MEDIUM'
                  ? 'bg-amber-950/40 border-amber-800 text-amber-200'
                  : 'bg-slate-900 border-slate-800 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs">{item.zone}</span>
                <Badge variant={item.level === 'HIGH' ? 'rose' : 'amber'}>
                  {item.delayDays} Days Delay
                </Badge>
              </div>
              <p className="text-[11px] opacity-90 leading-snug">{item.reason}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
