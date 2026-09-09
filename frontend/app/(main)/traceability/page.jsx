'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Download,
  FileSearch,
  FileText,
  Filter,
  Paperclip,
  Search,
  X,
} from 'lucide-react';
import { MOCK_AUDIT_LOGS } from '../../../services/mock/mockAuditLogs.js';
import { MOCK_FIELD_REPORTS } from '../../../services/mock/mockFieldReports.js';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const ACTIVE_PROJECT = MOCK_PROJECTS[0];
const PAGE_SIZE = 5;

const APPROVED_RECORDS = MOCK_AUDIT_LOGS.filter((log) => ['PLANNER_APPROVED', 'DB_COMMITTED', 'PLANNER_OVERRIDDEN'].includes(log.action)).map((log, index) => ({
  id: log.id,
  activityId: log.activityCode,
  activity: log.activityName,
  wbs: `Metro Package 4 > ${index % 2 ? 'Superstructure' : 'Substructure'}`,
  discipline: index % 2 ? 'Structural' : 'Civil',
  fieldReport: log.sourceDocument,
  reportedProgress: log.newProgress,
  actualStart: index === 0 ? '02 Sep 2026' : '03 Sep 2026',
  actualFinish: index === 2 ? '04 Sep 2026' : 'In progress',
  approvedBy: log.actor,
  approvedAt: log.timestamp,
  evidenceLocation: log.sourceRefLocation,
  details: log.details,
  sourceType: log.sourceDocument.endsWith('.xlsx') ? 'EXCEL' : log.sourceDocument.endsWith('.wav') ? 'VOICE_MEMO' : 'DSR_PDF',
}));

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function ProgressBar({ value }) {
  return <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#FA5A16]" style={{ width: `${Math.min(value, 100)}%` }} /></div>;
}

function InfoCard({ label, value, detail, tone = 'orange' }) {
  const valueClass = tone === 'green' ? 'text-emerald-600' : 'text-slate-900';
  return <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">{label}</p><p className={`mt-2 text-2xl font-bold ${valueClass}`}>{value}</p><p className="mt-1 text-[11px] text-slate-400">{detail}</p></div>;
}

export default function TraceabilityPage() {
  const [query, setQuery] = useState('');
  const [date, setDate] = useState('All dates');
  const [discipline, setDiscipline] = useState('All disciplines');
  const [wbs, setWbs] = useState('All WBS');
  const [status, setStatus] = useState('Approved');
  const [selectedId, setSelectedId] = useState(APPROVED_RECORDS[0]?.id);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const projectLabel = Array.from(document.querySelector('main')?.querySelectorAll('div') || []).find((node) => node.textContent?.trim() === ACTIVE_PROJECT.code);
    if (projectLabel?.parentElement) projectLabel.parentElement.style.display = 'none';
  }, []);

  const filteredRecords = useMemo(() => APPROVED_RECORDS.filter((record) => {
    const normalized = query.toLowerCase().trim();
    const matchesQuery = !normalized || [record.id, record.activityId, record.activity, record.wbs, record.fieldReport].some((value) => value.toLowerCase().includes(normalized));
    const matchesDate = date === 'All dates' || record.approvedAt.startsWith('2026-09');
    const matchesDiscipline = discipline === 'All disciplines' || record.discipline === discipline;
    const matchesWbs = wbs === 'All WBS' || record.wbs.includes(wbs);
    return matchesQuery && matchesDate && matchesDiscipline && matchesWbs && status === 'Approved';
  }), [query, date, discipline, wbs, status]);

  const totalPages = Math.max(1, Math.ceil(filteredRecords.length / PAGE_SIZE));
  const visibleRecords = filteredRecords.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const selectedRecord = filteredRecords.find((record) => record.id === selectedId) || filteredRecords[0];
  const evidenceTotal = MOCK_FIELD_REPORTS.reduce((total, report) => total + report.evidenceCount, 0);

  const clearFilters = () => {
    setQuery('');
    setDate('All dates');
    setDiscipline('All disciplines');
    setWbs('All WBS');
    setStatus('Approved');
    setPage(1);
  };

  const exportRegister = () => {
    const csv = [['Activity ID', 'Activity', 'WBS', 'Discipline', 'Field Report', 'Reported Progress', 'Actual Start', 'Actual Finish', 'Approved By'], ...filteredRecords.map((record) => [record.activityId, record.activity, record.wbs, record.discipline, record.fieldReport, `${record.reportedProgress}%`, record.actualStart, record.actualFinish, record.approvedBy])].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    link.download = `${ACTIVE_PROJECT.code}-approved-activities.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"><span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />NIYOGEN / PLANNING & CONTROLS / APPROVED ACTIVITIES</div><h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">Approved Activities</h1><p className="mt-1 text-sm text-slate-500">Activities and AI matches that have been reviewed and approved by the Planner.</p></div><div className="flex flex-wrap items-center gap-2"><div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700"><CalendarDays className="h-3.5 w-3.5 text-[#FA5A16]" />{ACTIVE_PROJECT.code}<ChevronDown className="h-3.5 w-3.5 text-slate-400" /></div><div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><p className="text-[10px] uppercase tracking-wider text-slate-400">Approved ledger</p><p className="mt-0.5 font-semibold text-emerald-600">Synced · 08 Sep 2026</p></div><button onClick={exportRegister} className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2 text-xs font-bold text-white hover:bg-[#E44E0E]"><Download className="h-3.5 w-3.5" />Export register</button></div></div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3"><InfoCard label="Total Approved" value={APPROVED_RECORDS.length} detail="Approved project records" /><InfoCard label="Approved Today" value="4" detail="Planner actions today" tone="green" /><InfoCard label="This Week" value="18" detail="Approved since Monday" tone="green" /></div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-900"><Filter className="h-4 w-4 text-[#FA5A16]" /> Filter approved register</div><div className="grid grid-cols-1 gap-2.5 md:grid-cols-2 xl:grid-cols-[minmax(260px,1.8fr)_repeat(4,minmax(145px,1fr))_auto]"><div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Search Activity ID, WBS, field report" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs outline-none focus:border-[#FA5A16] focus:bg-white" /></div><select value={date} onChange={(event) => { setDate(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All dates</option><option>Current month</option></select><select value={discipline} onChange={(event) => { setDiscipline(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All disciplines</option><option>Civil</option><option>Structural</option></select><select value={wbs} onChange={(event) => { setWbs(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All WBS</option><option>Substructure</option><option>Superstructure</option></select><select value={status} onChange={(event) => setStatus(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>Approved</option></select><button onClick={clearFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 hover:bg-slate-100"><X className="h-3.5 w-3.5" />Clear Filters</button></div></div>

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"><div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="text-sm font-bold tracking-wide text-slate-900">APPROVED REGISTER</h2><p className="mt-1 text-xs text-slate-500">Verified activity updates committed to the project ledger</p></div><span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600"><CheckCircle2 className="h-4 w-4" />Approved ledger active</span></div><div className="overflow-x-auto"><table className="w-full min-w-[1100px] text-left text-xs"><thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="px-4 py-3 font-bold">Activity</th><th className="px-4 py-3 font-bold">WBS</th><th className="px-4 py-3 font-bold">Discipline</th><th className="px-4 py-3 font-bold">Field Report</th><th className="px-4 py-3 font-bold">Reported Progress</th><th className="px-4 py-3 font-bold">Actual Start</th><th className="px-4 py-3 font-bold">Actual Finish</th><th className="px-4 py-3 font-bold">Approved By</th></tr></thead><tbody className="divide-y divide-slate-100">{visibleRecords.map((record) => <tr key={record.id} onClick={() => setSelectedId(record.id)} className={`cursor-pointer transition ${selectedRecord?.id === record.id ? 'bg-orange-50/70' : 'hover:bg-slate-50'}`}><td className="px-4 py-3"><p className="font-mono text-[10px] font-bold text-[#FA5A16]">{record.activityId}</p><p className="mt-1 max-w-[230px] truncate font-semibold text-slate-800">{record.activity}</p></td><td className="max-w-[180px] truncate px-4 py-3 text-slate-500">{record.wbs}</td><td className="px-4 py-3 text-slate-600">{record.discipline}</td><td className="max-w-[220px] truncate px-4 py-3 text-slate-600"><span className="inline-flex items-center gap-1.5"><FileText className="h-3.5 w-3.5 text-[#FA5A16]" />{record.fieldReport}</span></td><td className="w-36 px-4 py-3"><div className="mb-1 flex items-center justify-between text-[10px] font-bold text-slate-700"><span>{record.reportedProgress}%</span><span className="rounded-full bg-emerald-50 px-1.5 py-0.5 text-emerald-700">Approved</span></div><ProgressBar value={record.reportedProgress} /></td><td className="whitespace-nowrap px-4 py-3 text-slate-600">{record.actualStart}</td><td className="whitespace-nowrap px-4 py-3 text-slate-600">{record.actualFinish}</td><td className="max-w-[190px] truncate px-4 py-3 font-semibold text-slate-700">{record.approvedBy}</td></tr>)}</tbody></table></div><div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-3 text-xs sm:flex-row sm:items-center sm:justify-between"><span className="text-slate-500">Showing {filteredRecords.length ? (page - 1) * PAGE_SIZE + 1 : 0}-{Math.min(page * PAGE_SIZE, filteredRecords.length)} of {filteredRecords.length} approved records</span><div className="flex items-center gap-1">{Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => <button key={number} onClick={() => setPage(number)} className={`h-7 min-w-7 rounded-md px-2 font-bold ${page === number ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-100'}`}>{number}</button>)}</div></div></section>

        {selectedRecord && <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><div className="flex items-center gap-2"><span className="rounded-md bg-orange-50 px-2 py-1 font-mono text-[10px] font-bold text-[#FA5A16]">{selectedRecord.activityId}</span><span className="rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold text-emerald-700">APPROVED</span></div><h2 className="mt-2 text-base font-bold text-slate-900">Approved Activity Trace</h2><p className="mt-1 text-xs text-slate-500">{selectedRecord.activity}</p></div><div className="text-right text-xs"><p className="text-slate-400">Approved by</p><p className="mt-1 font-semibold text-slate-700">{selectedRecord.approvedBy}</p><p className="mt-1 text-slate-400">{formatDate(selectedRecord.approvedAt)}</p></div></div><div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Source document</p><p className="mt-1 truncate text-xs font-semibold text-slate-700">{selectedRecord.fieldReport}</p><p className="mt-1 text-[11px] text-slate-500">{selectedRecord.evidenceLocation}</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Evidence coverage</p><p className="mt-1 text-lg font-bold text-[#FA5A16]">{evidenceTotal} files</p><p className="mt-1 text-[11px] text-slate-500">Across current field reports</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Approval detail</p><p className="mt-1 text-xs leading-relaxed text-slate-600">{selectedRecord.details}</p></div></div><div className="mt-4 flex items-center gap-2 text-xs font-semibold text-[#FA5A16]"><Paperclip className="h-4 w-4" />Trace source document and approved project update</div></section>}
      </div>
    </div>
  );
}
