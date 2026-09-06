'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  CalendarDays,
  FileSpreadsheet,
  Cpu,
  CheckSquare,
  LineChart,
  FileSearch,
  History,
  HardHat,
  X,
  FileText,
  Mic,
  Activity,
  Shield,
  HardHat as HardHatIcon,
  UserCog
} from 'lucide-react';
import { useRoleContext } from '../providers/RoleContext.jsx';
import { ROLES, ROLE_LABELS } from '../../hooks/useRole.js';

// ---------------------------------------------------------------------------
// Sidebar open/close context (shared between Sidebar & TopNav hamburger btn)
// ---------------------------------------------------------------------------
const SidebarContext = createContext(null);

export function SidebarProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <SidebarContext.Provider value={{ isOpen, setIsOpen }}>
      {children}
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const ctx = useContext(SidebarContext);
  if (!ctx) throw new Error('useSidebar must be used within <SidebarProvider>');
  return ctx;
}

// ---------------------------------------------------------------------------
// Navigation definition
// ---------------------------------------------------------------------------
const navSections = [
  {
    title: 'OVERVIEW',
    items: [
      { name: 'Dashboard Overview', href: '/', icon: LayoutDashboard, roles: null /* all roles */ }
    ]
  },
  {
    title: 'SITE DATA CAPTURE',
    items: [
      {
        name: 'Multi-Format Ingest',
        href: '/capture',
        icon: FileSpreadsheet,
        badge: 'PDF / Excel / Voice',
        roles: ['planner', 'worker', 'admin']
      }
    ]
  },
  {
    title: 'PLANNING & MATCHING',
    items: [
      {
        name: 'Primavera L5/L6 Schedule',
        href: '/schedule',
        icon: CalendarDays,
        roles: ['planner', 'manager', 'admin']
      },
      {
        name: 'AI Activity Matching',
        href: '/matching',
        icon: Cpu,
        badge: 'AI',
        roles: ['planner', 'manager', 'admin']
      },
      {
        name: 'Planner Verification',
        href: '/verification',
        icon: CheckSquare,
        badge: '4 Pending',
        highlight: true,
        roles: ['planner', 'admin']
      }
    ]
  },
  {
    title: 'TRACKING & AUDIT',
    items: [
      {
        name: 'Source Traceability',
        href: '/traceability',
        icon: FileSearch,
        roles: ['planner', 'manager', 'admin']
      },
      {
        name: 'Planned vs Actual',
        href: '/analytics',
        icon: LineChart,
        roles: ['planner', 'manager', 'admin']
      },
      {
        name: 'Audit Trail & Archive',
        href: '/history',
        icon: History,
        roles: ['manager', 'admin']
      }
    ]
  }
];

// Role badge colour map
const roleBadgeStyles = {
  planner: 'bg-blue-900/60 text-blue-300 border border-blue-700',
  manager: 'bg-indigo-900/60 text-indigo-300 border border-indigo-700',
  worker: 'bg-emerald-900/60 text-emerald-300 border border-emerald-700',
  admin: 'bg-rose-900/60 text-rose-300 border border-rose-700',
};

// ---------------------------------------------------------------------------
// SidebarContent — the inner panel (shared between desktop & mobile drawer)
// ---------------------------------------------------------------------------
function SidebarContent({ onLinkClick }) {
  const pathname = usePathname();
  const { role, setRole } = useRoleContext();

  // Filter nav items by role
  const visibleSections = navSections
    .map((sec) => ({
      ...sec,
      items: sec.items.filter((item) => !item.roles || item.roles.includes(role))
    }))
    .filter((sec) => sec.items.length > 0);

  return (
    <div className="flex flex-col h-full">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 flex items-center gap-3 bg-slate-950/60 shrink-0">
        <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
          <HardHat className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-extrabold text-slate-100 text-base leading-tight tracking-tight">SIH26122</h1>
          <p className="text-[10px] text-blue-400 font-medium">Planning-to-Execution Bridge</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
        {visibleSections.map((sec, idx) => (
          <div key={idx} className="space-y-1">
            <div className="px-3 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              {sec.title}
            </div>
            {sec.items.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onLinkClick}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-xs font-bold'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-bold shrink-0 ${
                        isActive
                          ? 'bg-blue-800 text-white'
                          : item.highlight
                          ? 'bg-amber-950 text-amber-400 border border-amber-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Role Switcher (dev / demo convenience) */}
      <div className="px-3 py-2 border-t border-slate-800 bg-slate-950/50 shrink-0">
        <p className="px-1 text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Active Role</p>
        <div className="grid grid-cols-2 gap-1">
          {Object.values(ROLES).map((r) => (
            <button
              key={r}
              onClick={() => setRole(r)}
              className={`px-2 py-1 rounded text-[10px] font-bold text-left transition-all cursor-pointer ${
                role === r
                  ? roleBadgeStyles[r]
                  : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
              }`}
            >
              {ROLE_LABELS[r]}
            </button>
          ))}
        </div>
      </div>

      {/* Active Project Footer Card */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/70 shrink-0">
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mb-1">
            <span>ACTIVE PROJECT</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
          <p className="text-xs font-bold text-slate-100 truncate">Metro Viaduct Package 4</p>
          <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-400 font-mono">
            <span>SPI: <strong className="text-amber-400 font-bold">0.89</strong></span>
            <span>CPI: <strong className="text-emerald-400 font-bold">0.94</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sidebar — Desktop: sticky aside | Mobile: slide-over drawer
// ---------------------------------------------------------------------------
export function Sidebar() {
  const { isOpen, setIsOpen } = useSidebar();

  // Close drawer on Escape key
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [setIsOpen]);

  // Prevent body scroll when drawer is open on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  return (
    <>
      {/* ===== DESKTOP: Always-visible fixed sidebar (hidden on mobile) ===== */}
      <aside className="hidden md:flex w-64 bg-slate-900 border-r border-slate-800 flex-col h-screen sticky top-0 z-30 select-none text-slate-300 shrink-0">
        <SidebarContent onLinkClick={undefined} />
      </aside>

      {/* ===== MOBILE: Slide-over drawer (visible only on mobile) ===== */}
      {/* Backdrop overlay */}
      <div
        aria-hidden="true"
        onClick={() => setIsOpen(false)}
        className={`md:hidden fixed inset-0 bg-slate-950/70 z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
      />

      {/* Drawer panel */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Navigation"
        className={`md:hidden fixed top-0 left-0 h-full w-72 max-w-[85vw] bg-slate-900 border-r border-slate-800 z-50 flex flex-col text-slate-300 select-none
          transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Close button inside drawer */}
        <button
          onClick={() => setIsOpen(false)}
          className="absolute top-3 right-3 p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-all cursor-pointer z-10"
          aria-label="Close navigation"
        >
          <X className="w-4 h-4" />
        </button>

        <SidebarContent onLinkClick={() => setIsOpen(false)} />
      </aside>
    </>
  );
}
