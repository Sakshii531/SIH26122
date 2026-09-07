import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'
import { PlannerProvider } from '@/context/PlannerContext'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'SIH26122 — Intelligent Data Capture & Schedule-Linking Layer',
  description: 'AI-Powered Planning-to-Execution Bridge for Infrastructure Project Management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`h-full bg-slate-50 ${inter.variable}`}>
      <body className="h-full font-sans text-slate-900 antialiased selection:bg-blue-600 selection:text-white bg-[#F8FAFC]">
        <AuthProvider>
          <PlannerProvider>{children}</PlannerProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
