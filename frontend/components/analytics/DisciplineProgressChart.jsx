'use client';

import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { MOCK_DISCIPLINE_PROGRESS } from '../../services/mock/mockAuditLogs.js';
import { Card } from '../common/Card.jsx';

export function DisciplineProgressChart() {
  return (
    <Card
      title="Engineering Discipline Progress Breakdown"
      subtitle="Planned vs Actual Physical Completion % across Disciplines"
    >
      <div className="h-64 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={MOCK_DISCIPLINE_PROGRESS} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis dataKey="discipline" stroke="#64748B" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748B" tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
            <Tooltip
              contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />

            <Bar dataKey="planned" name="Planned %" fill="#475569" radius={[4, 4, 0, 0]} />
            <Bar dataKey="actual" name="Actual %" fill="#10B981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
