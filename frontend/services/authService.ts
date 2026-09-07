import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase/client'
import { AuthResult, LoginCredentials } from '@/types/auth'
import { User, UserRole } from '@/types/database'

const FALLBACK_PLANNER_USER: User = {
  id: 'usr-pln-01',
  user_id: 'demo-planner-auth-id',
  email: 'planner@sih26122.infrastructure.in',
  full_name: 'Vikram Mehta',
  role: 'Planner',
  discipline: 'Planning & Controls',
  project_id: 'proj-001',
  created_at: '2026-08-01T00:00:00Z',
  updated_at: '2026-09-01T00:00:00Z',
}

const LOCAL_SESSION_KEY = 'sih26122_planner_auth_session'

export const authService = {
  async signIn(credentials: LoginCredentials): Promise<AuthResult> {
    const { email, password } = credentials

    if (!email || !password) {
      return { success: false, error: 'Please provide both email and password.' }
    }

    const supabase = getSupabaseClient()

    if (supabase) {
      try {
        const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (authError || !authData.user) {
          return {
            success: false,
            error: authError?.message || 'Invalid email or password.',
          }
        }

        const supabaseUserId = authData.user.id

        // Query the existing users table to determine role
        const { data: userData, error: userError } = await supabase
          .from('users')
          .select('id, user_id, email, full_name, role, discipline, project_id, created_at, updated_at')
          .eq('user_id', supabaseUserId)
          .single()

        if (userError || !userData) {
          // If no row in users table or no role assigned
          return {
            success: false,
            error: 'Your account is not assigned to a valid role in the system.',
          }
        }

        const role = userData.role as UserRole

        if (role !== 'Planner') {
          if (role === 'Supervisor') {
            return {
              success: false,
              error: 'Supervisor accounts cannot access the Planner Portal.',
            }
          }
          return {
            success: false,
            error: 'Your account is not assigned to a valid role.',
          }
        }

        const userObj: User = {
          id: userData.id,
          user_id: userData.user_id,
          email: userData.email || email,
          full_name: userData.full_name || 'Planner User',
          role: role,
          discipline: userData.discipline,
          project_id: userData.project_id,
          created_at: userData.created_at,
          updated_at: userData.updated_at,
        }

        if (typeof window !== 'undefined') {
          localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(userObj))
        }

        return {
          success: true,
          user: userObj,
          role: role,
        }
      } catch (err: any) {
        return {
          success: false,
          error: err?.message || 'An unexpected error occurred during authentication.',
        }
      }
    }

    // Graceful fallback for local development / testing without live Supabase credentials
    // Verify standard credentials format
    if (email.toLowerCase().includes('planner') || email === 'planner@sih26122.infrastructure.in') {
      const demoUser: User = {
        ...FALLBACK_PLANNER_USER,
        email: email,
      }
      if (typeof window !== 'undefined') {
        localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(demoUser))
      }
      return {
        success: true,
        user: demoUser,
        role: 'Planner',
      }
    }

    if (email.toLowerCase().includes('supervisor')) {
      return {
        success: false,
        error: 'Supervisor accounts cannot access the Planner Portal.',
      }
    }

    if (password === 'password' || password === 'planner123' || password.length >= 6) {
      const demoUser: User = {
        ...FALLBACK_PLANNER_USER,
        email: email,
        full_name: email.split('@')[0].replace('.', ' ').toUpperCase(),
      }
      if (typeof window !== 'undefined') {
        localStorage.setItem(LOCAL_SESSION_KEY, JSON.stringify(demoUser))
      }
      return {
        success: true,
        user: demoUser,
        role: 'Planner',
      }
    }

    return {
      success: false,
      error: 'Invalid email or password. (Hint: Use planner@sih26122.infrastructure.in or password with >= 6 characters)',
    }
  },

  async getCurrentUser(): Promise<User | null> {
    const supabase = getSupabaseClient()

    if (supabase) {
      try {
        const { data: { user: authUser } } = await supabase.auth.getUser()
        if (authUser) {
          const { data: userData } = await supabase
            .from('users')
            .select('id, user_id, email, full_name, role, discipline, project_id, created_at, updated_at')
            .eq('user_id', authUser.id)
            .single()

          if (userData && userData.role === 'Planner') {
            return {
              id: userData.id,
              user_id: userData.user_id,
              email: userData.email,
              full_name: userData.full_name,
              role: userData.role,
              discipline: userData.discipline,
              project_id: userData.project_id,
              created_at: userData.created_at,
              updated_at: userData.updated_at,
            }
          }
        }
      } catch (err) {
        console.warn('Supabase auth session check failed:', err)
      }
    }

    if (typeof window !== 'undefined') {
      const sessionStr = localStorage.getItem(LOCAL_SESSION_KEY)
      if (sessionStr) {
        try {
          return JSON.parse(sessionStr) as User
        } catch {
          return null
        }
      }
    }

    return null
  },

  async signOut(): Promise<void> {
    const supabase = getSupabaseClient()
    if (supabase) {
      try {
        await supabase.auth.signOut()
      } catch (err) {
        console.warn('Supabase sign out error:', err)
      }
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem(LOCAL_SESSION_KEY)
    }
  },
}
