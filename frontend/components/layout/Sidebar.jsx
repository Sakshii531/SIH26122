'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  FileText,
  FilePlus2,
  Bell,
  LogOut,
  X,
  LayoutDashboard,
  CalendarDays,
  Cpu,
  CheckSquare,
  AlertTriangle,
  History,
  Settings,
  UserCircle
} from 'lucide-react';
import { useRoleContext } from '../providers/RoleContext.jsx';
import { ROLES } from '../../hooks/useRole.js';

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
// Supervisor Navigation Definitions: Reports & Submit Daily Report ONLY
// ---------------------------------------------------------------------------
const supervisorNavItems = [
  {
    name: 'Reports',
    href: '/',
    icon: FileText,
  },
  {
    name: 'Submit Daily Report',
    href: '/capture',
    icon: FilePlus2,
  },
];

// ---------------------------------------------------------------------------
// Planner Navigation
// ---------------------------------------------------------------------------
const plannerNavItems = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Project Plan', href: '/schedule', icon: CalendarDays },
  { name: 'Activities', href: '/capture', icon: CheckSquare },
  { name: 'AI Match Review', href: '/matching', icon: Cpu },
  { name: 'Conflict Center', href: '/verification', icon: AlertTriangle },
  { name: 'Approved Activities', href: '/traceability', icon: CheckSquare },
  { name: 'Audit Trail', href: '/history', icon: History },
];

// ---------------------------------------------------------------------------
// SupervisorSidebarContent — Clean Supervisor Sidebar with NIYOGEN Branding
// ---------------------------------------------------------------------------
function SupervisorSidebarContent({ onLinkClick }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    router.push('/login');
  };

  return (
    <div className="flex flex-col h-full bg-[#18181B] text-[#9CA3AF] select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#27272A] shrink-0">
        <div className="flex items-center justify-between">
          {/* NIYOGEN White Box Logo */}
          <div className="bg-white rounded-md px-3 py-1.5 flex items-center gap-2 shadow-xs">
            <svg
              className="w-5 h-5 text-black"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="24" height="24" rx="3" fill="#000000" />
              <path
                d="M6 18V6L14 18V6"
                stroke="#FFFFFF"
                strokeWidth="2.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M18 6V18"
                stroke="#FA5A16"
                strokeWidth="2.7"
                strokeLinecap="round"
              />
            </svg>
            <span className="font-black text-black tracking-wider text-sm">NIYOGEN</span>
          </div>

          {/* Orange Status Indicator Dot */}
          <div className="relative flex items-center justify-center">
            <span className="w-2.5 h-2.5 rounded-full bg-[#FA5A16]" />
            <span className="absolute w-4 h-4 rounded-full bg-[#FA5A16]/30 animate-ping" />
          </div>
        </div>

        {/* Role Sub-Badge */}
        <div className="mt-3.5 px-0.5">
          <div className="flex items-center justify-between text-[10px] font-mono tracking-wider font-bold text-[#FA5A16]">
            <span>ROLE: SUPERVISOR</span>
            <span className="text-[#9CA3AF] bg-[#27272A] px-1 rounded text-[9px]">SEC-04</span>
          </div>
          <p className="text-[11px] text-[#A1A1AA] mt-0.5 font-medium">Field Operations Unit</p>
        </div>
      </div>

      {/* Main Navigation: Reports & Submit Daily Report ONLY */}
      <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        <div className="space-y-1.5">
          <div className="px-2 pb-1 text-[10px] font-bold text-[#71717A] tracking-wider uppercase font-mono">
            OPERATIONS CORE
          </div>
          {supervisorNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onLinkClick}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer ${
                  isActive
                    ? 'bg-[#FA5A16] text-white shadow-md font-bold'
                    : 'text-[#A1A1AA] hover:text-white hover:bg-[#27272A]/70'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-[#A1A1AA]'}`} />
                <span className="tracking-tight">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* User Card at the Bottom */}
      <div className="p-3 border-t border-[#27272A] bg-[#141416] shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            {/* Marcus Vance Profile Picture */}
            <div className="relative w-8 h-8 rounded-full overflow-hidden bg-gradient-to-tr from-amber-600 to-[#FA5A16] flex items-center justify-center text-white font-bold text-xs shrink-0 border border-white/20 shadow-xs">
              <img
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
                alt="Marcus Vance"
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
              <span className="absolute">MV</span>
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold text-white truncate leading-tight">Marcus Vance</p>
              <p className="text-[11px] text-[#71717A] truncate font-medium">Site Sup. | Sector 4</p>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogout}
            title="Log out session"
            className="p-1.5 rounded text-[#71717A] hover:text-white hover:bg-[#27272A] transition-colors cursor-pointer"
            aria-label="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// PlannerSidebarContent — Planner Sidebar with Full Project Access
// ---------------------------------------------------------------------------
function PlannerSidebarContent({ onLinkClick }) {
  const pathname = usePathname();
  const router = useRouter();
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const handleSignOut = () => {
    setIsProfileMenuOpen(false);
    router.push('/login');
  };

  return (
    <div className="flex flex-col h-full bg-[#18181B] text-[#9CA3AF] select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#27272A] shrink-0">
        <div className="flex items-center justify-between">
          <div className="bg-white rounded-md px-3 py-1.5 flex items-center gap-2 shadow-xs">
            <svg className="w-5 h-5 text-black" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="24" height="24" rx="3" fill="#000000" />
              <path d="M6 18V6L14 18V6" stroke="#FFFFFF" strokeWidth="2.7" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M18 6V18" stroke="#FA5A16" strokeWidth="2.7" strokeLinecap="round" />
            </svg>
            <span className="font-black text-black tracking-wider text-sm">NIYOGEN</span>
          </div>
          <span className="w-2.5 h-2.5 rounded-full bg-[#FA5A16]" />
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {plannerNavItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={onLinkClick}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                isActive
                  ? 'bg-[#FA5A16] text-white shadow-xs font-bold'
                  : 'text-[#A1A1AA] hover:text-white hover:bg-[#27272A]/70'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-[#A1A1AA]'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Planner User Profile */}
      <div className="relative p-3 border-t border-[#27272A] bg-[#141416] shrink-0">
        {isProfileMenuOpen && (
          <div className="absolute bottom-full left-3 right-3 mb-2 overflow-hidden rounded-lg border border-[#3F3F46] bg-[#1F1F22] p-1 shadow-xl">
            <Link
              href="/history"
              onClick={() => {
                setIsProfileMenuOpen(false);
                onLinkClick?.();
              }}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-xs font-semibold text-[#D4D4D8] hover:bg-[#27272A] hover:text-white"
            >
              <UserCircle className="h-4 w-4" />
              <span>Profile</span>
            </Link>
            <Link
              href="/history"
              onClick={() => {
                setIsProfileMenuOpen(false);
                onLinkClick?.();
              }}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-xs font-semibold text-[#D4D4D8] hover:bg-[#27272A] hover:text-white"
            >
              <Bell className="h-4 w-4" />
              <span>Notifications</span>
            </Link>
            <Link
              href="/analytics"
              onClick={() => {
                setIsProfileMenuOpen(false);
                onLinkClick?.();
              }}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-xs font-semibold text-[#D4D4D8] hover:bg-[#27272A] hover:text-white"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
            <button
              type="button"
              onClick={handleSignOut}
              className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-xs font-semibold text-[#D4D4D8] hover:bg-[#27272A] hover:text-white"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </button>
          </div>
        )}
        <button
          type="button"
          onClick={() => setIsProfileMenuOpen((isOpen) => !isOpen)}
          aria-expanded={isProfileMenuOpen}
          aria-label="Open planner profile menu"
          className="flex w-full items-center gap-2.5 min-w-0 rounded-lg p-1 text-left hover:bg-[#27272A] transition-colors"
        >
          <div className="relative w-8 h-8 rounded-full overflow-hidden bg-gradient-to-tr from-amber-600 to-[#FA5A16] flex items-center justify-center text-white font-bold text-xs shrink-0 border border-white/20 shadow-xs">
            <img
              src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80"
              alt="Planner profile"
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
            <span className="absolute">PK</span>
          </div>
          <div className="min-w-0">
            <p className="text-xs font-bold text-white truncate leading-tight">Planner Workspace</p>
            <p className="text-[11px] text-[#71717A] truncate font-medium">Planning & Controls</p>
          </div>
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Sidebar Component — Desktop: aside | Mobile: slide-over drawer
// ---------------------------------------------------------------------------
export function Sidebar() {
  const { isOpen, setIsOpen } = useSidebar();
  const { role } = useRoleContext();
  const isSupervisor = role === ROLES.SUPERVISOR;

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
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const SidebarBody = isSupervisor ? SupervisorSidebarContent : PlannerSidebarContent;

  return (
    <>
      {/* ===== DESKTOP: Fixed Sidebar ===== */}
      <aside
        className={`hidden md:flex w-60 border-r flex-col h-screen sticky top-0 z-30 select-none shrink-0 ${
          isSupervisor ? 'bg-[#18181B] border-[#27272A]' : 'bg-slate-900 border-slate-800'
        }`}
      >
        <SidebarBody onLinkClick={undefined} />
      </aside>

      {/* ===== MOBILE: Slide-Over Drawer ===== */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          {/* Backdrop overlay */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />

          {/* Drawer panel */}
          <div
            className={`relative flex-1 flex flex-col max-w-xs w-full shadow-2xl z-10 ${
              isSupervisor ? 'bg-[#18181B]' : 'bg-slate-900'
            }`}
          >
            {/* Close drawer button */}
            <div className="absolute top-2 right-2 z-20">
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                aria-label="Close navigation menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <SidebarBody onLinkClick={() => setIsOpen(false)} />
          </div>
        </div>
      )}
    </>
  );
}
