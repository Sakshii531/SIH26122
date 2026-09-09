'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  Download,
  FileText,
  Filter,
  Flag,
  List,
  MessageSquare,
  Paperclip,
  Search,
  ShieldAlert,
  SlidersHorizontal,
  UploadCloud,
  X,
} from 'lucide-react';
import { verificationService } from '../../../services/verificationService.js';
import { MOCK_FIELD_REPORTS } from '../../../services/mock/mockFieldReports.js';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const ACTIVE_PROJECT = MOCK_PROJECTS[0];

function priorityFor(item) {
  if (item.primaryMatch.totalConfidenceScore < 65) return 'High';
  if (item.primaryMatch.totalConfidenceScore < 85) return 'Medium';
  return 'Low';
}

function priorityClass(priority) {
  return priority === 'High' ? 'border-rose-200 bg-rose-50 text-rose-700' : priority === 'Medium' ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-slate-200 bg-slate-100 text-slate-600';
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function ProgressBar({ value, muted = false }) {
  return <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full ${muted ? 'bg-slate-400' : 'bg-[#FA5A16]'}`} style={{ width: `${Math.min(value, 100)}%` }} /></div>;
}

export default function VerificationPage() {
  const [items, setItems] = useState([]);
  const [resolvedItems, setResolvedItems] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [activeTab, setActiveTab] = useState('open');
  const [query, setQuery] = useState('');
  const [conflictType, setConflictType] = useState('All conflict types');
  const [activity, setActivity] = useState('All activities');
  const [priority, setPriority] = useState('All priorities');
  const [sort, setSort] = useState('Priority');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    const projectLabel = Array.from(document.querySelector('main')?.querySelectorAll('div') || []).find((node) => node.textContent?.trim() === ACTIVE_PROJECT.code);
    if (projectLabel?.parentElement) projectLabel.parentElement.style.display = 'none';
  }, []);

  const fetchQueue = async () => {
    const list = await verificationService.getPendingQueue('ALL');
    setItems(list);
    setSelectedId((current) => current || list[0]?.id || null);
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const filteredItems = useMemo(() => {
    const source = activeTab === 'open' ? items : resolvedItems;
    const normalizedQuery = query.toLowerCase().trim();
    const result = source.filter((item) => {
      const type = item.extractedEvent.sourceType === 'VOICE_MEMO' ? 'Progress' : item.extractedEvent.sourceType === 'EXCEL' ? 'Quantity' : 'Schedule';
      const matchesQuery = !normalizedQuery || [item.id, item.primaryMatch.l6ActivityName, item.primaryMatch.l6ActivityCode, item.primaryMatch.wbsPath].some((value) => value?.toLowerCase().includes(normalizedQuery));
      const matchesType = conflictType === 'All conflict types' || type === conflictType;
      const matchesActivity = activity === 'All activities' || item.primaryMatch.l6ActivityCode === activity;
      const matchesPriority = priority === 'All priorities' || priorityFor(item) === priority;
      return matchesQuery && matchesType && matchesActivity && matchesPriority;
    });
    return result.sort((a, b) => sort === 'Confidence' ? a.primaryMatch.totalConfidenceScore - b.primaryMatch.totalConfidenceScore : priorityFor(a).localeCompare(priorityFor(b)));
  }, [activeTab, items, resolvedItems, query, conflictType, activity, priority, sort]);

  const selectedItem = filteredItems.find((item) => item.id === selectedId) || filteredItems[0];
  const openCount = items.length;
  const highPriority = items.filter((item) => priorityFor(item) === 'High').length;
  const relatedReports = MOCK_FIELD_REPORTS.slice(0, 3);

  const markResolved = async (action) => {
    if (!selectedItem) return;
    if (action === 'approve') await verificationService.approveMatch(selectedItem.id);
    if (action === 'reject') await verificationService.rejectMatch(selectedItem.id, notes || 'Conflict rejected by planner');
    if (action === 'override') await verificationService.overrideMatch(selectedItem.id, { notes: notes || 'Conflict resolved with planner review' });
    setResolvedItems((current) => [...current, { ...selectedItem, approvalStatus: action === 'approve' ? 'APPROVED' : action === 'reject' ? 'REJECTED' : 'OVERRIDDEN' }]);
    setNotes('');
    await fetchQueue();
  };

  const clearFilters = () => {
    setQuery('');
    setConflictType('All conflict types');
    setActivity('All activities');
    setPriority('All priorities');
    setSort('Priority');
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"><span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />NIYOGEN / CONFLICT CENTER</div><h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">CONFLICT CENTER</h1><p className="mt-1 text-sm text-slate-500">Review and resolve conflicts and discrepancies across field reports and project data.</p></div><div className="flex flex-wrap items-center gap-2"><div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700"><CalendarDays className="h-3.5 w-3.5 text-[#FA5A16]" />{ACTIVE_PROJECT.code}<ChevronDown className="h-3.5 w-3.5 text-slate-400" /></div><div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><p className="text-[10px] uppercase tracking-wider text-slate-400">Last updated</p><p className="mt-0.5 font-semibold text-slate-700">08 Sep 2026, 18:02</p></div><span className="inline-flex items-center gap-1.5 rounded-full border border-orange-200 bg-orange-50 px-3 py-2 text-xs font-bold text-[#FA5A16]"><AlertTriangle className="h-3.5 w-3.5" />{openCount} open conflicts</span></div></div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-5"><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Open Conflicts</p><p className="mt-2 text-2xl font-bold text-slate-900">{openCount}</p><p className="mt-1 text-[11px] text-slate-400">Awaiting resolution</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">High Priority</p><p className="mt-2 text-2xl font-bold text-rose-600">{highPriority}</p><p className="mt-1 text-[11px] text-slate-400">Needs immediate action</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Under Review</p><p className="mt-2 text-2xl font-bold text-amber-600">{openCount}</p><p className="mt-1 text-[11px] text-slate-400">Planner queue</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Resolved Week</p><p className="mt-2 text-2xl font-bold text-slate-900">12</p><p className="mt-1 text-[11px] text-slate-400">This reporting week</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Resolution Rate</p><p className="mt-2 text-2xl font-bold text-[#FA5A16]">84%</p><p className="mt-1 text-[11px] text-slate-400">Weekly average</p></div></div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm"><button onClick={() => setActiveTab('open')} className={`rounded-md px-3 py-2 text-xs font-bold ${activeTab === 'open' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}>Open Conflicts ({items.length})</button><button onClick={() => setActiveTab('resolved')} className={`rounded-md px-3 py-2 text-xs font-bold ${activeTab === 'resolved' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}>Resolved Conflicts ({resolvedItems.length})</button></div><div className="flex items-center gap-2"><button className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]"><Download className="h-3.5 w-3.5" />Export Log</button><button onClick={fetchQueue} className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2 text-xs font-bold text-white hover:bg-[#E44E0E]"><ArrowRight className="h-3.5 w-3.5" />Sync Field Reports</button></div></div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="grid grid-cols-1 gap-2.5 md:grid-cols-2 xl:grid-cols-[minmax(260px,1.8fr)_repeat(4,minmax(140px,1fr))_auto]"><div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search conflicts by ID, activity, or WBS" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs outline-none focus:border-[#FA5A16] focus:bg-white" /></div><select value={conflictType} onChange={(event) => setConflictType(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All conflict types</option><option>Progress</option><option>Quantity</option><option>Discipline</option><option>Schedule</option></select><select value={activity} onChange={(event) => setActivity(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All activities</option>{items.map((item) => <option key={item.id} value={item.primaryMatch.l6ActivityCode}>{item.primaryMatch.l6ActivityCode}</option>)}</select><select value={priority} onChange={(event) => setPriority(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All priorities</option><option>High</option><option>Medium</option><option>Low</option></select><select value={sort} onChange={(event) => setSort(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>Priority</option><option>Confidence</option></select><button onClick={clearFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 hover:bg-slate-100"><X className="h-3.5 w-3.5" />Clear</button></div><div className="mt-3 flex flex-wrap gap-2"><span className="text-[11px] font-semibold text-slate-400">Filter by type:</span>{['All', 'Progress', 'Quantity', 'Discipline', 'Schedule'].map((type) => <button key={type} onClick={() => setConflictType(type === 'All' ? 'All conflict types' : type)} className={`rounded-full border px-3 py-1 text-[11px] font-semibold ${conflictType === (type === 'All' ? 'All conflict types' : type) ? 'border-[#FA5A16] bg-orange-50 text-[#FA5A16]' : 'border-slate-200 bg-white text-slate-500 hover:border-orange-200'}`}>{type}</button>)}</div></div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,0.82fr)_minmax(0,1.5fr)]"><section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="mb-4 flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">CONFLICT WORKSPACE</h2><p className="mt-1 text-xs text-slate-500">Select a conflict to review</p></div><SlidersHorizontal className="h-4 w-4 text-[#FA5A16]" /></div><div className="space-y-2">{filteredItems.map((item) => <button key={item.id} onClick={() => setSelectedId(item.id)} className={`w-full rounded-lg border p-3 text-left transition ${selectedItem?.id === item.id ? 'border-[#FA5A16] bg-orange-50/70' : 'border-slate-200 hover:border-orange-200 hover:bg-orange-50/30'}`}><div className="flex items-center justify-between gap-2"><span className="font-mono text-[10px] font-bold text-[#FA5A16]">{item.id}</span><span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold ${priorityClass(priorityFor(item))}`}>{priorityFor(item)} priority</span></div><p className="mt-2 text-xs font-bold text-slate-800">{item.primaryMatch.l6ActivityName}</p><p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-slate-500">{item.primaryMatch.matchingRationale}</p><div className="mt-2 flex items-center justify-between text-[10px] text-slate-400"><span>{formatDate(item.extractedEvent.timestamp)}</span><span className="inline-flex items-center gap-1"><Paperclip className="h-3 w-3" />{item.extractedEvent.equipmentUsed?.length || 0} documents</span></div></button>)}</div>{filteredItems.length === 0 && <p className="py-10 text-center text-xs text-slate-500">No conflicts match the current filters.</p>}</section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">{selectedItem ? <><div className="flex flex-col gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-start sm:justify-between"><div><div className="flex flex-wrap items-center gap-2"><span className="rounded-md bg-orange-50 px-2 py-1 font-mono text-[10px] font-bold text-[#FA5A16]">{selectedItem.id}</span><span className={`rounded-full border px-2 py-1 text-[10px] font-bold ${priorityClass(priorityFor(selectedItem))}`}>{priorityFor(selectedItem)} priority</span><span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-[10px] font-bold text-amber-700">{activeTab === 'open' ? 'OPEN' : selectedItem.approvalStatus}</span></div><h2 className="mt-2 text-base font-bold text-slate-900">Conflict Details</h2></div><span className="text-xs font-semibold text-slate-500">{selectedItem.primaryMatch.totalConfidenceScore}% match confidence</span></div><div className="grid grid-cols-1 gap-3 pt-4 md:grid-cols-2"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Conflict type</p><p className="mt-1 text-sm font-bold text-slate-800">{selectedItem.extractedEvent.sourceType === 'VOICE_MEMO' ? 'Progress discrepancy' : selectedItem.extractedEvent.sourceType === 'EXCEL' ? 'Quantity discrepancy' : 'Schedule discrepancy'}</p><p className="mt-2 text-[11px] text-slate-500">Affected activity: {selectedItem.primaryMatch.l6ActivityCode}</p><p className="mt-1 text-[11px] text-slate-500">{selectedItem.primaryMatch.wbsPath}</p></div><div className="rounded-lg border border-orange-200 bg-orange-50/50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-[#FA5A16]">Suggested action</p><p className="mt-1 text-xs font-bold text-slate-800">Review and confirm the suggested project activity match.</p><p className="mt-2 text-[11px] text-slate-600">{selectedItem.primaryMatch.matchingRationale}</p></div></div><div className="mt-4"><h3 className="text-xs font-bold text-slate-900">Field Report vs Existing Project Data</h3><div className="mt-2 grid grid-cols-1 gap-3 md:grid-cols-2"><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Reported progress / status</p><p className="mt-2 text-lg font-bold text-[#FA5A16]">{selectedItem.extractedEvent.quantity} {selectedItem.extractedEvent.unit}</p><p className="mt-1 line-clamp-3 text-[11px] text-slate-500">{selectedItem.extractedEvent.rawText}</p></div><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Baseline progress / status</p><p className="mt-2 text-lg font-bold text-slate-800">{selectedItem.primaryMatch.totalConfidenceScore}% match</p><p className="mt-1 text-[11px] text-slate-500">{selectedItem.primaryMatch.l6ActivityName}</p></div></div></div><div className="mt-4 flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" /><div><p className="text-xs font-bold text-amber-800">Clear discrepancy detected</p><p className="mt-1 text-[11px] leading-relaxed text-amber-700">{selectedItem.primaryMatch.matchingRationale}</p></div></div><div className="mt-4"><h3 className="flex items-center gap-2 text-xs font-bold text-slate-900"><Paperclip className="h-4 w-4 text-[#FA5A16]" />Supporting evidence</h3><div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] font-bold text-slate-400">SOURCE DOCUMENT</p><p className="mt-1 truncate text-xs font-semibold text-slate-700">{selectedItem.extractedEvent.sourceFileName}</p><p className="mt-1 text-[10px] text-slate-500">{selectedItem.extractedEvent.sourceRefLocation}</p></div>{relatedReports.slice(0, 1).map((report) => <div key={report.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] font-bold text-slate-400">FIELD ATTACHMENT</p><p className="mt-1 text-xs font-semibold text-slate-700">{report.evidenceCount} files from {report.id}</p><p className="mt-1 text-[10px] text-slate-500">{report.activity}</p></div>)}</div></div><div className="mt-5 border-t border-slate-100 pt-4"><h3 className="flex items-center gap-2 text-xs font-bold text-slate-900"><MessageSquare className="h-4 w-4 text-[#FA5A16]" />Conflict resolution</h3><p className="mt-1 text-[11px] text-slate-500">Add a planner note before resolving this conflict.</p><textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} placeholder="Comments / notes" className="mt-3 w-full rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs outline-none focus:border-[#FA5A16] focus:bg-white" /><div className="mt-3 flex flex-wrap gap-2"><button className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:border-[#FA5A16] hover:text-[#FA5A16]"><UploadCloud className="h-3.5 w-3.5" />Attach Evidence</button><button onClick={() => markResolved('override')} className="inline-flex items-center gap-1.5 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700"><ShieldAlert className="h-3.5 w-3.5" />Save Override</button><button onClick={() => markResolved('approve')} className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2 text-xs font-bold text-white hover:bg-[#E44E0E]"><CheckCircle2 className="h-3.5 w-3.5" />Resolve Conflict</button></div></div></> : <div className="py-16 text-center text-xs text-slate-500">Select an open conflict to inspect.</div>}</section></div>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="mb-4 flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">RECENT CONFLICTS</h2><p className="mt-1 text-xs text-slate-500">Latest discrepancies and their current resolution status</p></div><button className="text-xs font-bold text-[#FA5A16]">View All</button></div><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-xs"><thead className="border-b border-slate-100 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="pb-2">ID</th><th className="pb-2">Type</th><th className="pb-2">Affected Activity</th><th className="pb-2">Discipline</th><th className="pb-2">Priority</th><th className="pb-2">Status</th><th className="pb-2">Date</th><th className="pb-2 text-right">Actions</th></tr></thead><tbody className="divide-y divide-slate-100">{[...items, ...resolvedItems].slice(0, 6).map((item) => <tr key={`${item.id}-${item.approvalStatus}`}><td className="py-3 font-mono font-bold text-[#FA5A16]">{item.id}</td><td className="py-3 text-slate-500">{item.extractedEvent.sourceType}</td><td className="max-w-[260px] truncate py-3 font-semibold text-slate-700">{item.primaryMatch.l6ActivityName}</td><td className="py-3 text-slate-500">Planning</td><td className="py-3"><span className={`rounded-full border px-2 py-1 text-[10px] font-bold ${priorityClass(priorityFor(item))}`}>{priorityFor(item)}</span></td><td className="py-3 text-slate-500">{item.approvalStatus === 'PENDING_VERIFICATION' ? 'Open' : item.approvalStatus}</td><td className="whitespace-nowrap py-3 text-slate-500">{formatDate(item.extractedEvent.timestamp)}</td><td className="py-3 text-right"><button onClick={() => { setSelectedId(item.id); setActiveTab(item.approvalStatus === 'PENDING_VERIFICATION' ? 'open' : 'resolved'); }} className="font-semibold text-[#FA5A16] hover:underline">View</button></td></tr>)}</tbody></table></div></section>
      </div>
    </div>
  );
}
