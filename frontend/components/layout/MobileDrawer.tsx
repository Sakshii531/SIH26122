'use client'

import React, { useEffect } from 'react'
import { X } from 'lucide-react'
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
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed inset-y-0 left-0 flex max-w-full z-10">
        <div className="relative flex w-64 max-w-xs flex-col bg-slate-900 shadow-xl">
          <button
            onClick={onClose}
            className="absolute top-4 right-3 z-20 rounded-md p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
          <PlannerSidebar onCloseMobile={onClose} />
        </div>
      </div>
    </div>
  )
}
