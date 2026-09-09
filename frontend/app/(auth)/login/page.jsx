'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRoleContext } from '../../../components/providers/RoleContext.jsx';

export default function LoginPage() {
  const router = useRouter();
  const { setRole } = useRoleContext();
  const [workspace, setWorkspace] = useState('planner');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleContinue = (e) => {
    e.preventDefault();
    setIsLoading(true);
    const targetRole = workspace === 'supervisor' ? 'supervisor' : 'planner';
    if (setRole) {
      setRole(targetRole);
    }
    if (typeof window !== 'undefined') {
      localStorage.setItem('sih26122_active_role', targetRole);
    }
    setTimeout(() => {
      router.push('/');
    }, 600);
  };

  return (
    <div className="min-h-screen flex bg-white">
      {/* ── Left: Hero Panel ── */}
      <div
        className="hidden lg:flex lg:w-[58%] relative flex-col justify-between overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, #1a0a00 0%, #3d1a00 30%, #7a3800 60%, #c8701a 85%, #e8a84a 100%)',
        }}
      >
        {/* Construction site background image overlay */}
        <div
          className="absolute inset-0 bg-cover bg-center mix-blend-overlay opacity-60"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=1200&auto=format&fit=crop&q=80')",
          }}
        />

        {/* Warm amber gradient overlay on top */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(160deg, rgba(20,8,0,0.55) 0%, rgba(90,40,0,0.3) 40%, rgba(200,130,30,0.15) 100%)',
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col h-full p-10 justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="bg-white rounded-md px-3 py-1.5 flex items-center gap-2 shadow-lg">
              <svg
                className="w-5 h-5"
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
          </div>

          {/* Hero Text */}
          <div className="space-y-5">
            <h1
              className="text-5xl xl:text-6xl font-black leading-[1.05] tracking-tight text-white"
              style={{ textShadow: '0 2px 24px rgba(0,0,0,0.5)' }}
            >
              TURN PROJECT
              <br />
              PLANS INTO
              <br />
              <span style={{ color: '#FA5A16' }}>PROGRESS.</span>
            </h1>
            <p className="text-sm text-white/75 font-medium leading-relaxed max-w-xs">
              Track with precision. Connect every update.
              <br />
              Make smarter project decisions.
            </p>
          </div>

          {/* Bottom branding strip */}
          <div className="flex items-center gap-4 text-white/40 text-[11px] font-mono tracking-wider">
            <span>© 2026 NIYOGEN SYSTEMS</span>
            <span>·</span>
            <span>FIELD OPERATIONS PLATFORM</span>
          </div>
        </div>
      </div>

      {/* ── Right: Login Form Panel ── */}
      <div className="flex-1 flex flex-col justify-between px-8 py-10 sm:px-14 md:px-20 lg:px-16 xl:px-24 bg-white">
        {/* Mobile logo */}
        <div className="lg:hidden mb-8 flex items-center gap-2">
          <div className="bg-black rounded-md px-2.5 py-1.5 flex items-center gap-1.5">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none">
              <path d="M6 18V6L14 18V6" stroke="#FFFFFF" strokeWidth="2.7" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M18 6V18" stroke="#FA5A16" strokeWidth="2.7" strokeLinecap="round" />
            </svg>
            <span className="font-black text-white tracking-wider text-xs">NIYOGEN</span>
          </div>
        </div>

        {/* Form area */}
        <div className="flex-1 flex flex-col justify-center max-w-sm w-full mx-auto lg:mx-0">
          {/* Heading */}
          <div className="mb-8">
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">
              WELCOME BACK.
            </h2>
            <p className="text-sm text-slate-500 mt-1.5 font-medium">
              Choose your workspace and continue.
            </p>
          </div>

          <form onSubmit={handleContinue} className="space-y-5">
            {/* Workspace Selector */}
            <div>
              <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-2">
                Select Workspace
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setWorkspace('planner')}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg border-2 text-sm font-bold transition-all cursor-pointer ${
                    workspace === 'planner'
                      ? 'border-slate-900 bg-white text-slate-900'
                      : 'border-slate-200 bg-slate-50 text-slate-500 hover:border-slate-300'
                  }`}
                >
                  <span className="tracking-wide text-xs">PLANNER</span>
                  <span
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 ${
                      workspace === 'planner'
                        ? 'border-[#FA5A16]'
                        : 'border-slate-300'
                    }`}
                  >
                    {workspace === 'planner' && (
                      <span className="w-2 h-2 rounded-full bg-[#FA5A16]" />
                    )}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setWorkspace('supervisor')}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg border-2 text-sm font-bold transition-all cursor-pointer ${
                    workspace === 'supervisor'
                      ? 'border-slate-900 bg-white text-slate-900'
                      : 'border-slate-200 bg-slate-50 text-slate-500 hover:border-slate-300'
                  }`}
                >
                  <span className="tracking-wide text-xs">SUPERVISOR</span>
                  <span
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 ${
                      workspace === 'supervisor'
                        ? 'border-[#FA5A16]'
                        : 'border-slate-300'
                    }`}
                  >
                    {workspace === 'supervisor' && (
                      <span className="w-2 h-2 rounded-full bg-[#FA5A16]" />
                    )}
                  </span>
                </button>
              </div>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="login-email"
                className="block text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-1.5"
              >
                Email
              </label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                autoComplete="email"
                className="w-full px-3.5 py-2.5 text-sm bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-400 focus:ring-1 focus:ring-slate-200 transition-all"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="login-password"
                  className="block text-[11px] font-bold text-slate-500 uppercase tracking-widest"
                >
                  Password
                </label>
                <button
                  type="button"
                  className="text-xs text-slate-500 hover:text-slate-800 font-medium transition-colors"
                >
                  Forgot password?
                </button>
              </div>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                autoComplete="current-password"
                className="w-full px-3.5 py-2.5 text-sm bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:border-slate-400 focus:ring-1 focus:ring-slate-200 transition-all"
              />
            </div>

            {/* Remember me */}
            <div className="flex items-center gap-2.5">
              <button
                type="button"
                id="remember-me-toggle"
                onClick={() => setRememberMe(!rememberMe)}
                className={`w-4 h-4 rounded flex items-center justify-center border-2 transition-all cursor-pointer shrink-0 ${
                  rememberMe
                    ? 'bg-[#FA5A16] border-[#FA5A16]'
                    : 'bg-white border-slate-300 hover:border-slate-400'
                }`}
                aria-checked={rememberMe}
                role="checkbox"
              >
                {rememberMe && (
                  <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 12 12" fill="none">
                    <path
                      d="M2 6L5 9L10 3"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </button>
              <label
                htmlFor="remember-me-toggle"
                className="text-sm text-slate-600 font-medium cursor-pointer select-none"
              >
                Remember me
              </label>
            </div>

            {/* Continue Button */}
            <button
              id="login-continue-btn"
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-lg bg-[#FA5A16] hover:bg-[#e04e10] active:bg-[#c74510] text-white text-sm font-bold tracking-widest uppercase flex items-center justify-center gap-2 transition-all shadow-md hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <>
                  <span>CONTINUE</span>
                  <span>→</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
            </div>

            {/* Google SSO */}
            <button
              id="login-google-btn"
              type="button"
              className="w-full py-3 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-semibold flex items-center justify-center gap-2.5 transition-all shadow-sm hover:shadow-md cursor-pointer"
            >
              {/* Google G Icon */}
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span>CONTINUE WITH GOOGLE</span>
            </button>
          </form>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-medium mt-8 max-w-sm w-full mx-auto lg:mx-0">
          <span className="font-black text-slate-700 tracking-wide text-xs">NIYOGEN</span>
          <div className="flex items-center gap-3">
            <button className="hover:text-slate-600 transition-colors cursor-pointer">Privacy</button>
            <span>·</span>
            <button className="hover:text-slate-600 transition-colors cursor-pointer">Terms</button>
          </div>
        </div>
      </div>
    </div>
  );
}
