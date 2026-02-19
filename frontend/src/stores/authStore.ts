import { create } from 'zustand'
import { loginRequest, signupRequest, type AuthUser } from '../services/authApi'

type AuthState = {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => void
  clearError: () => void
}

const TOKEN_KEY = 'natalis_auth_token'
const USER_KEY = 'natalis_auth_user'

function readSession() {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const rawUser = localStorage.getItem(USER_KEY)
    const user = rawUser ? (JSON.parse(rawUser) as AuthUser) : null

    return { token, user }
  } catch {
    return { token: null, user: null }
  }
}

const session = readSession()

export const useAuthStore = create<AuthState>((set) => ({
  token: session.token,
  user: session.user,
  isAuthenticated: Boolean(session.token && session.user),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await loginRequest(email, password)
      localStorage.setItem(TOKEN_KEY, response.token)
      localStorage.setItem(USER_KEY, JSON.stringify(response.user))
      set({
        token: response.token,
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to login.',
      })
      throw error
    }
  },

  signup: async (fullName, email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await signupRequest(fullName, email, password)
      localStorage.setItem(TOKEN_KEY, response.token)
      localStorage.setItem(USER_KEY, JSON.stringify(response.user))
      set({
        token: response.token,
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create account.',
      })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    set({ token: null, user: null, isAuthenticated: false, error: null })
  },

  clearError: () => set({ error: null }),
}))
