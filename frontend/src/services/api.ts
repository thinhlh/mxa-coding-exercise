export class ApiError extends Error {
  readonly status: number
  readonly detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

// `||`, not `??`: docker compose passes an empty string for a variable its
// `.env` never set, and an empty base URL would post to the Vite dev server.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface ApiFetchOptions extends RequestInit {
  token: string
}

async function readDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    return typeof body.detail === 'string' ? body.detail : 'request failed'
  } catch {
    return 'request failed'
  }
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions): Promise<T> {
  const { token, headers, ...init } = options

  const response = await fetch(`${API_BASE_URL}/api${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(response.status, await readDetail(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
