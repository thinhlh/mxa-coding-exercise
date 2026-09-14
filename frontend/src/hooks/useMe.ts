import { useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { apiFetch } from '../services/api'
import type { Me } from '../types/me'

interface UseMeResult {
  me: Me | null
  loading: boolean
  error: unknown
}

export function useMe(): UseMeResult {
  const { user } = useAuth()
  const token = user?.access_token
  const [me, setMe] = useState<Me | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    apiFetch<Me>('/me', { token })
      .then((result) => {
        if (!cancelled) setMe(result)
      })
      .catch((caught: unknown) => {
        if (!cancelled) setError(caught)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [token])

  return { me, loading, error }
}
