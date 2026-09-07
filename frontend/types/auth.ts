import { User, UserRole } from './database'

export interface AuthState {
  user: User | null
  supabaseUserId: string | null
  role: UserRole | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResult {
  success: boolean
  user?: User
  role?: UserRole
  error?: string
}
