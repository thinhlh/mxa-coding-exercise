import { useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { listTimesheetsByStatus } from '../services/timesheets'
import type { Timesheet } from '../types/timesheet'

interface UseProjectTimesheetsResult {
  timesheets: Timesheet[]
  loading: boolean
  error: unknown
}

// The submitted timesheets that carry a line item for one project — reached by a manager
// clicking into a project from their project list.
export function useProjectTimesheets(projectId: string | undefined): UseProjectTimesheetsResult {
  const { user } = useAuth()
  const token = user?.access_token
  const [timesheets, setTimesheets] = useState<Timesheet[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    if (!token || !projectId) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    listTimesheetsByStatus(token, 'submitted', projectId)
      .then((result) => {
        if (!cancelled) setTimesheets(result)
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
  }, [token, projectId])

  return { timesheets, loading, error }
}
