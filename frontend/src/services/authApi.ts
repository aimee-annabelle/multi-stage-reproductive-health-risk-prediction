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

type BackendAuthUser = {
  id: number
  full_name: string
  email: string
  created_at: string
}

type BackendAuthResponse = {
  access_token: string
  token_type: string
  expires_in: number
  user: BackendAuthUser
}

const API_BASE = (import.meta.env.VITE_API_URL || '').trim() || 'http://localhost:8000'
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
    },
  } satisfies AuthResponse
}

function mapBackendAuthResponse(payload: BackendAuthResponse): AuthResponse {
  return {
    token: payload.access_token,
    user: {
      id: String(payload.user.id),
      fullName: payload.user.full_name,
      email: payload.user.email,
    },
  }
}

async function parseApiError(response: Response, fallbackMessage: string): Promise<never> {
  let message = fallbackMessage
  try {
    const body = (await response.json()) as { detail?: string }
    if (typeof body?.detail === 'string' && body.detail.trim()) {
      message = body.detail
    }
  } catch {
    // Ignore response parsing errors and use fallback.
  }
  throw new Error(message)
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
    await parseApiError(response, 'Unable to login. Please verify your credentials.')
  }

  const payload = (await response.json()) as BackendAuthResponse
  return mapBackendAuthResponse(payload)
}

export async function signupRequest(fullName: string, email: string, password: string): Promise<AuthResponse> {
  if (USE_MOCK) {
    if (!fullName || !email || !password) {
      throw new Error('Full name, email, and password are required.')
    }
    return mockLogin(email, fullName)
  }

  const response = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, email, password }),
  })

  if (!response.ok) {
    await parseApiError(response, 'Unable to create account right now.')
  }

  const payload = (await response.json()) as BackendAuthResponse
  return mapBackendAuthResponse(payload)
}
