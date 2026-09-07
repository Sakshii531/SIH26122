'use client'

import React, { useEffect } from 'react'
import { PlannerSidebar } from './PlannerSidebar'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function MobileDrawer({ isOpen, onClose }: MobileDrawerProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-[2px] animate-fade-in"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar Panel */}
      <div className="fixed inset-y-0 left-0 z-10 flex animate-slide-in-left">
        <div className="relative flex w-64 flex-col shadow-panel">
          <PlannerSidebar onCloseMobile={onClose} />
        </div>
      </div>
    </div>
  )
}
