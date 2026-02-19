export type AuthUser = {
  id: string
  fullName: string
  email: string
  avatarUrl?: string
}

export type AuthResponse = {
  token: string
  user: AuthUser
}

const API_BASE = import.meta.env.VITE_API_URL?.toString().trim() || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK_AUTH !== 'false'

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function mockLogin(email: string, fullName = 'Sarah') {
  await wait(500)

  return {
    token: `mock-token-${Date.now()}`,
    user: {
      id: 'user-1',
      fullName,
      email,
      avatarUrl: 'https://i.pravatar.cc/100?img=32',
    },
  } satisfies AuthResponse
}

export async function loginRequest(email: string, password: string): Promise<AuthResponse> {
  if (USE_MOCK) {
    if (!email || !password) {
      throw new Error('Email and password are required.')
    }
    return mockLogin(email)
  }

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    throw new Error('Unable to login. Please verify your credentials.')
  }

  return (await response.json()) as AuthResponse
}

export async function signupRequest(fullName: string, email: string, password: string): Promise<AuthResponse> {
  if (USE_MOCK) {
    if (!fullName || !email || !password) {
      throw new Error('Full name, email, and password are required.')
    }
    return mockLogin(email, fullName)
  }

  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fullName, email, password }),
  })

  if (!response.ok) {
    throw new Error('Unable to create account right now.')
  }

  return (await response.json()) as AuthResponse
}
