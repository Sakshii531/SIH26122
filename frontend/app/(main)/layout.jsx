'use client';

import React, { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { Sidebar } from '../../components/layout/Sidebar.jsx';
import { TopNav } from '../../components/layout/TopNav.jsx';
import { useRoleContext } from '../../components/providers/RoleContext.jsx';
import { ROLES } from '../../hooks/useRole.js';

const SUPERVISOR_ALLOWED_ROUTES = ['/', '/capture'];

export default function MainLayout({ children }) {
  const pathname = usePathname();
  const router = useRouter();
  const { role } = useRoleContext();

  const isSupervisor = role === ROLES.SUPERVISOR;

  useEffect(() => {
    if (isSupervisor && !SUPERVISOR_ALLOWED_ROUTES.includes(pathname)) {
      router.replace('/');
    }
  }, [isSupervisor, pathname, router]);

  if (isSupervisor && !SUPERVISOR_ALLOWED_ROUTES.includes(pathname)) {
    return null;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <TopNav />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
