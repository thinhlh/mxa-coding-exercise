import { useCallback, useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { weekStartFor } from '../domain/week'
import { getTimesheetForWeek, writeTimesheet } from '../services/timesheets'
import type { LineItemInput, Timesheet, TimesheetStatus } from '../types/timesheet'

const WEEK_SECONDS = 7 * 24 * 60 * 60

function currentWeekAt(): number {
  return Math.floor(Date.now() / 1000)
}

interface UseTimesheetWeekResult {
  timesheet: Timesheet | null
  loading: boolean
  error: unknown
  weekAt: number
  canGoToNextWeek: boolean
  goToPreviousWeek: () => void
  goToNextWeek: () => void
  goToThisWeek: () => void
  save: (lineItems: LineItemInput[], options?: { submit?: boolean; message?: string }) => Promise<Timesheet>
  saving: boolean
}

// One editable timesheet week: loads it on `weekAt` change, and writes it into `draft` or `submitted`.
export function useTimesheetWeek(): UseTimesheetWeekResult {
  const { user } = useAuth()
  const token = user?.access_token
  const [weekAt, setWeekAt] = useState(() => Math.floor(Date.now() / 1000))
  const [timesheet, setTimesheet] = useState<Timesheet | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    getTimesheetForWeek(token, weekAt)
      .then((result) => {
        if (!cancelled) setTimesheet(result)
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
  }, [token, weekAt])

  const save = useCallback(
    async (lineItems: LineItemInput[], options?: { submit?: boolean; message?: string }): Promise<Timesheet> => {
      if (!token) throw new Error('not signed in')
      const targetStatus: TimesheetStatus = options?.submit ? 'submitted' : 'draft'
      setSaving(true)
      try {
        const result = await writeTimesheet(token, targetStatus, {
          at: weekAt,
          lineItems,
          message: options?.message,
        })
        setTimesheet(result)
        return result
      } finally {
        setSaving(false)
      }
    },
    [token, weekAt],
  )

  const canGoToNextWeek = weekStartFor(weekAt).getTime() < weekStartFor(currentWeekAt()).getTime()

  return {
    timesheet,
    loading,
    error,
    weekAt,
    canGoToNextWeek,
    goToPreviousWeek: () => setWeekAt((at) => at - WEEK_SECONDS),
    goToNextWeek: () => setWeekAt((at) => (canGoToNextWeek ? at + WEEK_SECONDS : at)),
    goToThisWeek: () => setWeekAt(currentWeekAt()),
    save,
    saving,
  }
}
