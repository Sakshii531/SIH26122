'use client';

/**
 * RoleContext — React context that wraps the entire app shell so that
 * Sidebar, TopNav, and any page component can read / switch the active role
 * without prop-drilling.
 */

import React, { createContext, useContext } from 'react';
import { useRole } from '../../hooks/useRole.js';

const RoleContext = createContext(null);

export function RoleProvider({ children }) {
  const roleState = useRole();
  return (
    <RoleContext.Provider value={roleState}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRoleContext() {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRoleContext must be used within <RoleProvider>');
  return ctx;
}
