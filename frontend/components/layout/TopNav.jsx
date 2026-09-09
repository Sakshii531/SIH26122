'use client';

import React, { useState } from 'react';
import {
  Search,
  Building2,
  ChevronDown,
  Menu,
  CheckCircle2,
  TrainTrack,
  Bell,
  CircleHelp
} from 'lucide-react';
import { MOCK_PROJECTS } from '../../services/mock/mockProjects.js';
import { useSidebar } from './Sidebar.jsx';
import { useRoleContext } from '../providers/RoleContext.jsx';
import { ROLES } from '../../hooks/useRole.js';
import { usePathname } from 'next/navigation';

export function TopNav() {
  const pathname = usePathname();
  const { role } = useRoleContext();
  const [selectedProject, setSelectedProject] = useState(MOCK_PROJECTS[0]);
  const [isProjectDropdownOpen, setIsProjectDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { setIsOpen: setSidebarOpen } = useSidebar();
  const isPlannerDashboard = role === ROLES.PLANNER && pathname === '/';
  const isSupervisor = role === ROLES.SUPERVISOR;

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 md:px-6 flex items-center justify-between sticky top-0 z-20 shadow-2xs gap-4">
      {/* Left: Mobile hamburger + Field Operations Title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={() => setSidebarOpen(true)}
          className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-all shrink-0 cursor-pointer"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-base md:text-lg font-bold text-slate-900 leading-tight">
            Field Operations
          </h1>
          <p className="text-[11px] md:text-xs text-slate-500 leading-tight">
            Field reporting and project activity records
          </p>
        </div>
      </div>

      {/* Right: Project Selector, Search, Field Sync status, Profile Avatar */}
      <div className="flex items-center gap-2.5 md:gap-4 shrink-0">
        {/* Project Selector Badge */}
        <div className="relative">
          <button
            onClick={() => setIsProjectDropdownOpen(!isProjectDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#D97706]/40 bg-[#FFFBEB]/40 hover:bg-[#FFFBEB] text-slate-800 text-xs font-semibold transition-all cursor-pointer shadow-2xs"
          >
            <div className="w-4 h-4 rounded bg-[#D97706]/15 flex items-center justify-center text-[#B45309]">
              <TrainTrack className="w-3 h-3" />
            </div>
            <span className="truncate max-w-[140px] sm:max-w-[200px] md:max-w-[260px]">
              {selectedProject.name}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          </button>

          {isProjectDropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 md:w-80 bg-white border border-slate-200 rounded-xl shadow-xl p-2 z-50 animate-fade-in">
              <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                Select Active Infrastructure Project
              </div>
              <div className="space-y-1 mt-1">
                {MOCK_PROJECTS.map((proj) => (
                  <button
                    key={proj.id}
                    onClick={() => {
                      setSelectedProject(proj);
                      setIsProjectDropdownOpen(false);
                    }}
                    className={`w-full text-left p-2.5 rounded-lg text-xs transition-all flex items-start justify-between cursor-pointer ${
                      selectedProject.id === proj.id
                        ? 'bg-orange-50 border border-orange-200 text-orange-950 font-semibold'
                        : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div>
                      <p className="font-bold text-slate-900">{proj.name}</p>
                      <p className="text-[11px] text-slate-500 line-clamp-1">{proj.location}</p>
                    </div>
                    {selectedProject.id === proj.id && (
                      <CheckCircle2 className="w-4 h-4 text-[#FA5A16] shrink-0 mt-0.5" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Global Search Ctrl+K */}
        <div className="relative hidden sm:block">
          <div className="flex items-center bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus-within:border-slate-400 focus-within:bg-white transition-all">
            <Search className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search"
              className="bg-transparent text-xs text-slate-800 placeholder-slate-400 focus:outline-none w-28 md:w-36"
            />
            <kbd className="hidden md:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-white border border-slate-200 rounded shadow-3xs ml-1">
              Ctrl+K
            </kbd>
          </div>
        </div>

        {/* Field Sync: Connected Status Indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="hidden sm:inline text-xs font-medium text-slate-700">
            Field Sync: <strong className="font-semibold text-slate-900">Connected</strong>
          </span>
        </div>

        {isPlannerDashboard && (
          <>
            <button
              title="Notifications"
              aria-label="Notifications"
              className="relative rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-[#FA5A16]" />
            </button>
            <button
              title="Help and support"
              aria-label="Help and support"
              className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800"
            >
              <CircleHelp className="h-4 w-4" />
            </button>
          </>
        )}

        {!isPlannerDashboard && !isSupervisor && <div className="relative w-8 h-8 rounded-full overflow-hidden border border-slate-300 shadow-3xs shrink-0 cursor-pointer">
          <img
            src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
            alt="Marcus Vance"
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
          <div className="w-full h-full bg-slate-800 flex items-center justify-center text-white font-bold text-xs">
            MV
          </div>
        </div>}
      </div>
    </header>
  );
}
