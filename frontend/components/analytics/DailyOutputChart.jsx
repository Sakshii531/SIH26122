'use client';

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { MOCK_DAILY_OUTPUT_TRENDS } from '../../services/mock/mockAuditLogs.js';
import { Card } from '../common/Card.jsx';

export function DailyOutputChart() {
  return (
    <Card
      title="Daily Field Output Trends (Concrete m³, Rebar MT, Excavation m³)"
      subtitle="Last 7 Days Production Trends Extracted from Site Log Inputs"
    >
      <div className="h-64 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={MOCK_DAILY_OUTPUT_TRENDS} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="date" stroke="#64748B" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748B" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />

            <Line type="monotone" dataKey="concrete" name="Concrete (m³)" stroke="#06B6D4" strokeWidth={2.5} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="rebar" name="Rebar Tying (MT)" stroke="#F59E0B" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="excavation" name="Excavation (m³)" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
