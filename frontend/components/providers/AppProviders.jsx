'use client';

/**
 * AppProviders — single client boundary that wraps all context providers.
 *
 * layout.jsx is a Server Component, which cannot directly render client-only
 * hooks/context. By isolating all providers here behind 'use client', Next.js
 * treats this subtree as a client component tree while layout.jsx stays a
 * server component responsible only for metadata and the HTML shell.
 */

import React from 'react';
import { RoleProvider } from './RoleContext.jsx';
import { SidebarProvider } from '../layout/Sidebar.jsx';

export function AppProviders({ children }) {
  return (
    <RoleProvider>
      <SidebarProvider>
        {children}
      </SidebarProvider>
    </RoleProvider>
  );
}
