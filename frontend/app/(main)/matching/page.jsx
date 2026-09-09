'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  FileText,
  Filter,
  Flag,
  Layers,
  List,
  Paperclip,
  Search,
  ShieldAlert,
  Sparkles,
  Target,
  UserRound,
  X,
} from 'lucide-react';
import { aiService } from '../../../services/aiService.js';
import { MOCK_FIELD_REPORTS } from '../../../services/mock/mockFieldReports.js';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const ACTIVE_PROJECT = MOCK_PROJECTS[0];

function confidenceTone(score) {
  if (score >= 85) return 'border-orange-200 bg-orange-50 text-[#FA5A16]';
  if (score >= 65) return 'border-amber-200 bg-amber-50 text-amber-700';
  return 'border-rose-200 bg-rose-50 text-rose-700';
}

function priorityLabel(score) {
  if (score < 65) return 'High priority';
  if (score < 85) return 'Review';
  return 'Standard';
}

function StatCard({ label, value, detail, icon: Icon, tone = 'orange' }) {
  const iconStyle = {
    orange: 'bg-orange-50 text-[#FA5A16]',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
    slate: 'bg-slate-100 text-slate-600',
    green: 'bg-emerald-50 text-emerald-600',
  };
  return <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="flex items-start justify-between"><div><p className="text-xs font-semibold text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold text-slate-900">{value}</p><p className="mt-1 text-[11px] text-slate-400">{detail}</p></div><span className={`flex h-8 w-8 items-center justify-center rounded-lg ${iconStyle[tone]}`}><Icon className="h-4 w-4" /></span></div></div>;
}

function ProgressBar({ value }) {
  return <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#FA5A16]" style={{ width: `${Math.min(value, 100)}%` }} /></div>;
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function MatchingPage() {
  const [items, setItems] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [query, setQuery] = useState('');
  const [discipline, setDiscipline] = useState('All disciplines');
  const [status, setStatus] = useState('Requires review');
  const [role, setRole] = useState('All roles');
  const [scheduleRange, setScheduleRange] = useState('Full schedule range');
  const [view, setView] = useState('list');

  useEffect(() => {
    aiService.getAllExtractedMatches().then(setItems);
  }, []);

  useEffect(() => {
    const projectLabel = Array.from(document.querySelector('main')?.querySelectorAll('div') || []).find((node) => node.textContent?.trim() === ACTIVE_PROJECT.code);
    if (projectLabel?.parentElement) projectLabel.parentElement.style.display = 'none';
  }, []);

  const filteredItems = useMemo(() => items.filter((item) => {
    const search = query.trim().toLowerCase();
    const matchesQuery = !search || [item.id, item.primaryMatch.l6ActivityCode, item.primaryMatch.l6ActivityName, item.extractedEvent.extractedActivity, item.primaryMatch.wbsPath].some((value) => value?.toLowerCase().includes(search));
    const matchesDiscipline = discipline === 'All disciplines' || item.primaryMatch.l6ActivityName.toLowerCase().includes(discipline.toLowerCase());
    const matchesStatus = status === 'All statuses' || (status === 'Requires review' && item.approvalStatus === 'PENDING_VERIFICATION') || (status === 'Low confidence' && item.primaryMatch.totalConfidenceScore < 65) || (status === 'Ambiguous' && item.alternateCandidates.length > 0);
    const matchesRole = role === 'All roles' || (role === 'Civil' && item.extractedEvent.rawText.toLowerCase().includes('concrete')) || (role === 'Structural' && item.extractedEvent.rawText.toLowerCase().includes('segment'));
    const matchesRange = scheduleRange === 'Full schedule range' || item.extractedEvent.extractedStart.startsWith('2026-09');
    return matchesQuery && matchesDiscipline && matchesStatus && matchesRole && matchesRange;
  }), [items, query, discipline, status, role, scheduleRange]);

  const [rejectedIds, setRejectedIds] = useState([]);
  const visibleItems = filteredItems.filter((item) => !rejectedIds.includes(item.id));
  const activeItem = visibleItems[selectedIndex] || visibleItems[0];
  const lowConfidence = items.filter((item) => item.primaryMatch.totalConfidenceScore < 65).length;
  const ambiguous = items.filter((item) => item.alternateCandidates.length > 0).length;
  const unmatched = items.filter((item) => item.primaryMatch.totalConfidenceScore < 55).length;
  const relatedReports = MOCK_FIELD_REPORTS.slice(0, 3);

  const clearFilters = () => {
    setQuery('');
    setDiscipline('All disciplines');
    setStatus('All statuses');
    setRole('All roles');
    setScheduleRange('Full schedule range');
  };

  const rejectSelectedMatch = () => {
    if (!activeItem) return;
    setRejectedIds((current) => [...current, activeItem.id]);
    setSelectedIndex(0);
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"><span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />Planning workspace / review queue</div><h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">AI MATCH REVIEW</h1><p className="mt-1 text-sm text-slate-500">Review AI activity matches, resolve discrepancies, and approve field updates.</p></div>
          <div className="flex flex-wrap items-center gap-2"><div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><CalendarDays className="h-3.5 w-3.5 text-[#FA5A16]" /><span className="font-semibold text-slate-700">{ACTIVE_PROJECT.code}</span><ChevronDown className="h-3.5 w-3.5 text-slate-400" /></div><div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><p className="text-[10px] uppercase tracking-wider text-slate-400">Last updated</p><p className="mt-0.5 font-semibold text-slate-700">08 Sep 2026, 18:02</p></div><span className="inline-flex items-center gap-1.5 rounded-full border border-orange-200 bg-orange-50 px-3 py-2 text-xs font-bold text-[#FA5A16]"><AlertTriangle className="h-3.5 w-3.5" />{items.length} matches require review</span></div>
        </div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-5"><StatCard label="Requires Review" value={items.length} detail="Pending planner action" icon={Flag} /><StatCard label="Low Confidence" value={lowConfidence} detail="Below 65% confidence" icon={ShieldAlert} tone="rose" /><StatCard label="Ambiguous" value={ambiguous} detail="Alternate matches found" icon={Layers} tone="amber" /><StatCard label="Unmatched" value={unmatched} detail="Needs manual mapping" icon={X} tone="slate" /><StatCard label="Approved Today" value="12" detail="Committed to schedule" icon={CheckCircle2} tone="green" /></div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-900"><Filter className="h-4 w-4 text-[#FA5A16]" /> Filter match queue</div><div className="grid grid-cols-1 gap-2.5 md:grid-cols-2 xl:grid-cols-[minmax(250px,1.8fr)_repeat(4,minmax(140px,1fr))_auto]"><div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search match ID, activity or WBS" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs outline-none focus:border-[#FA5A16] focus:bg-white" /></div><select value={discipline} onChange={(event) => setDiscipline(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All disciplines</option><option>Civil</option><option>Structural</option><option>Mechanical</option></select><select value={status} onChange={(event) => setStatus(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>Requires review</option><option>All statuses</option><option>Low confidence</option><option>Ambiguous</option></select><select value={role} onChange={(event) => setRole(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All roles</option><option>Civil</option><option>Structural</option></select><select value={scheduleRange} onChange={(event) => setScheduleRange(event.target.value)} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>Full schedule range</option><option>Current schedule window</option></select><button onClick={clearFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 hover:bg-slate-100"><X className="h-3.5 w-3.5" />Clear</button></div></div>

        <div className="flex items-center justify-between"><div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm"><button onClick={() => setView('list')} className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-bold ${view === 'list' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}><List className="h-3.5 w-3.5" />List View</button><button onClick={() => setView('gantt')} className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-bold ${view === 'gantt' ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-50'}`}><BarChart3 className="h-3.5 w-3.5" />Gantt View</button></div><span className="text-xs text-slate-400">{filteredItems.length} results</span></div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.45fr)]">
          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="mb-3 flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">MATCH QUEUE</h2><p className="mt-1 text-xs text-slate-500">Select a match to inspect and resolve</p></div><Sparkles className="h-4 w-4 text-[#FA5A16]" /></div>{view === 'list' ? <div className="space-y-2">{filteredItems.map((item, index) => <button key={item.id} onClick={() => setSelectedIndex(index)} className={`w-full rounded-lg border p-3 text-left transition ${activeItem?.id === item.id ? 'border-[#FA5A16] bg-orange-50/70' : 'border-slate-200 bg-white hover:border-orange-200 hover:bg-orange-50/30'}`}><div className="flex items-center justify-between gap-2"><span className="font-mono text-[10px] font-bold text-[#FA5A16]">{item.id}</span><span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold ${confidenceTone(item.primaryMatch.totalConfidenceScore)}`}>{item.primaryMatch.totalConfidenceScore}%</span></div><div className="mt-2 flex items-center gap-2"><span className="rounded bg-amber-50 px-1.5 py-0.5 text-[9px] font-bold uppercase text-amber-700">{priorityLabel(item.primaryMatch.totalConfidenceScore)}</span><span className="text-[10px] text-slate-400">{item.extractedEvent.sourceType}</span></div><p className="mt-2 line-clamp-2 text-xs font-bold text-slate-800">{item.primaryMatch.l6ActivityName}</p><p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-slate-500">{item.primaryMatch.matchingRationale}</p><div className="mt-2 flex items-center justify-between text-[10px] text-slate-400"><span>{formatDate(item.extractedEvent.timestamp)}</span><span className="inline-flex items-center gap-1"><Paperclip className="h-3 w-3" />{item.extractedEvent.equipmentUsed?.length || 0} docs</span></div></button>)}</div> : <div className="space-y-3">{filteredItems.map((item, index) => <button key={item.id} onClick={() => setSelectedIndex(index)} className="flex w-full items-center gap-3 rounded-lg border border-slate-200 p-3 text-left hover:border-orange-200"><span className="w-28 shrink-0 font-mono text-[10px] font-bold text-[#FA5A16]">{item.primaryMatch.l6ActivityCode}</span><div className="min-w-0 flex-1"><p className="truncate text-xs font-bold text-slate-800">{item.primaryMatch.l6ActivityName}</p><div className="mt-2 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#FA5A16]" style={{ width: `${item.primaryMatch.totalConfidenceScore}%` }} /></div></div><span className="text-xs font-bold text-slate-600">{item.primaryMatch.totalConfidenceScore}%</span></button>)}</div>}</section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">{activeItem ? <><div className="flex flex-col gap-3 border-b border-slate-100 pb-4 sm:flex-row sm:items-start sm:justify-between"><div><div className="flex flex-wrap items-center gap-2"><span className="rounded-md bg-orange-50 px-2 py-1 font-mono text-[10px] font-bold text-[#FA5A16]">{activeItem.id}</span><span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-[10px] font-bold text-amber-700">PENDING REVIEW</span></div><h2 className="mt-2 text-base font-bold text-slate-900">Selected Match Details</h2><p className="mt-1 text-xs text-slate-500">{activeItem.primaryMatch.l6ActivityName}</p></div><span className={`rounded-full border px-3 py-1.5 text-xs font-bold ${confidenceTone(activeItem.primaryMatch.totalConfidenceScore)}`}>{activeItem.primaryMatch.totalConfidenceScore}% confidence</span></div><div className="grid grid-cols-1 gap-3 pt-4 md:grid-cols-2"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Field report</p><p className="mt-1 text-xs font-bold text-slate-800">{activeItem.extractedEvent.extractedActivity}</p><p className="mt-2 text-[11px] text-slate-500">{activeItem.extractedEvent.quantity} {activeItem.extractedEvent.unit} · {activeItem.extractedEvent.workforceCount} workers</p><p className="mt-2 line-clamp-3 text-[11px] leading-relaxed text-slate-600">{activeItem.extractedEvent.rawText}</p></div><div className="rounded-lg border border-orange-200 bg-orange-50/50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-[#FA5A16]">Existing project data</p><p className="mt-1 text-xs font-bold text-slate-800">{activeItem.primaryMatch.l6ActivityName}</p><p className="mt-2 text-[11px] text-slate-500">{activeItem.primaryMatch.l6ActivityCode} · {activeItem.primaryMatch.wbsPath}</p><p className="mt-2 text-[11px] leading-relaxed text-slate-600">Matched from schedule context and semantic similarity.</p></div></div><div className="mt-4 flex gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" /><div><p className="text-xs font-bold text-amber-800">Review discrepancy</p><p className="mt-1 text-[11px] leading-relaxed text-amber-700">{activeItem.primaryMatch.matchingRationale}</p></div></div><div className="mt-4 grid grid-cols-2 gap-3 text-xs"><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Evidence / attachments</p><p className="mt-1 font-bold text-slate-800">{activeItem.extractedEvent.equipmentUsed?.length || 0} documents</p><p className="mt-1 text-[11px] text-slate-500">{activeItem.extractedEvent.sourceFileName}</p></div><div className="rounded-lg border border-slate-200 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Match scores</p><p className="mt-1 font-semibold text-slate-700">Semantic {(activeItem.primaryMatch.semanticSimilarityScore * 100).toFixed(0)}% · Context {(activeItem.primaryMatch.contextualScore * 100).toFixed(0)}%</p><ProgressBar value={activeItem.primaryMatch.totalConfidenceScore} /></div></div><div className="mt-5 border-t border-slate-100 pt-4"><p className="text-xs font-bold text-slate-900">Resolution</p><p className="mt-1 text-[11px] text-slate-500">Confirm the suggested activity or open the verification queue for an override.</p><div className="mt-3 flex flex-wrap gap-2"><button className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2 text-xs font-bold text-white hover:bg-[#E44E0E]"><CheckCircle2 className="h-3.5 w-3.5" />Approve match</button><a href="#" onClick={(event) => { event.preventDefault(); rejectSelectedMatch(); }} className="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-bold text-rose-700 hover:bg-rose-100">Reject <X className="h-3.5 w-3.5" /></a></div></div></> : <div className="py-16 text-center text-xs text-slate-500">Loading AI matching engine results...</div>}</section>
        </div>

        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.25fr_0.75fr]">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="mb-4 flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">RECENT CONFLICTS</h2><p className="mt-1 text-xs text-slate-500">Latest match exceptions and review activity</p></div><Clock3 className="h-4 w-4 text-[#FA5A16]" /></div><div className="overflow-x-auto"><table className="w-full min-w-[560px] text-left text-xs"><thead className="border-b border-slate-100 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="pb-2">Match ID</th><th className="pb-2">Affected activity</th><th className="pb-2">Type</th><th className="pb-2">Confidence</th><th className="pb-2">Date</th></tr></thead><tbody className="divide-y divide-slate-100">{items.slice(0, 4).map((item) => <tr key={item.id}><td className="py-3 font-mono font-bold text-[#FA5A16]">{item.id}</td><td className="max-w-[230px] truncate py-3 font-semibold text-slate-700">{item.primaryMatch.l6ActivityName}</td><td className="py-3 text-slate-500">{item.extractedEvent.sourceType}</td><td className="py-3"><span className={`rounded-full border px-2 py-1 text-[10px] font-bold ${confidenceTone(item.primaryMatch.totalConfidenceScore)}`}>{item.primaryMatch.totalConfidenceScore}%</span></td><td className="whitespace-nowrap py-3 text-slate-500">{formatDate(item.extractedEvent.timestamp)}</td></tr>)}</tbody></table></div></section>
          <div className="space-y-5"><section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">FIELD EVIDENCE</h2><p className="mt-1 text-xs text-slate-500">Latest source material</p></div><Paperclip className="h-4 w-4 text-[#FA5A16]" /></div><p className="mt-4 text-3xl font-bold text-slate-900">{relatedReports.reduce((sum, report) => sum + report.evidenceCount, 0)}</p><p className="text-xs text-slate-500">files across recent reports</p></section><section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="text-sm font-bold text-slate-900">ACTIVITY INSIGHTS</h2><p className="mt-1 text-xs text-slate-500">AI confidence distribution</p></div><Sparkles className="h-4 w-4 text-[#FA5A16]" /></div><div className="mt-4 space-y-3"><div><div className="mb-1 flex justify-between text-[11px] text-slate-500"><span>High confidence</span><strong>{items.filter((item) => item.primaryMatch.totalConfidenceScore >= 85).length}</strong></div><ProgressBar value={items.length ? (items.filter((item) => item.primaryMatch.totalConfidenceScore >= 85).length / items.length) * 100 : 0} /></div><div><div className="mb-1 flex justify-between text-[11px] text-slate-500"><span>Needs review</span><strong>{ambiguous}</strong></div><ProgressBar value={items.length ? (ambiguous / items.length) * 100 : 0} /></div></div></section></div>
        </div>
      </div>
    </div>
  );
}
