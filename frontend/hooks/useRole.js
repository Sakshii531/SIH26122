'use client';

/**
 * useRole — Lightweight frontend-only role simulation hook.
 *
 * In production this would be replaced by an auth context (e.g. NextAuth session).
 * For now it reads/writes to localStorage so the role persists across page navigations
 * within the same browser session.
 *
 * Roles:
 *   'planner'   — Planner: full schedule + verification access
 *   'manager'   — Project/Planning Manager: read-only analytics + all views
 *   'worker'    — Site/Field Worker: capture + submission only
 *   'admin'     — Admin: all access including audit trail
 */

import { useState, useCallback, useEffect } from 'react';

export const ROLES = {
  PLANNER: 'planner',
  MANAGER: 'manager',
  WORKER: 'worker',
  ADMIN: 'admin',
};

export const ROLE_LABELS = {
  planner: 'Planner',
  manager: 'Planning Manager',
  worker: 'Site Engineer',
  admin: 'Admin',
};

export const ROLE_PERMISSIONS = {
  planner: {
    canVerify: true,
    canViewSchedule: true,
    canCapture: true,
    canViewAnalytics: true,
    canViewAudit: false,
    canViewAdmin: false,
  },
  manager: {
    canVerify: false,
    canViewSchedule: true,
    canCapture: false,
    canViewAnalytics: true,
    canViewAudit: true,
    canViewAdmin: false,
  },
  worker: {
    canVerify: false,
    canViewSchedule: false,
    canCapture: true,
    canViewAnalytics: false,
    canViewAudit: false,
    canViewAdmin: false,
  },
  admin: {
    canVerify: true,
    canViewSchedule: true,
    canCapture: true,
    canViewAnalytics: true,
    canViewAudit: true,
    canViewAdmin: true,
  },
};

const STORAGE_KEY = 'sih26122_active_role';

export function useRole() {
  const [role, setRoleState] = useState(ROLES.PLANNER);

  // Hydrate from localStorage on mount (client only)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && ROLES[stored.toUpperCase()]) {
        setRoleState(stored);
      }
    }
  }, []);

  const setRole = useCallback((newRole) => {
    if (Object.values(ROLES).includes(newRole)) {
      setRoleState(newRole);
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, newRole);
      }
    }
  }, []);

  const permissions = ROLE_PERMISSIONS[role] ?? ROLE_PERMISSIONS.planner;

  return { role, setRole, permissions, label: ROLE_LABELS[role] };
}
