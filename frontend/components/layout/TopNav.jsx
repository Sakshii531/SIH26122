'use client';

import React, { useState } from 'react';
import {
  Search, Bell, Building2, UploadCloud, ChevronDown,
  CheckCircle2, Menu, LogOut, UserCog
} from 'lucide-react';
import { MOCK_PROJECTS } from '../../services/mock/mockProjects.js';
import { NotificationDrawer } from './NotificationDrawer.jsx';
import { useSidebar } from './Sidebar.jsx';
import { useRoleContext } from '../providers/RoleContext.jsx';
import { ROLE_LABELS } from '../../hooks/useRole.js';

// Role → colour pill style
const rolePillStyles = {
  planner: 'bg-blue-100 text-blue-700 border-blue-200',
  manager: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  worker: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  admin: 'bg-rose-100 text-rose-700 border-rose-200',
};

export function TopNav() {
  const [selectedProject, setSelectedProject] = useState(MOCK_PROJECTS[0]);
  const [isProjectDropdownOpen, setIsProjectDropdownOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);

  const { setIsOpen: setSidebarOpen } = useSidebar();
  const { role, label: roleLabel } = useRoleContext();

  return (
    <>
      <header className="h-14 md:h-16 bg-white border-b border-slate-200 px-3 md:px-6 flex items-center justify-between sticky top-0 z-20 shadow-sm gap-2">

        {/* ---- LEFT: Hamburger (mobile only) + Project Selector ---- */}
        <div className="flex items-center gap-2 min-w-0">
          {/* Hamburger — mobile only */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-all shrink-0 cursor-pointer"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Project Selector */}
          <div className="relative">
            <button
              onClick={() => setIsProjectDropdownOpen(!isProjectDropdownOpen)}
              className="flex items-center gap-1.5 md:gap-2.5 px-2.5 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-800 transition-all cursor-pointer min-w-0"
            >
              <Building2 className="w-4 h-4 text-blue-600 shrink-0" />
              <span className="font-bold text-slate-900 hidden sm:inline shrink-0">{selectedProject.code}:</span>
              <span className="text-slate-600 truncate max-w-[120px] md:max-w-[240px]">{selectedProject.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            </button>

            {isProjectDropdownOpen && (
              <div className="absolute left-0 mt-2 w-72 md:w-80 bg-white border border-slate-200 rounded-xl shadow-xl p-2 z-50 animate-fade-in">
                <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Select Infrastructure Project
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
                          ? 'bg-blue-50 border border-blue-200 text-blue-900'
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <div>
                        <p className="font-bold">{proj.code}</p>
                        <p className="text-[11px] text-slate-500 line-clamp-1">{proj.name}</p>
                      </div>
                      {selectedProject.id === proj.id && (
                        <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ---- CENTER: Global Search (hidden on small screens) ---- */}
        <div className="relative flex-1 max-w-sm hidden lg:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search Primavera activity, WBS, DSR log…"
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
          />
        </div>

        {/* ---- RIGHT: Actions & Profile ---- */}
        <div className="flex items-center gap-2 md:gap-3 shrink-0">
          {/* Ingest CTA — hide label on small mobile */}
          <a
            href="/capture"
            className="flex items-center gap-1.5 md:gap-2 px-2.5 md:px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-all"
          >
            <UploadCloud className="w-4 h-4 shrink-0" />
            <span className="hidden sm:inline">Ingest Daily Log</span>
          </a>

          {/* Notification Bell */}
          <button
            onClick={() => setIsNotificationOpen(true)}
            className="relative p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition-all cursor-pointer"
            title="Pending Verification Alerts"
            aria-label="Open notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-white text-[9px] font-bold flex items-center justify-center border-2 border-white shadow-xs">
              4
            </span>
          </button>

          {/* User Profile + Role Pill */}
          <div className="flex items-center gap-2 pl-2 md:pl-3 border-l border-slate-200">
            <div className="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center font-bold text-xs text-blue-700 shrink-0">
              VK
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-bold text-slate-800 leading-tight">Er. V. K. Kulkarni</p>
              <span className={`inline-block mt-0.5 px-1.5 py-0.5 rounded-md text-[9px] font-bold border ${rolePillStyles[role]}`}>
                {roleLabel}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Notification Drawer Slide-over */}
      <NotificationDrawer isOpen={isNotificationOpen} onClose={() => setIsNotificationOpen(false)} />
    </>
  );
}
