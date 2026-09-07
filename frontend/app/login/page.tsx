'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Building2,
  Lock,
  Mail,
  Eye,
  EyeOff,
  ShieldCheck,
  AlertCircle,
  Layers,
  TrendingUp,
  CheckCircle2,
  HardHat,
  ArrowRight,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/common/Button'
import { Input } from '@/components/common/Input'

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()

  const [email, setEmail] = useState('planner@sih26122.infrastructure.in')
  const [password, setPassword] = useState('password123')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    if (!email.trim()) {
      setErrorMessage('Please enter your work email address.')
      return
    }

    if (!password) {
      setErrorMessage('Please enter your account password.')
      return
    }

    setIsLoading(true)

    try {
      const result = await login({ email: email.trim(), password })

      if (result.success) {
        router.push('/planner/dashboard')
      } else {
        setErrorMessage(result.error || 'Invalid credentials or unauthorized account role.')
      }
    } catch (err: any) {
      setErrorMessage(err?.message || 'Authentication service error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const fillDemoAccount = () => {
    setEmail('planner@sih26122.infrastructure.in')
    setPassword('password123')
    setErrorMessage(null)
  }

  return (
    <div className="min-h-screen flex bg-[#F8FAFC]">
      {/* Left Column: Brand Context & Infrastructure Overview (Hidden on smaller screens, visible on lg+) */}
      <div className="hidden lg:flex lg:w-1/2 bg-slate-900 text-white flex-col justify-between p-12 relative overflow-hidden border-r border-slate-800">
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

        {/* Top Brand Block */}
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white shadow-md shadow-blue-900/30 font-bold">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-widest text-blue-400 block">
                SIH26122 BRIDGE
              </span>
              <span className="text-base font-bold text-white tracking-tight">
                Planning & Execution Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* Middle Feature Highlights */}
        <div className="relative z-10 space-y-6 max-w-lg my-auto">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 text-xs font-medium">
              <HardHat className="w-3.5 h-3.5 text-amber-400" />
              <span>Project Management Control</span>
            </div>
            <h1 className="text-2xl xl:text-3xl font-bold text-white tracking-tight leading-snug">
              Intelligent Data Capture & Schedule-Linking Layer
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Connects daily site progress reports (DPR, Voice, Excel, PDF) with planned L5/L6 schedule activities using human-in-the-loop AI validation.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-800/80">
            <div className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-1">
              <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs">
                <Layers className="w-4 h-4" />
                <span>L5/L6 Matching</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Semantic linking to Primavera P6 & MS Project WBS
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-1">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                <CheckCircle2 className="w-4 h-4" />
                <span>Planner Review</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Audited verification of uncertain matches & evidence
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Status Info */}
        <div className="relative z-10 pt-6 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Enterprise Project Security</span>
          <span className="flex items-center gap-1.5 text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
            Supabase RBAC Verified
          </span>
        </div>
      </div>

      {/* Right Column: Authentication Form Panel */}
      <div className="flex-1 flex flex-col justify-center py-10 px-4 sm:px-8 lg:px-16 xl:px-24">
        <div className="mx-auto w-full max-w-md">
          {/* Mobile Brand Header */}
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white shadow-xs mb-3">
              <Building2 className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              SIH26122 Planner Portal
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Planning-to-Execution Bridge for Infrastructure Projects
            </p>
          </div>

          {/* Form Header */}
          <div className="mb-6">
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Planner Sign In
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Enter your credentials to access the project planning & review console.
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-card space-y-5">
            <form onSubmit={handleSubmit} className="space-y-4">
              {errorMessage && (
                <div
                  className="p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-xs text-rose-800"
                  role="alert"
                >
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <div>
                <Input
                  label="Work Email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="planner@infrastructure.in"
                  leftIcon={<Mail className="w-4 h-4" />}
                  autoComplete="email"
                />
              </div>

              <div>
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  leftIcon={<Lock className="w-4 h-4" />}
                  rightIcon={
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-slate-400 hover:text-slate-600 focus:outline-none p-0.5"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  }
                  autoComplete="current-password"
                />
              </div>

              <div className="pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  className="w-full bg-blue-600 hover:bg-blue-700 border-blue-600"
                  size="md"
                  isLoading={isLoading}
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                >
                  Sign In to Planner Portal
                </Button>
              </div>
            </form>

            {/* Demo Access Card */}
            <div className="pt-4 border-t border-slate-100">
              <div className="p-3 bg-slate-50 border border-slate-200/80 rounded-lg flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                    Quick Demo Access
                  </span>
                  <p className="text-[11px] font-mono text-slate-700 truncate mt-0.5">
                    planner@sih26122.infrastructure.in
                  </p>
                </div>
                <button
                  type="button"
                  onClick={fillDemoAccount}
                  className="px-2.5 py-1 text-xs font-semibold text-blue-700 hover:text-blue-800 hover:bg-blue-50 rounded border border-blue-200 transition-colors shrink-0"
                >
                  Autofill
                </button>
              </div>
            </div>
          </div>

          {/* Footer Security Note */}
          <div className="mt-6 text-center text-[11px] text-slate-400">
            Role-Based Access Control enforced. Supervisor accounts must use the field reporting application.
          </div>
        </div>
      </div>
    </div>
  )
}
