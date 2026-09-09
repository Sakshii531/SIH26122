'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  CalendarDays,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Download,
  FileSpreadsheet,
  Folder,
  List,
  RotateCcw,
  Search,
  SlidersHorizontal,
  TableProperties,
  X,
} from 'lucide-react';
import { scheduleService } from '../../../services/scheduleService.js';
import { GanttChart } from '../../../components/schedule/GanttChart.jsx';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const PAGE_SIZE = 5;
const ACTIVE_PROJECT = MOCK_PROJECTS[0];

function formatDate(value) {
  if (!value) return '-';
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (status === 'In Progress') return 'bg-orange-50 text-[#FA5A16] border-orange-200';
  return 'bg-slate-100 text-slate-600 border-slate-200';
}

function flattenTree(nodes, expandedNodes, selectedActivity, onToggle, onSelect) {
  const rows = [];

  const visit = (node, depth = 0) => {
    const hasChildren = Boolean(node.children?.length || node.activities?.length);
    rows.push({ type: 'wbs', node, depth, hasChildren, expanded: expandedNodes[node.id] });
    if (!expandedNodes[node.id]) return;

    node.children?.forEach((child) => visit(child, depth + 1));
    node.activities?.forEach((activity) => {
      rows.push({
        type: 'activity',
        activity,
        depth: depth + 1,
        selected: selectedActivity?.id === activity.id,
        onSelect,
        onToggle,
      });
    });
  };

  nodes.forEach((node) => visit(node));
  return rows;
}

function InfoCard({ label, value, icon: Icon }) {
  return (
    <div className="min-w-0 rounded-lg border border-slate-200 bg-white px-4 py-3">
      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
        <Icon className="h-3.5 w-3.5 text-[#FA5A16]" />
        {label}
      </div>
      <p className="mt-2 truncate text-sm font-bold text-slate-900">{value}</p>
    </div>
  );
}

export default function SchedulePage() {
  const [wbsData, setWbsData] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [view, setView] = useState('list');
  const [search, setSearch] = useState('');
  const [wbsFilter, setWbsFilter] = useState('All WBS');
  const [discipline, setDiscipline] = useState('All disciplines');
  const [status, setStatus] = useState('All statuses');
  const [dateRange, setDateRange] = useState('Full schedule range');
  const [expandedNodes, setExpandedNodes] = useState({});
  const [page, setPage] = useState(1);

  useEffect(() => {
    scheduleService.getWBSTree(ACTIVE_PROJECT.id).then((data) => {
      setWbsData(data);
      const expanded = {};
      const markExpanded = (nodes) => nodes.forEach((node) => {
        expanded[node.id] = true;
        if (node.children) markExpanded(node.children);
      });
      markExpanded(data);
      setExpandedNodes(expanded);
      setSelectedActivity(data[0]?.children?.[1]?.children?.[0]?.children?.[0]?.activities?.[0] || null);
    });
  }, []);

  const allActivities = useMemo(() => {
    const activities = [];
    const visit = (nodes) => nodes.forEach((node) => {
      node.activities?.forEach((activity) => activities.push(activity));
      if (node.children) visit(node.children);
    });
    visit(wbsData);
    return activities;
  }, [wbsData]);

  const wbsOptions = useMemo(() => [...new Set(allActivities.map((activity) => activity.wbsId).filter(Boolean))], [allActivities]);

  const filteredActivities = useMemo(() => {
    const query = search.trim().toLowerCase();
    return allActivities.filter((activity) => {
      const matchesQuery = !query || [activity.code, activity.name, activity.wbsPath, activity.id].some((value) => value?.toLowerCase().includes(query));
      const matchesWbs = wbsFilter === 'All WBS' || activity.wbsId === wbsFilter;
      const matchesDiscipline = discipline === 'All disciplines' || activity.discipline === discipline;
      const matchesStatus = status === 'All statuses' || activity.status === status;
      const matchesDateRange = dateRange === 'Full schedule range'
        || (dateRange === 'Current month' && activity.plannedStart?.startsWith('2026-09'))
        || (dateRange === 'Next 30 days' && activity.plannedStart >= '2026-09-09' && activity.plannedStart <= '2026-10-09');
      return matchesQuery && matchesWbs && matchesDiscipline && matchesStatus && matchesDateRange;
    });
  }, [allActivities, search, wbsFilter, discipline, status, dateRange]);

  const filteredIds = useMemo(() => new Set(filteredActivities.map((activity) => activity.id)), [filteredActivities]);
  const pagedIds = useMemo(() => new Set(filteredActivities.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map((activity) => activity.id)), [filteredActivities, page]);
  const visibleRows = useMemo(() => {
    const rows = flattenTree(wbsData, expandedNodes, selectedActivity, setExpandedNodes, setSelectedActivity);
    return rows.filter((row) => row.type === 'wbs' || (filteredIds.has(row.activity.id) && pagedIds.has(row.activity.id)));
  }, [wbsData, expandedNodes, selectedActivity, filteredIds, pagedIds]);

  const totalPages = Math.max(1, Math.ceil(filteredActivities.length / PAGE_SIZE));
  const hasFilters = search || wbsFilter !== 'All WBS' || discipline !== 'All disciplines' || status !== 'All statuses' || dateRange !== 'Full schedule range';

  const resetFilters = () => {
    setSearch('');
    setWbsFilter('All WBS');
    setDiscipline('All disciplines');
    setStatus('All statuses');
    setDateRange('Full schedule range');
    setPage(1);
  };

  const toggleAll = (expanded) => {
    const next = {};
    const mark = (nodes) => nodes.forEach((node) => {
      next[node.id] = expanded;
      if (node.children) mark(node.children);
    });
    mark(wbsData);
    setExpandedNodes(next);
  };

  const exportSchedule = () => {
    const header = ['WBS', 'Activity ID', 'Activity Name', 'Discipline', 'Planned Start', 'Planned Finish', 'Duration', 'Status'];
    const rows = filteredActivities.map((activity) => [
      activity.wbsPath,
      activity.id,
      activity.name,
      activity.discipline,
      activity.plannedStart,
      activity.plannedFinish,
      `${activity.plannedDurationDays} days`,
      activity.status,
    ]);
    const csv = [header, ...rows].map((row) => row.map((value) => `"${String(value ?? '').replaceAll('"', '""')}"`).join(',')).join('\n');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    link.download = `${ACTIVE_PROJECT.code}-schedule.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
              <span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />
              Planning workspace
            </div>
            <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">PROJECT PLAN</h1>
            <p className="mt-1 text-sm text-slate-500">Manage the approved baseline, activities, and planned project timeline.</p>
          </div>
          <button onClick={exportSchedule} className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#FA5A16] px-3.5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-[#E44E0E]">
            <Download className="h-4 w-4" />
            Export Schedule CSV/XLSX
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
          <InfoCard label="Project Code" value={ACTIVE_PROJECT.code} icon={FileSpreadsheet} />
          <InfoCard label="Planned Start" value={formatDate(ACTIVE_PROJECT.startDate)} icon={CalendarDays} />
          <InfoCard label="Planned Finish" value={formatDate(ACTIVE_PROJECT.targetCompletion)} icon={CalendarDays} />
          <InfoCard label="Total Duration" value="896 days" icon={CalendarDays} />
          <InfoCard label="Activities" value={ACTIVE_PROJECT.totalActivities.toLocaleString()} icon={TableProperties} />
          <InfoCard label="Calendar" value="7 days / week" icon={CalendarDays} />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-2.5 xl:grid-cols-[minmax(260px,1.8fr)_repeat(3,minmax(150px,1fr))_auto]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder="Search WBS, activity or ID" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs text-slate-800 outline-none transition focus:border-[#FA5A16] focus:bg-white" />
            </div>
            <select value={wbsFilter} onChange={(event) => { setWbsFilter(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs font-medium text-slate-600 outline-none"><option>All WBS</option>{wbsOptions.map((option) => <option key={option}>{option}</option>)}</select>
            <select value={discipline} onChange={(event) => { setDiscipline(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs font-medium text-slate-600 outline-none"><option>All disciplines</option><option>Civil</option><option>Structural</option><option>Geotechnical</option><option>Mechanical</option></select>
            <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs font-medium text-slate-600 outline-none"><option>All statuses</option><option>Completed</option><option>In Progress</option><option>Not Started</option></select>
            <select value={dateRange} onChange={(event) => setDateRange(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs font-medium text-slate-600 outline-none"><option>Full schedule range</option><option>Current month</option><option>Next 30 days</option></select>
            <button onClick={resetFilters} disabled={!hasFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 disabled:cursor-default disabled:opacity-50"><RotateCcw className="h-3.5 w-3.5" /> Clear</button>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
            <button onClick={() => setView('list')} className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-bold ${view === 'list' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}><List className="h-3.5 w-3.5" /> List View</button>
            <button onClick={() => setView('gantt')} className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-bold ${view === 'gantt' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}><TableProperties className="h-3.5 w-3.5" /> Gantt View</button>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <button onClick={() => toggleAll(true)} className="rounded-md border border-slate-200 bg-white px-3 py-2 font-semibold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]">Expand All</button>
            <button onClick={() => toggleAll(false)} className="rounded-md border border-slate-200 bg-white px-3 py-2 font-semibold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]">Collapse All</button>
          </div>
        </div>

        {view === 'list' ? (
          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div><h2 className="text-sm font-bold tracking-wide text-slate-900">WORK BREAKDOWN STRUCTURE</h2><p className="mt-1 text-xs text-slate-500">Hierarchical WBS and L6 activity baseline view</p></div>
              <span className="text-xs font-semibold text-slate-400">{filteredActivities.length} activities</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1120px] text-left text-xs">
                <thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="px-4 py-3 font-bold">WBS / Hierarchy</th><th className="px-4 py-3 font-bold">Activity ID</th><th className="px-4 py-3 font-bold">Activity Name</th><th className="px-4 py-3 font-bold">Discipline</th><th className="px-4 py-3 font-bold">Planned Start</th><th className="px-4 py-3 font-bold">Planned Finish</th><th className="px-4 py-3 font-bold">Duration</th><th className="px-4 py-3 font-bold">Planner Status</th><th className="px-4 py-3 text-right font-bold">Action</th></tr></thead>
                <tbody className="divide-y divide-slate-100">
                  {visibleRows.map((row) => row.type === 'wbs' ? (
                    <tr key={row.node.id} className="bg-slate-50/60 hover:bg-orange-50/40">
                      <td colSpan="9" className="px-4 py-3"><button onClick={() => setExpandedNodes((current) => ({ ...current, [row.node.id]: !current[row.node.id] }))} className="flex items-center gap-2 text-left" style={{ paddingLeft: `${row.depth * 20}px` }}>{row.hasChildren ? (row.expanded ? <ChevronDown className="h-4 w-4 text-[#FA5A16]" /> : <ChevronRight className="h-4 w-4 text-slate-400" />) : <span className="w-4" />}<Folder className="h-4 w-4 text-[#FA5A16]" /><span className="font-mono font-bold text-slate-500">{row.node.code}</span><span className="font-bold text-slate-800">{row.node.name}</span></button></td>
                    </tr>
                  ) : (
                    <tr key={row.activity.id} className={`${row.selected ? 'bg-orange-50/60' : 'hover:bg-slate-50'}`}>
                      <td className="px-4 py-3" style={{ paddingLeft: `${28 + row.depth * 20}px` }}><span className="font-mono text-[10px] font-bold text-slate-400">{row.activity.wbsId}</span></td>
                      <td className="px-4 py-3 font-mono font-bold text-[#FA5A16]">{row.activity.code}</td>
                      <td className="max-w-[280px] px-4 py-3 font-semibold text-slate-800">{row.activity.name}</td>
                      <td className="px-4 py-3 text-slate-600">{row.activity.discipline}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-slate-600">{formatDate(row.activity.plannedStart)}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-slate-600">{formatDate(row.activity.plannedFinish)}</td>
                      <td className="px-4 py-3 text-slate-600">{row.activity.plannedDurationDays} days</td>
                      <td className="px-4 py-3"><span className={`inline-flex rounded-full border px-2 py-1 text-[10px] font-bold ${statusClass(row.activity.status)}`}>{row.activity.status}</span></td>
                      <td className="px-4 py-3 text-right"><button onClick={() => setSelectedActivity(row.activity)} className="rounded-md border border-slate-200 px-2.5 py-1.5 text-[11px] font-bold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]">View</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-3 text-xs sm:flex-row sm:items-center sm:justify-between"><span className="text-slate-500">Showing {filteredActivities.length ? (page - 1) * PAGE_SIZE + 1 : 0}-{Math.min(page * PAGE_SIZE, filteredActivities.length)} of {filteredActivities.length} activities</span><div className="flex items-center gap-1">{Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => <button key={number} onClick={() => setPage(number)} className={`h-7 min-w-7 rounded-md px-2 font-bold ${page === number ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-100'}`}>{number}</button>)}</div></div>
          </section>
        ) : (
          <section><div className="mb-3"><h2 className="text-sm font-bold tracking-wide text-slate-900">PLANNED TIMELINE HORIZON (2026 BASELINE GANTT)</h2><p className="mt-1 text-xs text-slate-500">Horizontal baseline and approved actual progress timeline.</p></div><GanttChart selectedActivity={selectedActivity} onSelectActivity={setSelectedActivity} /></section>
        )}

        {view === 'list' && (
          <section><div className="mb-3 flex items-center justify-between"><div><h2 className="text-sm font-bold tracking-wide text-slate-900">PLANNED TIMELINE HORIZON (2026 BASELINE GANTT)</h2><p className="mt-1 text-xs text-slate-500">Horizontal baseline and approved actual progress timeline.</p></div><SlidersHorizontal className="h-4 w-4 text-slate-400" /></div><GanttChart selectedActivity={selectedActivity} onSelectActivity={setSelectedActivity} /></section>
        )}
      </div>
    </div>
  );
}
