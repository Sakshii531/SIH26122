'use client';

import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { MOCK_S_CURVE_DATA } from '../../services/mock/mockAuditLogs.js';
import { Card } from '../common/Card.jsx';

export function SCurveChart() {
  return (
    <Card
      title="Cumulative Progress S-Curve (Baseline Plan vs Approved Actual)"
      subtitle="Metro Viaduct Package 4 Progress Baseline (SPI: 0.89)"
    >
      <div className="h-80 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={MOCK_S_CURVE_DATA} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="plannedGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#475569" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#475569" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="month" stroke="#64748B" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748B" tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
            <Tooltip
              contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />

            <Area
              type="monotone"
              dataKey="planned"
              name="Cumulative Planned Baseline %"
              stroke="#64748B"
              strokeWidth={2}
              strokeDasharray="4 4"
              fillOpacity={1}
              fill="url(#plannedGradient)"
            />
            <Area
              type="monotone"
              dataKey="actual"
              name="Approved Actual Physical %"
              stroke="#06B6D4"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#actualGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
