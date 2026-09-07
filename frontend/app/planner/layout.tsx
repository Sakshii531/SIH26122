'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { PlannerSidebar } from '@/components/layout/PlannerSidebar'
import { PlannerTopNav } from '@/components/layout/PlannerTopNav'
import { MobileDrawer } from '@/components/layout/MobileDrawer'
import { Loader2 } from 'lucide-react'

export default function PlannerLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false)
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    // If auth checking has finished and no user exists, redirect to login
    // Note: In development/demo, AuthContext automatically provides demo planner session if not configured
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p className="text-xs font-medium text-slate-500">
            Verifying Planner credentials...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Desktop Fixed Sidebar */}
      <div className="hidden lg:flex lg:shrink-0">
        <PlannerSidebar />
      </div>

      {/* Mobile Drawer */}
      <MobileDrawer
        isOpen={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        <PlannerTopNav onToggleMobile={() => setMobileDrawerOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  )
}
