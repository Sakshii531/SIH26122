'use client';

import React, { useMemo, useState } from 'react';
import {
  Activity,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  FileText,
  Filter,
  Search,
  SlidersHorizontal,
  Target,
  X,
} from 'lucide-react';
import { SupervisorDailyReportForm } from '../../../components/capture/SupervisorDailyReportForm.jsx';
import { useRoleContext } from '../../../components/providers/RoleContext.jsx';
import { ROLES } from '../../../hooks/useRole.js';
import { MOCK_ALL_L6_ACTIVITIES } from '../../../services/mock/mockSchedules.js';
import { MOCK_FIELD_REPORTS } from '../../../services/mock/mockFieldReports.js';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const PAGE_SIZE = 5;
const ACTIVE_PROJECT = MOCK_PROJECTS[0];

function formatDate(value) {
  if (!value) return '-';
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function statusClass(status) {
  if (status === 'Completed') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (status === 'In Progress') return 'border-orange-200 bg-orange-50 text-[#FA5A16]';
  return 'border-slate-200 bg-slate-100 text-slate-600';
}

function ProgressBar({ value }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
      <div className="h-full rounded-full bg-[#FA5A16]" style={{ width: `${Math.min(value, 100)}%` }} />
    </div>
  );
}

function PlannerActivitiesPage() {
  const [query, setQuery] = useState('');
  const [discipline, setDiscipline] = useState('All disciplines');
  const [status, setStatus] = useState('All statuses');
  const [wbsLevel, setWbsLevel] = useState('All WBS levels');
  const [progressRange, setProgressRange] = useState('All progress');
  const [dateHorizon, setDateHorizon] = useState('Full horizon');
  const [selectedId, setSelectedId] = useState(MOCK_ALL_L6_ACTIVITIES[1]?.id || MOCK_ALL_L6_ACTIVITIES[0]?.id);
  const [page, setPage] = useState(1);

  const filteredActivities = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return MOCK_ALL_L6_ACTIVITIES.filter((activity) => {
      const matchesQuery = !normalizedQuery || [activity.id, activity.code, activity.name, activity.wbsPath].some((value) => value?.toLowerCase().includes(normalizedQuery));
      const matchesDiscipline = discipline === 'All disciplines' || activity.discipline === discipline;
      const matchesStatus = status === 'All statuses' || activity.status === status;
      const matchesLevel = wbsLevel === 'All WBS levels' || activity.wbsPath?.includes(wbsLevel);
      const matchesProgress = progressRange === 'All progress'
        || (progressRange === '0-25%' && activity.actualProgressPercent <= 25)
        || (progressRange === '26-75%' && activity.actualProgressPercent > 25 && activity.actualProgressPercent <= 75)
        || (progressRange === '76-100%' && activity.actualProgressPercent > 75);
      const matchesHorizon = dateHorizon === 'Full horizon'
        || (dateHorizon === 'Current month' && activity.plannedStart?.startsWith('2026-09'))
        || (dateHorizon === 'Next 30 days' && activity.plannedStart >= '2026-09-09' && activity.plannedStart <= '2026-10-09');
      return matchesQuery && matchesDiscipline && matchesStatus && matchesLevel && matchesProgress && matchesHorizon;
    });
  }, [query, discipline, status, wbsLevel, progressRange, dateHorizon]);

  const totalPages = Math.max(1, Math.ceil(filteredActivities.length / PAGE_SIZE));
  const visibleActivities = filteredActivities.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const selectedActivity = MOCK_ALL_L6_ACTIVITIES.find((activity) => activity.id === selectedId) || filteredActivities[0] || MOCK_ALL_L6_ACTIVITIES[0];
  const relatedReports = MOCK_FIELD_REPORTS.filter((report) => selectedActivity?.name?.toLowerCase().split(' ').some((term) => term.length > 4 && report.summary?.toLowerCase().includes(term))).slice(0, 3);
  const variance = selectedActivity ? selectedActivity.actualProgressPercent - selectedActivity.plannedProgressPercent : 0;

  const resetFilters = () => {
    setQuery('');
    setDiscipline('All disciplines');
    setStatus('All statuses');
    setWbsLevel('All WBS levels');
    setProgressRange('All progress');
    setDateHorizon('Full horizon');
    setPage(1);
  };

  const updateFilter = (setter) => (event) => {
    setter(event.target.value);
    setPage(1);
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"><span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />Planning workspace / project plan</div>
            <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">ACTIVITIES</h1>
            <p className="mt-1 text-sm text-slate-500">Inspect planned work, progress, and field execution for the active project.</p>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-900"><Filter className="h-4 w-4 text-[#FA5A16]" /> Search and filter activities</div>
          <div className="grid grid-cols-1 gap-2.5 md:grid-cols-2 xl:grid-cols-[minmax(260px,1.8fr)_repeat(5,minmax(135px,1fr))_auto]">
            <div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Activity ID, name or WBS" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs outline-none transition focus:border-[#FA5A16] focus:bg-white" /></div>
            <select value={discipline} onChange={updateFilter(setDiscipline)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All disciplines</option><option>Civil</option><option>Structural</option><option>Geotechnical</option><option>Mechanical</option></select>
            <select value={status} onChange={updateFilter(setStatus)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All statuses</option><option>Completed</option><option>In Progress</option><option>Not Started</option></select>
            <select value={wbsLevel} onChange={updateFilter(setWbsLevel)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All WBS levels</option><option>Substructure</option><option>Superstructure</option><option>Stations</option></select>
            <select value={progressRange} onChange={updateFilter(setProgressRange)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All progress</option><option>0-25%</option><option>26-75%</option><option>76-100%</option></select>
            <select value={dateHorizon} onChange={updateFilter(setDateHorizon)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>Full horizon</option><option>Current month</option><option>Next 30 days</option></select>
            <button onClick={resetFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 hover:bg-slate-100 hover:text-slate-800"><X className="h-3.5 w-3.5" /> Clear</button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(330px,0.85fr)]">
          <section className="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="text-sm font-bold tracking-wide text-slate-900">ACTIVITY LIST</h2><p className="mt-1 text-xs text-slate-500">{filteredActivities.length} activities in the active project</p></div><button className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]"><SlidersHorizontal className="h-3.5 w-3.5" /> Columns</button></div>
            <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-xs"><thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="px-4 py-3 font-bold">Activity ID</th><th className="px-4 py-3 font-bold">Activity Name & WBS</th><th className="px-4 py-3 font-bold">Discipline</th><th className="px-4 py-3 font-bold">Planned Window</th><th className="px-4 py-3 font-bold">Progress</th></tr></thead><tbody className="divide-y divide-slate-100">{visibleActivities.map((activity) => <tr key={activity.id} onClick={() => setSelectedId(activity.id)} className={`cursor-pointer transition ${selectedActivity?.id === activity.id ? 'bg-orange-50/70' : 'hover:bg-slate-50'}`}><td className="whitespace-nowrap px-4 py-3 font-mono font-bold text-[#FA5A16]">{activity.code}</td><td className="max-w-[300px] px-4 py-3"><p className="truncate font-semibold text-slate-800">{activity.name}</p><p className="mt-1 truncate text-[10px] text-slate-400">{activity.wbsPath}</p></td><td className="px-4 py-3 text-slate-600">{activity.discipline}</td><td className="whitespace-nowrap px-4 py-3 text-slate-600"><p>{formatDate(activity.plannedStart)}</p><p className="mt-1 text-[10px] text-slate-400">to {formatDate(activity.plannedFinish)}</p></td><td className="w-32 px-4 py-3"><div className="mb-1 flex items-center justify-between text-[10px] font-bold text-slate-700"><span>{activity.actualProgressPercent}%</span><span className={`rounded-full border px-1.5 py-0.5 ${statusClass(activity.status)}`}>{activity.status}</span></div><ProgressBar value={activity.actualProgressPercent} /></td></tr>)}</tbody></table></div>
            <div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-3 text-xs sm:flex-row sm:items-center sm:justify-between"><span className="text-slate-500">Showing {filteredActivities.length ? (page - 1) * PAGE_SIZE + 1 : 0}-{Math.min(page * PAGE_SIZE, filteredActivities.length)} of {filteredActivities.length}</span><div className="flex items-center gap-1">{Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => <button key={number} onClick={() => setPage(number)} className={`h-7 min-w-7 rounded-md px-2 font-bold ${page === number ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-100'}`}>{number}</button>)}</div></div>
          </section>

          <aside className="min-w-0 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-4"><div><p className="text-[10px] font-bold uppercase tracking-wider text-[#FA5A16]">Selected activity</p><h2 className="mt-1 text-base font-bold leading-snug text-slate-900">Activity Details</h2></div><Activity className="h-5 w-5 text-[#FA5A16]" /></div>
            {selectedActivity ? <div className="space-y-5 pt-4"><div><div className="flex flex-wrap items-center gap-2"><span className="rounded-md bg-orange-50 px-2 py-1 font-mono text-[10px] font-bold text-[#FA5A16]">{selectedActivity.code}</span><span className={`rounded-full border px-2 py-1 text-[10px] font-bold ${statusClass(selectedActivity.status)}`}>{selectedActivity.status}</span></div><h3 className="mt-3 text-sm font-bold leading-relaxed text-slate-900">{selectedActivity.name}</h3><p className="mt-1 text-[11px] leading-relaxed text-slate-500">{selectedActivity.wbsPath}</p></div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><div className="mb-2 flex items-center justify-between text-xs"><span className="font-semibold text-slate-600">Actual progress</span><strong className="text-xl text-[#FA5A16]">{selectedActivity.actualProgressPercent}%</strong></div><ProgressBar value={selectedActivity.actualProgressPercent} /><div className="mt-2 flex items-center justify-between text-[10px] text-slate-500"><span>Target {selectedActivity.plannedProgressPercent}%</span><span className={variance >= 0 ? 'font-semibold text-emerald-600' : 'font-semibold text-amber-600'}>{variance >= 0 ? '+' : ''}{variance} pts variance</span></div></div>
              <div className="grid grid-cols-2 gap-2 text-xs"><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Specification</p><p className="mt-1 font-semibold text-slate-800">{selectedActivity.baselineQuantity} {selectedActivity.unitOfMeasure}</p></div><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Duration</p><p className="mt-1 font-semibold text-slate-800">{selectedActivity.plannedDurationDays} days</p></div></div>
              <div><h4 className="flex items-center gap-2 text-xs font-bold text-slate-900"><CalendarDays className="h-4 w-4 text-[#FA5A16]" /> Schedule chronology</h4><div className="mt-2 space-y-2 border-l border-orange-200 pl-4 text-xs"><div><p className="font-semibold text-slate-700">Planned start</p><p className="mt-0.5 text-slate-500">{formatDate(selectedActivity.plannedStart)}</p></div><div><p className="font-semibold text-slate-700">Planned finish</p><p className="mt-0.5 text-slate-500">{formatDate(selectedActivity.plannedFinish)}</p></div><div><p className="font-semibold text-slate-700">Actual start</p><p className="mt-0.5 text-slate-500">{formatDate(selectedActivity.actualStart) || 'Not started'}</p></div></div></div>
              <div><h4 className="flex items-center gap-2 text-xs font-bold text-slate-900"><FileText className="h-4 w-4 text-[#FA5A16]" /> Related field reports</h4><div className="mt-2 space-y-2">{(relatedReports.length ? relatedReports : MOCK_FIELD_REPORTS.slice(0, 2)).map((report) => <div key={report.id} className="rounded-lg border border-slate-100 bg-slate-50 p-2.5"><div className="flex items-center justify-between"><span className="font-mono text-[10px] font-bold text-[#FA5A16]">{report.id}</span><span className="text-[10px] text-slate-400">{report.date}</span></div><p className="mt-1 line-clamp-2 text-[11px] font-semibold text-slate-700">{report.activity}</p><p className="mt-1 text-[10px] text-slate-500">{report.evidenceCount} evidence files · {report.status}</p></div>)}</div></div>
              <button className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[#FA5A16] px-3 py-2.5 text-xs font-bold text-white hover:bg-[#E44E0E]"><CheckCircle2 className="h-4 w-4" /> Open activity record</button>
            </div> : <div className="py-12 text-center text-xs text-slate-500">No activity matches the current filters.</div>}
          </aside>
        </div>
      </div>
    </div>
  );
}

export default function CapturePage() {
  const { role } = useRoleContext();
  if (role === ROLES.PLANNER || role === ROLES.MANAGER || role === ROLES.ADMIN) return <PlannerActivitiesPage />;
  return <SupervisorDailyReportForm />;
}
