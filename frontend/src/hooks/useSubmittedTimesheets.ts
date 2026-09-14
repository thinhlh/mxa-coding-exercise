import { useCallback, useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { listTimesheetsByStatus, writeTimesheet } from '../services/timesheets'
import type { Timesheet } from '../types/timesheet'

export type ReviewOutcome = 'approved' | 'rejected'

interface UseSubmittedTimesheetsResult {
  timesheets: Timesheet[]
  loading: boolean
  error: unknown
  review: (timesheetId: string, outcome: ReviewOutcome, message?: string) => Promise<Timesheet>
  reviewing: boolean
}

// The review queue. The submitted list carries whole timesheets, so a reviewer reads one
// from the same response the queue was drawn from; approving or rejecting drops it from
// the list, which is how it leaves the queue.
export function useSubmittedTimesheets(): UseSubmittedTimesheetsResult {
  const { user } = useAuth()
  const token = user?.access_token
  const [timesheets, setTimesheets] = useState<Timesheet[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [reviewing, setReviewing] = useState(false)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    listTimesheetsByStatus(token, 'submitted')
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
  }, [token])

  const review = useCallback(
    async (timesheetId: string, outcome: ReviewOutcome, message?: string): Promise<Timesheet> => {
      if (!token) throw new Error('not signed in')
      setReviewing(true)
      try {
        const reviewed = await writeTimesheet(token, outcome, { timesheetId, message })
        setTimesheets((current) => current.filter((timesheet) => timesheet.id !== timesheetId))
        return reviewed
      } finally {
        setReviewing(false)
      }
    },
    [token],
  )

  return { timesheets, loading, error, review, reviewing }
}
