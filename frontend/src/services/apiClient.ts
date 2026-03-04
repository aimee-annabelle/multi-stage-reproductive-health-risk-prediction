import { useAuthStore } from '../stores/authStore'

export const API_BASE = (import.meta.env.VITE_API_URL || '').trim() || 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function readErrorMessageFromPayload(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  if ('detail' in payload && typeof payload.detail === 'string' && payload.detail.trim()) {
    return payload.detail
  }

  if ('message' in payload && typeof payload.message === 'string' && payload.message.trim()) {
    return payload.message
  }

  return null
}

async function parseApiError(response: Response, fallbackMessage: string): Promise<never> {
  let message = fallbackMessage

  try {
    const payload = (await response.json()) as unknown
    const extracted = readErrorMessageFromPayload(payload)
    if (extracted) {
      message = extracted
    }
  } catch {
    try {
      const text = await response.text()
      if (text.trim()) {
        message = text
      }
    } catch {
      // Ignore secondary parsing failures.
    }
  }

  throw new ApiError(message, response.status)
}

export async function requestJson<T>(
  path: string,
  init: RequestInit,
  fallbackMessage: string,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)

  if (!response.ok) {
    await parseApiError(response, fallbackMessage)
  }

  return (await response.json()) as T
}

export function getAuthToken(): string | null {
  const stateToken = useAuthStore.getState().token
  if (stateToken) {
    return stateToken
  }

  try {
    return localStorage.getItem('natalis_auth_token')
  } catch {
    return null
  }
}
