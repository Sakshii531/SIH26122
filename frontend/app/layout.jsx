import './globals.css';
import { Sidebar } from '../components/layout/Sidebar.jsx';
import { TopNav } from '../components/layout/TopNav.jsx';
import { AppProviders } from '../components/providers/AppProviders.jsx';

export const metadata = {
  title: 'SIH26122 – Intelligent Schedule-Linking & Data Capture System',
  description: 'AI-Powered Planning-to-Execution Bridge for Infrastructure Project Progress Tracking'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-800 overflow-x-hidden">
        {/*
          AppProviders is a 'use client' boundary that wraps RoleProvider +
          SidebarProvider. Sidebar and TopNav are client components that consume
          these contexts; they are rendered inside AppProviders so they receive
          the context values correctly.
        */}
        <AppProviders>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
              <TopNav />
              <main className="flex-1 p-4 md:p-6 overflow-y-auto">
                {children}
              </main>
            </div>
          </div>
        </AppProviders>
      </body>
    </html>
  );
}
