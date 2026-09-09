'use client';

import React, { useState, useMemo, useEffect } from 'react';
import {
  Search,
  SlidersHorizontal,
  Lock,
  Eye,
  Paperclip,
  ChevronDown,
  RotateCcw,
  Calendar,
  Layers,
  CheckCircle2,
  AlertCircle,
  Clock3,
  ExternalLink
} from 'lucide-react';
import { MOCK_FIELD_REPORTS } from '../../services/mock/mockFieldReports.js';
import { ReportDetailModal } from '../../components/reports/ReportDetailModal.jsx';
import { useRoleContext } from '../../components/providers/RoleContext.jsx';
import { ROLES } from '../../hooks/useRole.js';
import { DashboardOverview } from '../../components/planner/DashboardOverview.jsx';

function FieldReportsPage() {
  const { role } = useRoleContext();

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDateFilter, setSelectedDateFilter] = useState('Last 30 Days');
  const [selectedActivity, setSelectedActivity] = useState('All Activities');
  const [selectedReportType, setSelectedReportType] = useState('All Types');
  const [selectedStatus, setSelectedStatus] = useState('All Statuses');
  const [selectedLocation, setSelectedLocation] = useState('All Sectors & Zones');
  const [sortOrder, setSortOrder] = useState('DATE (DESC)');

  // Selected report for modal inspect view
  const [selectedReport, setSelectedReport] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Live timestamp simulating supervisor session clock
  const [liveTime, setLiveTime] = useState('08 Sep 2026, 18:02:14 EET');

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      // Format with EET timezone feel
      const hours = String(now.getHours()).padStart(2, '0');
      const mins = String(now.getMinutes()).padStart(2, '0');
      const secs = String(now.getSeconds()).padStart(2, '0');
      setLiveTime(`08 Sep 2026, ${hours}:${mins}:${secs} EET`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Filtered reports logic
  const filteredReports = useMemo(() => {
    return MOCK_FIELD_REPORTS.filter((report) => {
      // Search matching ID, activity, WBS, or location
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = report.id.toLowerCase().includes(q);
        const matchesActivity = report.activity.toLowerCase().includes(q);
        const matchesWbs = report.wbs.toLowerCase().includes(q);
        const matchesLoc = report.location.toLowerCase().includes(q);
        if (!matchesId && !matchesActivity && !matchesWbs && !matchesLoc) {
          return false;
        }
      }

      // Activity filter
      if (selectedActivity !== 'All Activities' && report.activity !== selectedActivity) {
        return false;
      }

      // Report Type filter
      if (selectedReportType !== 'All Types' && report.reportType !== selectedReportType) {
        return false;
      }

      // Status filter
      if (selectedStatus !== 'All Statuses' && report.status !== selectedStatus) {
        return false;
      }

      // Location filter
      if (selectedLocation !== 'All Sectors & Zones' && report.location !== selectedLocation) {
        return false;
      }

      return true;
    });
  }, [
    searchQuery,
    selectedActivity,
    selectedReportType,
    selectedStatus,
    selectedLocation
  ]);

  // Clear filters handler
  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedDateFilter('Last 30 Days');
    setSelectedActivity('All Activities');
    setSelectedReportType('All Types');
    setSelectedStatus('All Statuses');
    setSelectedLocation('All Sectors & Zones');
  };

  const hasActiveFilters =
    searchQuery !== '' ||
    selectedDateFilter !== 'Last 30 Days' ||
    selectedActivity !== 'All Activities' ||
    selectedReportType !== 'All Types' ||
    selectedStatus !== 'All Statuses' ||
    selectedLocation !== 'All Sectors & Zones';

  const handleOpenReport = (report) => {
    setSelectedReport(report);
    setIsModalOpen(true);
  };

  if (role === ROLES.PLANNER) {
    return <DashboardOverview />;
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-5 animate-fade-in text-slate-800">
      {/* 1. Header & Breadcrumb Zone */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          {/* Breadcrumb with Orange Dot */}
          <div className="flex items-center gap-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider font-mono">
            <span className="w-2 h-2 rounded-full bg-[#FA5A16]" />
            <span>NIYOGEN / FIELD SURVEILLANCE & AUDIT</span>
          </div>

          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Field Reports
          </h1>
          <p className="text-xs md:text-sm text-slate-500 mt-0.5">
            View submitted field reports and track reported project activity.
          </p>
        </div>

        {/* Read-Only Archive & Supervisor ID Stamp */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs font-mono text-slate-500">
          <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-slate-100 border border-slate-200 text-slate-700 font-semibold tracking-wider text-[11px]">
            <Lock className="w-3 h-3 text-slate-600" />
            <span>READ-ONLY ARCHIVE</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 ml-0.5" />
          </div>
          <div className="text-right sm:text-left">
            <span className="text-slate-600">Supervisor ID: </span>
            <strong className="text-slate-800 font-bold">SV-8842</strong>
            <span className="mx-1.5 text-slate-300">·</span>
            <span className="text-slate-500">{liveTime}</span>
          </div>
        </div>
      </div>

      {/* 2. Filter Toolbar Card */}
      <div className="p-3.5 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-3">
        {/* Row 1: Search & Date & Activity */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-2.5">
          {/* Main Search Input */}
          <div className="md:col-span-6 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports, activities or report ID..."
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50/70 hover:bg-slate-50 focus:bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-400 transition-all"
            />
          </div>

          {/* Date Filter Dropdown */}
          <div className="md:col-span-3 relative">
            <select
              value={selectedDateFilter}
              onChange={(e) => setSelectedDateFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50/70 hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-slate-400 transition-all appearance-none cursor-pointer pr-8"
            >
              <option value="Last 7 Days">Date: Last 7 Days</option>
              <option value="Last 30 Days">Date: Last 30 Days</option>
              <option value="Last 90 Days">Date: Last 90 Days</option>
              <option value="All Time">Date: All Records</option>
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Activity Dropdown */}
          <div className="md:col-span-3 relative">
            <select
              value={selectedActivity}
              onChange={(e) => setSelectedActivity(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50/70 hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-slate-400 transition-all appearance-none cursor-pointer pr-8"
            >
              <option value="All Activities">Activity: All Activities</option>
              <option value="Foundation Excavation">Foundation Excavation</option>
              <option value="Reinforcement Installation">Reinforcement Installation</option>
              <option value="Concrete Pouring">Concrete Pouring</option>
              <option value="Structural Formwork">Structural Formwork</option>
              <option value="Pipeline Installation">Pipeline Installation</option>
              <option value="Drainage Installation">Drainage Installation</option>
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>

        {/* Row 2: Report Type, Status, Location & Clear */}
        <div className="flex flex-wrap items-center justify-between gap-2.5 pt-1">
          <div className="flex flex-wrap items-center gap-2.5 flex-1 min-w-0">
            {/* Report Type */}
            <div className="relative min-w-[150px]">
              <select
                value={selectedReportType}
                onChange={(e) => setSelectedReportType(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50/70 hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-slate-400 transition-all appearance-none cursor-pointer pr-8"
              >
                <option value="All Types">Report Type: All Types</option>
                <option value="Daily Report">Daily Report</option>
                <option value="Shift Report">Shift Report</option>
                <option value="Inspection">Inspection</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            {/* Status Dropdown */}
            <div className="relative min-w-[150px]">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50/70 hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-slate-400 transition-all appearance-none cursor-pointer pr-8"
              >
                <option value="All Statuses">Status: All Statuses</option>
                <option value="Verified">Verified</option>
                <option value="Under Review">Under Review</option>
                <option value="Requires Attention">Requires Attention</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            {/* Location Dropdown */}
            <div className="relative min-w-[180px]">
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50/70 hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium focus:outline-none focus:border-slate-400 transition-all appearance-none cursor-pointer pr-8"
              >
                <option value="All Sectors & Zones">Location: All Sectors & Zones</option>
                <option value="North Foundation Zone">North Foundation Zone</option>
                <option value="Pier 14 West">Pier 14 West</option>
                <option value="Deck B Sub">Deck B Sub</option>
                <option value="Ret. Wall South">Ret. Wall South</option>
                <option value="Utility Trench N">Utility Trench N</option>
                <option value="Culvert C-04">Culvert C-04</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* Clear Filters Action */}
          <button
            onClick={handleClearFilters}
            className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
              hasActiveFilters
                ? 'text-[#FA5A16] hover:bg-orange-50'
                : 'text-slate-400 hover:text-slate-600'
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Clear filters</span>
          </button>
        </div>
      </div>

      {/* 3. Table Subheader & Sort Bar */}
      <div className="flex items-center justify-between text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider px-1">
        <div className="flex items-center gap-2">
          <span className="text-slate-500 font-bold">LEDGER STREAM</span>
          <span className="text-slate-400">•</span>
          <span className="text-slate-600 font-bold">{filteredReports.length} RECORDS SHOWN</span>
        </div>

        <div className="flex items-center gap-1 cursor-pointer hover:text-slate-600 transition-colors">
          <span>SORT: {sortOrder}</span>
          <ChevronDown className="w-3.5 h-3.5" />
        </div>
      </div>

      {/* 4. Ledger Stream Table Card */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/50 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4 w-28">REPORT ID</th>
                <th className="py-3 px-4 w-32">DATE</th>
                <th className="py-3 px-4">ACTIVITY & WBS</th>
                <th className="py-3 px-4">LOCATION</th>
                <th className="py-3 px-4 w-28">REPORT TYPE</th>
                <th className="py-3 px-4 w-44">REPORTED PROGRESS</th>
                <th className="py-3 px-4 w-36">STATUS</th>
                <th className="py-3 px-4 w-24">EVIDENCE</th>
                <th className="py-3 px-4 w-20 text-right">ACTION</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredReports.map((report, index) => {
                const isHighlight = index === 0; // First row has the orange accent bar as in screenshot
                return (
                  <tr
                    key={report.id}
                    onClick={() => handleOpenReport(report)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                  >
                    {/* REPORT ID */}
                    <td className="py-4 px-4 font-mono font-bold relative">
                      {isHighlight && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-[#FA5A16] rounded-r" />
                      )}
                      <div className="flex flex-col">
                        <span className="text-[#FA5A16] leading-none text-xs font-bold">
                          {report.idPrefix}
                        </span>
                        <span className="text-[#FA5A16] leading-none text-sm font-black tracking-tight">
                          {report.idNum}
                        </span>
                      </div>
                    </td>

                    {/* DATE */}
                    <td className="py-4 px-4 text-slate-700 font-medium whitespace-nowrap">
                      {report.date}
                    </td>

                    {/* ACTIVITY & WBS */}
                    <td className="py-4 px-4">
                      <p className="font-bold text-slate-900 text-xs group-hover:text-[#FA5A16] transition-colors">
                        {report.activity}
                      </p>
                      <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                        {report.wbs}
                      </p>
                    </td>

                    {/* LOCATION */}
                    <td className="py-4 px-4 text-slate-700 font-medium whitespace-nowrap">
                      {report.location}
                    </td>

                    {/* REPORT TYPE */}
                    <td className="py-4 px-4 text-slate-500 whitespace-nowrap text-[11px]">
                      {report.reportType}
                    </td>

                    {/* REPORTED PROGRESS */}
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-between mb-1 text-xs">
                        <span className="font-black text-slate-900 font-mono-num">
                          {report.progress}%
                        </span>
                        {report.progressDelta && (
                          <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                            {report.progressDelta}
                          </span>
                        )}
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            report.progress === 100 ? 'bg-emerald-600' : 'bg-[#FA5A16]'
                          }`}
                          style={{ width: `${report.progress}%` }}
                        />
                      </div>
                    </td>

                    {/* STATUS PILL */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      {report.status === 'Verified' && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#E8F8F0] text-[#059669] border border-[#A3E6CD]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#059669]" />
                          Verified
                        </span>
                      )}
                      {report.status === 'Under Review' && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FEF7E0] text-[#B78103] border border-[#FEEAA3]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#B78103]" />
                          Under Review
                        </span>
                      )}
                      {report.status === 'Requires Attention' && (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#FDE8E8] text-[#D9383A] border border-[#F8B4B4]">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#D9383A]" />
                          Requires Attention
                        </span>
                      )}
                    </td>

                    {/* EVIDENCE */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5 text-slate-500 font-medium">
                        <Paperclip className="w-3.5 h-3.5 text-slate-400 rotate-45" />
                        <span className="text-xs">{report.evidenceCount} files</span>
                      </div>
                    </td>

                    {/* ACTION */}
                    <td className="py-4 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenReport(report);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-all cursor-pointer shadow-3xs"
                      >
                        <Eye className="w-3.5 h-3.5 text-slate-500" />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                );
              })}

              {filteredReports.length === 0 && (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <p className="text-sm font-medium">No field reports match your active filters.</p>
                    <button
                      onClick={handleClearFilters}
                      className="mt-2 text-xs text-[#FA5A16] font-bold hover:underline"
                    >
                      Reset All Filters
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* 5. Pagination Footer */}
        <div className="px-4 py-3.5 border-t border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <span className="text-slate-500 font-medium">
            Showing 1-{filteredReports.length} of 248 entries
          </span>

          <div className="flex items-center gap-1 self-center sm:self-auto">
            <button
              disabled
              className="px-2.5 py-1 text-slate-400 hover:text-slate-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer font-medium"
            >
              &lt; Prev
            </button>
            <button className="w-7 h-7 rounded bg-[#FA5A16] text-white font-bold flex items-center justify-center shadow-xs">
              1
            </button>
            <button className="w-7 h-7 rounded text-slate-600 hover:bg-slate-200 font-medium flex items-center justify-center transition-colors">
              2
            </button>
            <button className="w-7 h-7 rounded text-slate-600 hover:bg-slate-200 font-medium flex items-center justify-center transition-colors">
              3
            </button>
            <span className="px-1 text-slate-400 font-bold">...</span>
            <button className="w-7 h-7 rounded text-slate-600 hover:bg-slate-200 font-medium flex items-center justify-center transition-colors">
              42
            </button>
            <button className="px-2.5 py-1 text-slate-600 hover:text-slate-900 font-medium cursor-pointer">
              Next &gt;
            </button>
          </div>
        </div>
      </div>

      {/* Report Details Slide-over / Modal */}
      <ReportDetailModal
        report={selectedReport}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}

export default function MainPage() {
  const { role } = useRoleContext();
  if (role === 'planner' || role === 'manager' || role === 'admin') {
    return <DashboardOverview />;
  }
  return <FieldReportsPage />;
}
