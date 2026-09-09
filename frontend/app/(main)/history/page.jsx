'use client';

import React, { useMemo, useState } from 'react';
import {
  CheckCircle2,
  ChevronDown,
  Clock3,
  Download,
  FileKey2,
  Filter,
  History,
  Search,
  Send,
  MessageSquare,
  ShieldCheck,
  UserRound,
  X,
} from 'lucide-react';
import { MOCK_AUDIT_LOGS } from '../../../services/mock/mockAuditLogs.js';
import { MOCK_PROJECTS } from '../../../services/mock/mockProjects.js';

const ACTIVE_PROJECT = MOCK_PROJECTS[0];
const PAGE_SIZE = 5;

function actionLabel(action) {
  const labels = { PLANNER_APPROVED: 'Match Approved', PLANNER_OVERRIDDEN: 'Match Corrected', REJECTED: 'Match Rejected', SEMANTIC_MATCHED: 'Match Reviewed', DB_COMMITTED: 'Progress Updated' };
  return labels[action] || action.replaceAll('_', ' ');
}

function actionClass(action) {
  if (action === 'PLANNER_APPROVED' || action === 'DB_COMMITTED') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (action === 'REJECTED') return 'border-rose-200 bg-rose-50 text-rose-700';
  if (action === 'PLANNER_OVERRIDDEN') return 'border-amber-200 bg-amber-50 text-amber-700';
  return 'border-orange-200 bg-orange-50 text-[#FA5A16]';
}

function formatDate(value) {
  return new Date(value).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function HistoryPage() {
  const [query, setQuery] = useState('');
  const [date, setDate] = useState('All dates');
  const [user, setUser] = useState('All users');
  const [action, setAction] = useState('All actions');
  const [entity, setEntity] = useState('All entities');
  const [activity, setActivity] = useState('All activities');
  const [page, setPage] = useState(1);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);

  const filteredLogs = useMemo(() => MOCK_AUDIT_LOGS.filter((log) => {
    const normalized = query.toLowerCase().trim();
    const matchesQuery = !normalized || [log.actor, log.action, log.activityCode, log.activityName, log.details].some((value) => value?.toLowerCase().includes(normalized));
    const matchesDate = date === 'All dates' || log.timestamp.startsWith('2026-09');
    const matchesUser = user === 'All users' || log.actor.includes(user);
    const matchesAction = action === 'All actions' || log.action === action;
    const matchesEntity = entity === 'All entities' || log.activityCode === entity;
    const matchesActivity = activity === 'All activities' || log.activityName === activity;
    return matchesQuery && matchesDate && matchesUser && matchesAction && matchesEntity && matchesActivity;
  }), [query, date, user, action, entity, activity]);

  const totalPages = Math.max(1, Math.ceil(filteredLogs.length / PAGE_SIZE));
  const visibleLogs = filteredLogs.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const clearFilters = () => {
    setQuery('');
    setDate('All dates');
    setUser('All users');
    setAction('All actions');
    setEntity('All entities');
    setActivity('All activities');
    setPage(1);
  };

  const exportLogs = () => {
    const csv = [['Timestamp', 'User', 'Action', 'Entity', 'Previous', 'New Value', 'Details'], ...filteredLogs.map((log) => [log.timestamp, log.actor, actionLabel(log.action), log.activityCode, `${log.previousProgress}%`, `${log.newProgress}%`, log.details])].map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\n');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    link.download = `${ACTIVE_PROJECT.code}-audit-trail.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const answerAuditQuestion = (question) => {
    const normalized = question.toLowerCase();
    const matchedLog = MOCK_AUDIT_LOGS.find((log) => normalized.includes(log.activityCode.toLowerCase()) || normalized.includes(log.activityName.toLowerCase().split(' ')[0].toLowerCase()));
    let answer = 'I could not find a matching audit record. Try an activity name, entity ID, or action from the audit stream.';
    if (matchedLog) {
      if (normalized.includes('who')) answer = `${matchedLog.actor} recorded ${actionLabel(matchedLog.action)} for ${matchedLog.activityName}.`;
      else if (normalized.includes('when')) answer = `${matchedLog.activityName} was recorded on ${formatDate(matchedLog.timestamp)}.`;
      else if (normalized.includes('previous') || normalized.includes('value') || normalized.includes('changed')) answer = `${matchedLog.activityName} changed from ${matchedLog.previousProgress}% to ${matchedLog.newProgress}%. ${matchedLog.details}`;
      else answer = `${actionLabel(matchedLog.action)}: ${matchedLog.details}`;
    } else if (normalized.includes('who updated')) {
      answer = 'Foundation Excavation is represented in the field-report ledger; no matching audit event is currently logged.';
    }
    setChatMessages((current) => [...current, { role: 'user', text: question }, { role: 'assistant', text: answer }]);
    setChatInput('');
  };

  return (
    <div className="min-h-full bg-[#F8F9FA] px-4 py-5 text-slate-800 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px] space-y-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"><span className="h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />NIYOGEN / PLANNING & CONTROLS / AUDIT TRAIL</div><h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900">Audit Trail</h1><p className="mt-1 text-sm text-slate-500">Complete history of important project actions, decisions, and changes.</p></div><div className="flex flex-wrap items-center gap-2"><div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"><p className="text-[10px] uppercase tracking-wider text-slate-400">Cryptographic ledger</p><p className="mt-0.5 font-semibold text-emerald-600">SHA-256 Chained · Immutable Log</p></div><button onClick={exportLogs} className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2 text-xs font-bold text-white hover:bg-[#E44E0E]"><Download className="h-3.5 w-3.5" />Export Audit Log</button></div></div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-3"><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Total Logged Events</p><p className="mt-2 text-3xl font-bold text-slate-900">{MOCK_AUDIT_LOGS.length}</p><p className="mt-1 text-[11px] text-slate-400">Immutable project events</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Planner Decisions</p><p className="mt-2 text-3xl font-bold text-[#FA5A16]">{MOCK_AUDIT_LOGS.filter((log) => log.action.includes('PLANNER')).length}</p><p className="mt-1 text-[11px] text-slate-400">Approved and corrected actions</p></div><div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><p className="text-xs font-semibold text-slate-500">Integrity & Compliance</p><p className="mt-2 flex items-center gap-2 text-2xl font-bold text-emerald-600"><ShieldCheck className="h-6 w-6" />Validated</p><p className="mt-1 text-[11px] text-slate-400">All records cryptographically chained</p></div></div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><div className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-900"><Filter className="h-4 w-4 text-[#FA5A16]" />Filter audit events</div><div className="grid grid-cols-1 gap-2.5 md:grid-cols-2 xl:grid-cols-[minmax(260px,1.8fr)_repeat(5,minmax(135px,1fr))_auto]"><div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} placeholder="Search user, action, entity ID, or note" className="w-full rounded-lg border border-slate-200 bg-slate-50 px-9 py-2.5 text-xs outline-none focus:border-[#FA5A16] focus:bg-white" /></div><select value={date} onChange={(event) => { setDate(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All dates</option><option>Current month</option></select><select value={user} onChange={(event) => { setUser(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All users</option><option>Er. V. K. Kulkarni</option><option>AI Semantic Matching Engine v2.4</option><option>Automated Progress Linking Engine</option></select><select value={action} onChange={(event) => { setAction(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All actions</option><option>PLANNER_APPROVED</option><option>PLANNER_OVERRIDDEN</option><option>SEMANTIC_MATCHED</option><option>DB_COMMITTED</option></select><select value={entity} onChange={(event) => { setEntity(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All entities</option>{MOCK_AUDIT_LOGS.map((log) => <option key={log.id}>{log.activityCode}</option>)}</select><select value={activity} onChange={(event) => { setActivity(event.target.value); setPage(1); }} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs text-slate-600 outline-none"><option>All activities</option>{MOCK_AUDIT_LOGS.map((log) => <option key={log.activityName}>{log.activityName}</option>)}</select><button onClick={clearFilters} className="inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-2.5 text-xs font-semibold text-slate-500 hover:bg-slate-100"><X className="h-3.5 w-3.5" />Clear Filters</button></div></div>

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"><div className="flex items-center justify-between border-b border-slate-200 px-5 py-4"><div><h2 className="text-sm font-bold tracking-wide text-slate-900">CHRONOLOGICAL AUDIT STREAM</h2><p className="mt-1 text-xs text-slate-500">Complete record of project actions and decisions</p></div><span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600"><CheckCircle2 className="h-4 w-4" />Ledger validated</span></div><div className="overflow-x-auto"><table className="w-full min-w-[1100px] text-left text-xs"><thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400"><tr><th className="px-4 py-3 font-bold">Timestamp</th><th className="px-4 py-3 font-bold">User</th><th className="px-4 py-3 font-bold">Action</th><th className="px-4 py-3 font-bold">Entity Affected</th><th className="px-4 py-3 font-bold">Previous → New Value</th><th className="px-4 py-3 font-bold">Reason / Details</th></tr></thead><tbody className="divide-y divide-slate-100">{visibleLogs.map((log) => <tr key={log.id} className="hover:bg-slate-50"><td className="whitespace-nowrap px-4 py-3 font-mono text-[10px] text-slate-500">{formatDate(log.timestamp)}</td><td className="max-w-[190px] px-4 py-3"><span className="inline-flex items-center gap-1.5 font-semibold text-slate-700"><UserRound className="h-3.5 w-3.5 text-slate-400" />{log.actor}</span></td><td className="px-4 py-3"><span className={`inline-flex rounded-full border px-2 py-1 text-[10px] font-bold ${actionClass(log.action)}`}>{actionLabel(log.action)}</span></td><td className="px-4 py-3"><p className="font-mono font-bold text-[#FA5A16]">{log.activityCode}</p><p className="mt-1 max-w-[220px] truncate text-[11px] text-slate-600">{log.activityName}</p></td><td className="whitespace-nowrap px-4 py-3 font-mono text-slate-600"><span className="text-slate-400">{log.previousProgress}%</span><span className="mx-1 text-slate-300">→</span><strong className="text-slate-800">{log.newProgress}%</strong></td><td className="max-w-[360px] px-4 py-3 leading-relaxed text-slate-500">{log.details}</td></tr>)}</tbody></table></div><div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-3 text-xs sm:flex-row sm:items-center sm:justify-between"><span className="text-slate-500">Showing {filteredLogs.length ? (page - 1) * PAGE_SIZE + 1 : 0}-{Math.min(page * PAGE_SIZE, filteredLogs.length)} of {filteredLogs.length} audit events</span><div className="flex items-center gap-1"><button disabled={page === 1} onClick={() => setPage((current) => current - 1)} className="rounded-md px-2 py-1 font-semibold text-slate-500 hover:bg-slate-100 disabled:opacity-40">Previous</button>{Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => <button key={number} onClick={() => setPage(number)} className={`h-7 min-w-7 rounded-md px-2 font-bold ${page === number ? 'bg-[#FA5A16] text-white' : 'text-slate-500 hover:bg-slate-100'}`}>{number}</button>)}<button disabled={page === totalPages} onClick={() => setPage((current) => current + 1)} className="rounded-md px-2 py-1 font-semibold text-slate-500 hover:bg-slate-100 disabled:opacity-40">Next</button></div></div></section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="text-sm font-bold tracking-wide text-slate-900">CRYPTOGRAPHIC AUDIT PROOF</h2><p className="mt-1 text-xs text-slate-500">Immutable validation metadata for the current ledger chain</p></div><span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700"><ShieldCheck className="h-3.5 w-3.5" />Ledger Validated</span></div><div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4"><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Audit Hash (SHA-256)</p><p className="mt-2 break-all font-mono text-[11px] font-semibold text-slate-700">8d3a5e1b4c2f9a77e61a0f4c2d8b9057...c18e</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Supervisor Report Reference</p><p className="mt-2 text-xs font-semibold text-slate-700">DSR_2026_09_05_Zone3_Pier14.pdf</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Evidence Bundle</p><p className="mt-2 text-xs font-semibold text-slate-700">AUD-90501 · 6 attached files</p></div><div className="rounded-lg border border-slate-200 bg-slate-50 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-400">Cryptographic Timestamp</p><p className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700"><Clock3 className="h-3.5 w-3.5 text-[#FA5A16]" />05 Sep 2026, 18:35:12 UTC</p></div></div></section>
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><div className="flex items-center gap-2"><MessageSquare className="h-4 w-4 text-[#FA5A16]" /><div><h2 className="text-sm font-bold text-slate-900">AUDIT TRAIL ASSISTANT</h2><p className="mt-1 text-xs text-slate-500">Ask questions about the available project activity and audit records.</p></div></div><div className="mt-4 flex flex-wrap gap-2">{['Who updated Foundation Excavation?', 'When was Reinforcement Installation approved?', 'What was the previous value?'].map((question) => <button key={question} onClick={() => answerAuditQuestion(question)} className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1.5 text-[11px] font-semibold text-[#FA5A16] hover:bg-orange-100">{question}</button>)}</div><div className="mt-4 max-h-52 space-y-2 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-3">{chatMessages.length === 0 ? <p className="text-xs text-slate-500">Ask a suggested question or search the audit records conversationally.</p> : chatMessages.map((message, index) => <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}><p className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${message.role === 'user' ? 'bg-[#FA5A16] text-white' : 'border border-slate-200 bg-white text-slate-700'}`}>{message.text}</p></div>)}</div><form onSubmit={(event) => { event.preventDefault(); if (chatInput.trim()) answerAuditQuestion(chatInput.trim()); }} className="mt-3 flex gap-2"><input value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="Ask about an activity or audit record" className="min-w-0 flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-xs outline-none focus:border-[#FA5A16]" /><button type="submit" className="inline-flex items-center gap-1.5 rounded-lg bg-[#FA5A16] px-3 py-2.5 text-xs font-bold text-white hover:bg-[#E44E0E]"><Send className="h-3.5 w-3.5" />Send</button></form></section>
      </div>
    </div>
  );
}
