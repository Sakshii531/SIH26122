'use client';

import React from 'react';
import Link from 'next/link';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CalendarDays,
  ChevronDown,
  Clock3,
  FileCheck2,
  FileText,
  Lightbulb,
  MoreHorizontal,
  Paperclip,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { MOCK_ALL_L6_ACTIVITIES } from '../../services/mock/mockSchedules.js';
import { MOCK_EXTRACTIONS_AND_MATCHES } from '../../services/mock/mockExtractions.js';
import { MOCK_FIELD_REPORTS } from '../../services/mock/mockFieldReports.js';
import { MOCK_AUDIT_LOGS, MOCK_S_CURVE_DATA } from '../../services/mock/mockAuditLogs.js';
import { MOCK_PROJECTS } from '../../services/mock/mockProjects.js';

const activeProject = MOCK_PROJECTS[0];

function KpiCard({ label, value, detail, icon: Icon, tone = 'orange', trend }) {
  const tones = {
    orange: 'bg-orange-50 text-[#FA5A16] border-orange-100',
    blue: 'bg-slate-100 text-slate-600 border-slate-200',
    green: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    slate: 'bg-slate-100 text-slate-600 border-slate-200',
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-semibold text-slate-500">{label}</p>
        <span className={`flex h-8 w-8 items-center justify-center rounded-lg border ${tones[tone]}`}>
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <p className="mt-3 text-2xl font-bold tracking-tight text-slate-900">{value}</p>
      <div className="mt-1 flex items-center gap-1.5 text-[11px] text-slate-500">
        {trend && <span className={trend.startsWith('+') ? 'font-semibold text-emerald-600' : 'font-semibold text-amber-600'}>{trend}</span>}
        <span>{detail}</span>
      </div>
    </div>
  );
}

function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div>
        <h2 className="text-sm font-bold text-slate-900">{title}</h2>
        {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

function Panel({ children, className = '' }) {
  return <section className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</section>;
}

function ProgressBar({ value, color = 'bg-[#FA5A16]' }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(value, 100)}%` }} />
    </div>
  );
}

export function DashboardOverview() {
  const progressVariance = activeProject.overallActualProgress - activeProject.overallPlannedProgress;
  const evidenceCount = MOCK_FIELD_REPORTS.reduce((total, report) => total + report.evidenceCount, 0);
  const verifiedReports = MOCK_FIELD_REPORTS.filter((report) => report.status === 'Verified').length;
  const activeActivities = MOCK_ALL_L6_ACTIVITIES.filter((activity) => activity.status === 'In Progress').length;

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
              <span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />
              Planner workspace / overview
            </div>
            <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">Project Overview</h1>
            <p className="mt-1 text-sm text-slate-500">A live view of progress, schedule health, and field execution.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm">
              <CalendarDays className="h-3.5 w-3.5 text-slate-400" />
              08 Sep 2026
              <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
            </button>
          </div>
        </div>


        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <KpiCard label="Overall Progress" value={`${activeProject.overallActualProgress}%`} detail="Project completion" icon={Target} tone="orange" trend="+4.8%" />
          <KpiCard label="Planned Progress" value={`${activeProject.overallPlannedProgress}%`} detail="Baseline plan" icon={CalendarDays} tone="blue" />
          <KpiCard label="Actual Progress" value={`${activeProject.overallActualProgress}%`} detail="Approved physical" icon={TrendingUp} tone="green" trend="+2.1%" />
          <KpiCard label="Schedule Variance" value={`${Math.abs(progressVariance).toFixed(1)} pts`} detail="Behind baseline" icon={Clock3} tone="amber" trend="-7.2 pts" />
          <KpiCard label="Active Activities" value={activeProject.totalActivities.toLocaleString()} detail={`${activeActivities} updates in progress`} icon={Activity} tone="slate" />
        </div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,0.8fr)]">
          <Panel>
            <SectionHeader title="Planned vs Actual Progress" subtitle="Cumulative project progress against the approved baseline" action={<button className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500">Last 12 months <ChevronDown className="h-3.5 w-3.5" /></button>} />
            <div className="h-[260px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={MOCK_S_CURVE_DATA} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                  <defs>
                    <linearGradient id="plannerActualFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#FA5A16" stopOpacity={0.2} /><stop offset="95%" stopColor="#FA5A16" stopOpacity={0} /></linearGradient>
                    <linearGradient id="plannerPlanFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#94A3B8" stopOpacity={0.12} /><stop offset="95%" stopColor="#94A3B8" stopOpacity={0} /></linearGradient>
                  </defs>
                  <CartesianGrid stroke="#E8EDF2" vertical={false} />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
                  <Tooltip contentStyle={{ border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 12, boxShadow: '0 4px 14px rgba(15,23,42,.08)' }} />
                  <Area type="monotone" dataKey="planned" name="Planned" stroke="#94A3B8" strokeWidth={2} strokeDasharray="5 5" fill="url(#plannerPlanFill)" />
                  <Area type="monotone" dataKey="actual" name="Actual" stroke="#FA5A16" strokeWidth={2.5} fill="url(#plannerActualFill)" connectNulls={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex items-center gap-5 text-[11px] text-slate-500"><span className="inline-flex items-center gap-2"><i className="h-0.5 w-5 border-t-2 border-dashed border-slate-400" /> Planned</span><span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[#FA5A16]" /> Actual</span></div>
          </Panel>

          <Panel>
            <SectionHeader title="Project Health" subtitle="Current delivery signals" action={<MoreHorizontal className="h-4 w-4 text-slate-400" />} />
            <div className="flex items-center gap-4 rounded-lg bg-amber-50 p-4"><div className="flex h-12 w-12 items-center justify-center rounded-full border-4 border-amber-200 bg-white text-amber-600"><Clock3 className="h-5 w-5" /></div><div><p className="text-sm font-bold text-amber-800">Needs attention</p><p className="mt-1 text-xs leading-relaxed text-amber-700">Actual progress is below baseline by 7.2 percentage points.</p></div></div>
            <div className="mt-5 space-y-4">
              <div><div className="mb-1.5 flex justify-between text-xs"><span className="text-slate-500">Schedule health</span><strong className="text-amber-600">At risk</strong></div><ProgressBar value={activeProject.spi * 100} color="bg-amber-500" /></div>
              <div><div className="mb-1.5 flex justify-between text-xs"><span className="text-slate-500">Cost health</span><strong className="text-emerald-600">On track</strong></div><ProgressBar value={activeProject.cpi * 100} color="bg-emerald-500" /></div>
              <div><div className="mb-1.5 flex justify-between text-xs"><span className="text-slate-500">Field reporting</span><strong className="text-[#FA5A16]">{verifiedReports}/{MOCK_FIELD_REPORTS.length} verified</strong></div><ProgressBar value={(verifiedReports / MOCK_FIELD_REPORTS.length) * 100} color="bg-[#FA5A16]" /></div>
            </div>
          </Panel>
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.7fr)]">
          <Panel>
            <SectionHeader title="Schedule Performance" subtitle="Performance indices against baseline" />
            <div className="grid grid-cols-2 gap-3"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[11px] text-slate-500">SPI</p><p className="mt-1 text-2xl font-bold text-amber-600">{activeProject.spi}</p><p className="mt-1 text-[10px] text-slate-500">Schedule index</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[11px] text-slate-500">CPI</p><p className="mt-1 text-2xl font-bold text-emerald-600">{activeProject.cpi}</p><p className="mt-1 text-[10px] text-slate-500">Cost index</p></div></div>
            <div className="mt-5 space-y-3 text-xs"><div className="flex items-center justify-between"><span className="text-slate-500">Delayed activities</span><strong className="text-slate-900">{activeProject.activeDelaysCount}</strong></div><div className="flex items-center justify-between"><span className="text-slate-500">Pending verification</span><strong className="text-slate-900">{activeProject.pendingVerificationsCount}</strong></div><div className="flex items-center justify-between"><span className="text-slate-500">Last sync</span><strong className="text-slate-700">Today, 18:02</strong></div></div>
            <Link href="/analytics" className="mt-5 inline-flex items-center gap-1 text-xs font-bold text-[#FA5A16]">View analytics <ArrowRight className="h-3.5 w-3.5" /></Link>
          </Panel>

          <Panel className="min-w-0 overflow-hidden">
            <SectionHeader title="Activity Progress" subtitle="Priority L6 activities across the active project" action={<Link href="/schedule" className="text-xs font-bold text-[#FA5A16]">View schedule</Link>} />
            <div className="overflow-x-auto"><table className="w-full min-w-[620px] text-left text-xs"><thead><tr className="border-b border-slate-100 text-[10px] uppercase tracking-wider text-slate-400"><th className="pb-2 font-semibold">Activity</th><th className="pb-2 font-semibold">Status</th><th className="pb-2 font-semibold">Planned</th><th className="pb-2 font-semibold">Actual</th><th className="pb-2 text-right font-semibold">Variance</th></tr></thead><tbody className="divide-y divide-slate-100">{MOCK_ALL_L6_ACTIVITIES.slice(0, 5).map((activity) => { const variance = activity.actualProgressPercent - activity.plannedProgressPercent; return <tr key={activity.id} className="align-middle"><td className="max-w-[270px] py-3 pr-4"><p className="truncate font-semibold text-slate-800">{activity.name}</p><p className="mt-1 font-mono text-[10px] text-slate-400">{activity.code}</p></td><td className="py-3 pr-4"><span className={`inline-flex rounded-full px-2 py-1 text-[10px] font-semibold ${activity.status === 'Completed' ? 'bg-emerald-50 text-emerald-700' : activity.status === 'In Progress' ? 'bg-orange-50 text-[#FA5A16]' : 'bg-slate-100 text-slate-600'}`}>{activity.status}</span></td><td className="py-3 pr-4 text-slate-600">{activity.plannedProgressPercent}%</td><td className="py-3 pr-4"><div className="flex items-center gap-2"><span className="w-8 text-slate-700">{activity.actualProgressPercent}%</span><div className="w-16"><ProgressBar value={activity.actualProgressPercent} color={activity.actualProgressPercent >= activity.plannedProgressPercent ? 'bg-emerald-500' : 'bg-[#FA5A16]'} /></div></div></td><td className={`py-3 text-right font-semibold ${variance >= 0 ? 'text-emerald-600' : 'text-amber-600'}`}>{variance > 0 ? '+' : ''}{variance} pts</td></tr>; })}</tbody></table></div>
          </Panel>
        </div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.1fr_0.8fr_1fr]">
          <Panel>
            <SectionHeader title="AI Insights" subtitle="Signals from the latest field updates" action={<Sparkles className="h-4 w-4 text-[#FA5A16]" />} />
            <div className="space-y-3">{MOCK_EXTRACTIONS_AND_MATCHES.slice(0, 3).map((item, index) => <div key={item.id} className="flex gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3"><div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md ${index === 0 ? 'bg-orange-50 text-[#FA5A16]' : 'bg-amber-50 text-amber-600'}`}><Lightbulb className="h-3.5 w-3.5" /></div><div className="min-w-0"><p className="text-xs font-semibold text-slate-800">{index === 0 ? 'Concrete pour is tracking below baseline' : index === 1 ? 'Rain interruption detected on Span 12-13' : 'D-wall excavation needs review'}</p><p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-slate-500">{item.primaryMatch.matchingRationale}</p></div></div>)}</div>
            <Link href="/matching" className="mt-4 inline-flex items-center gap-1 text-xs font-bold text-[#FA5A16]">Open AI matching <ArrowRight className="h-3.5 w-3.5" /></Link>
          </Panel>

          <Panel>
            <SectionHeader title="Field Evidence" subtitle="Latest submitted project evidence" action={<Paperclip className="h-4 w-4 text-slate-400" />} />
            <div className="flex items-end justify-between"><div><p className="text-3xl font-bold text-slate-900">{evidenceCount}</p><p className="mt-1 text-xs text-slate-500">files attached to reports</p></div><div className="rounded-lg bg-emerald-50 p-2.5 text-emerald-600"><FileCheck2 className="h-5 w-5" /></div></div>
            <div className="mt-5 space-y-3"><div className="flex items-center justify-between text-xs"><span className="text-slate-500">Reports received</span><strong className="text-slate-800">{MOCK_FIELD_REPORTS.length}</strong></div><div className="flex items-center justify-between text-xs"><span className="text-slate-500">Verified reports</span><strong className="text-emerald-600">{verifiedReports}</strong></div><div className="flex items-center justify-between text-xs"><span className="text-slate-500">Latest submission</span><strong className="text-slate-700">08 Sep 2026</strong></div></div>
            <Link href="/traceability" className="mt-5 inline-flex items-center gap-1 text-xs font-bold text-[#FA5A16]">View evidence <ArrowRight className="h-3.5 w-3.5" /></Link>
          </Panel>

          <Panel>
            <SectionHeader title="Recent Activity" subtitle="Latest project events" action={<Link href="/history" className="text-xs font-bold text-[#FA5A16]">View all</Link>} />
            <div className="space-y-4">{MOCK_AUDIT_LOGS.slice(0, 4).map((log, index) => <div key={log.id} className="flex gap-3"><div className={`mt-1 h-2 w-2 shrink-0 rounded-full ${index === 0 ? 'bg-emerald-500' : 'bg-slate-300'}`} /><div className="min-w-0 flex-1"><p className="truncate text-xs font-semibold text-slate-800">{log.activityName}</p><p className="mt-1 truncate text-[11px] text-slate-500">{log.action.replaceAll('_', ' ')} · {log.newProgress}% approved</p></div><span className="shrink-0 text-[10px] text-slate-400">{index + 1}d ago</span></div>)}</div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
