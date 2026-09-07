'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authService } from '@/services/authService'
import { AuthResult, LoginCredentials } from '@/types/auth'
import { User, UserRole } from '@/types/database'

interface AuthContextType {
  user: User | null
  role: UserRole | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<AuthResult>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const loadCurrentUser = async () => {
    try {
      setIsLoading(true)
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
    } catch (err: any) {
      console.error('Error loading current user:', err)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadCurrentUser()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<AuthResult> => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await authService.signIn(credentials)
      if (result.success && result.user) {
        setUser(result.user)
      } else {
        setError(result.error || 'Authentication failed.')
      }
      return result
    } catch (err: any) {
      const errMsg = err?.message || 'Authentication error.'
      setError(errMsg)
      return { success: false, error: errMsg }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await authService.signOut()
      setUser(null)
      setError(null)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshUser = async () => {
    await loadCurrentUser()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user?.role || null,
        isAuthenticated: Boolean(user && user.role === 'Planner'),
        isLoading,
        error,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
