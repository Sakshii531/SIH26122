'use client';

import React from 'react';
import Link from 'next/link';
import {
  LayoutDashboard,
  TrendingUp,
  AlertTriangle,
  CheckSquare,
  FileSpreadsheet,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Building2,
  HardHat,
  Calendar,
  Layers,
  CheckCircle2,
  Clock,
  Activity,
  Zap,
  BarChart3
} from 'lucide-react';
import { Card } from '../components/common/Card.jsx';
import { Badge } from '../components/common/Badge.jsx';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge.jsx';
import { SCurveChart } from '../components/analytics/SCurveChart.jsx';
import { MOCK_PROJECTS, MOCK_PROJECT_STATS } from '../services/mock/mockProjects.js';
import { MOCK_EXTRACTIONS_AND_MATCHES } from '../services/mock/mockExtractions.js';
import { MOCK_AUDIT_LOGS } from '../services/mock/mockAuditLogs.js';

export default function DashboardOverview() {
  const activeProject = MOCK_PROJECTS[0];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Executive Hero Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30 uppercase tracking-wider">
                SIH26122 Planning-to-Execution Bridge
              </span>
              <span className="text-xs text-slate-300">| Project Code: {activeProject.code}</span>
            </div>
            <h1 className="text-2xl font-black text-white tracking-tight">
              {activeProject.name}
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Owner/Client: <strong className="text-white">{activeProject.client}</strong> | Contractor: <strong className="text-white">{activeProject.contractor}</strong>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/capture"
              className="px-4 py-2.5 rounded-xl bg-blue-500 hover:bg-blue-400 text-white font-bold text-xs shadow-lg flex items-center gap-2 transition-all cursor-pointer"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Ingest Daily Site Log</span>
            </Link>
            <Link
              href="/verification"
              className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/20 flex items-center gap-2 transition-all cursor-pointer"
            >
              <CheckSquare className="w-4 h-4 text-amber-300" />
              <span>Pending Queue (4)</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 6 Key Enterprise KPI Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* KPI 1 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Total Primavera L6</p>
          <p className="text-xl font-extrabold font-mono text-slate-900">1,240</p>
          <p className="text-[10px] text-slate-400 font-medium">Active Activities</p>
        </div>

        {/* KPI 2 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Updated Today</p>
          <p className="text-xl font-extrabold font-mono text-blue-600">14</p>
          <p className="text-[10px] text-blue-600 font-medium">From DSR / Excel / Audio</p>
        </div>

        {/* KPI 3 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Auto AI Matched</p>
          <p className="text-xl font-extrabold font-mono text-emerald-600">84.2%</p>
          <p className="text-[10px] text-emerald-600 font-medium">High Confidence Match</p>
        </div>

        {/* KPI 4 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Pending Verification</p>
          <p className="text-xl font-extrabold font-mono text-amber-600">4 Items</p>
          <p className="text-[10px] text-amber-600 font-medium">Requires Planner Sign-off</p>
        </div>

        {/* KPI 5 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Approved Commits</p>
          <p className="text-xl font-extrabold font-mono text-indigo-600">128 Logs</p>
          <p className="text-[10px] text-slate-400 font-medium">Committed to Database</p>
        </div>

        {/* KPI 6 */}
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
          <p className="text-[11px] font-semibold text-slate-500">Matching Accuracy</p>
          <p className="text-xl font-extrabold font-mono text-cyan-600">94.2%</p>
          <p className="text-[10px] text-cyan-600 font-medium">Validated Vector Match</p>
        </div>
      </div>

      {/* Main Workflow Visualizer Bar */}
      <Card title="AI Planning-to-Execution Bridge End-to-End Pipeline">
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-center text-xs font-semibold">
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700">
            <span className="block text-[10px] text-slate-400 font-bold uppercase">1. Site Input</span>
            DSR PDF / Excel / Voice
          </div>
          <div className="p-2.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-800">
            <span className="block text-[10px] text-blue-500 font-bold uppercase">2. AI Extraction</span>
            Entities & Quantities
          </div>
          <div className="p-2.5 rounded-lg bg-purple-50 border border-purple-200 text-purple-800">
            <span className="block text-[10px] text-purple-500 font-bold uppercase">3. Semantic Match</span>
            Vector Similarity
          </div>
          <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-800">
            <span className="block text-[10px] text-amber-500 font-bold uppercase">4. Confidence</span>
            High / Medium / Low
          </div>
          <div className="p-2.5 rounded-lg bg-sky-50 border border-sky-200 text-sky-800">
            <span className="block text-[10px] text-sky-500 font-bold uppercase">5. Verification</span>
            Planner Review Inbox
          </div>
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800">
            <span className="block text-[10px] text-emerald-500 font-bold uppercase">6. Approved Progress</span>
            Physical % Committed
          </div>
          <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-800">
            <span className="block text-[10px] text-indigo-500 font-bold uppercase">7. Audit Trail</span>
            Traceable Evidence
          </div>
        </div>
      </Card>

      {/* Main Grid: Dual S-Curve & Verification Inbox */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SCurveChart />
        </div>

        {/* Pending Verification Queue Preview */}
        <Card
          title="Pending Planner Verification"
          subtitle="Field updates awaiting human planner action"
          action={
            <Link href="/verification" className="text-xs text-blue-600 hover:text-blue-700 font-bold flex items-center gap-1">
              View All <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          }
        >
          <div className="space-y-3">
            {MOCK_EXTRACTIONS_AND_MATCHES.slice(0, 3).map((item) => (
              <div key={item.id} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-amber-700">{item.primaryMatch.l6ActivityCode}</span>
                  <ConfidenceBadge score={item.primaryMatch.totalConfidenceScore} rating={item.primaryMatch.confidenceRating} />
                </div>
                <p className="font-bold text-slate-800 line-clamp-1">{item.primaryMatch.l6ActivityName}</p>
                <p className="text-[11px] text-slate-500 italic line-clamp-1">"{item.extractedEvent.rawText}"</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent Approved Audit Trail Feeds */}
      <Card
        title="Recent Approved Progress Updates"
        subtitle="Latest verified site progress updates written to Primavera P6 / Project Database"
        action={
          <Link href="/history" className="text-xs text-blue-600 hover:text-blue-700 font-bold flex items-center gap-1">
            Full Audit History <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        }
      >
        <div className="space-y-2">
          {MOCK_AUDIT_LOGS.slice(0, 3).map((log) => (
            <div key={log.id} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-amber-700">{log.activityCode}</span>
                  <span className="font-bold text-slate-800">{log.activityName}</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">{log.details}</p>
              </div>
              <div className="text-right font-mono">
                <span className="text-emerald-700 font-bold">{log.newProgress}% Approved</span>
                <p className="text-[10px] text-slate-400 font-sans">{log.actor}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
