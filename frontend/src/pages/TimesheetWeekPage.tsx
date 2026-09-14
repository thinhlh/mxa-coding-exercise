import { useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { AddLineItemForm } from '../components/AddLineItemForm'
import { WeekGrid } from '../components/WeekGrid'
import { dailyTotals, daysOverLimit } from '../domain/hours'
import { DAYS, isBeforeCurrentWeek, WEEKDAYS } from '../domain/week'
import { useTimesheetWeek } from '../hooks/useTimesheetWeek'
import { ApiError } from '../services/api'
import type { Me } from '../types/me'
import type { LineItem, LineItemInput } from '../types/timesheet'
import styles from './TimesheetWeekPage.module.css'

interface TimesheetWeekPageProps {
  me: Me
}

const WEEK_LABEL_FORMAT = new Intl.DateTimeFormat(undefined, {
  month: 'long',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
})

function toInputs(lineItems: LineItem[]): LineItemInput[] {
  return lineItems.map((item) => ({ projectCode: item.projectCode, hours: item.hours }))
}

function errorMessage(caught: unknown, fallback: string): string {
  return caught instanceof ApiError ? caught.detail : fallback
}

export function TimesheetWeekPage({ me }: TimesheetWeekPageProps) {
  const { user } = useAuth()
  const token = user?.access_token
  const { timesheet, loading, error, canGoToNextWeek, goToPreviousWeek, goToNextWeek, goToThisWeek, save, saving } =
    useTimesheetWeek()

  const [lineItems, setLineItems] = useState<LineItem[]>([])
  const [showWeekend, setShowWeekend] = useState(false)
  const [message, setMessage] = useState('')
  const [saveError, setSaveError] = useState<string | null>(null)

  useEffect(() => {
    if (timesheet) {
      setLineItems(timesheet.lineItems)
      setMessage(timesheet.submitMessage ?? '')
      setSaveError(null)
    }
  }, [timesheet])

  if (loading && !timesheet) {
    return <p>Loading your timesheet…</p>
  }

  if (error || !timesheet) {
    return <p role="alert">Could not load your timesheet.</p>
  }

  // An unsaved past week can't become a new draft; a week already saved as draft or
  // rejected stays editable no matter how far in the past it is.
  const editable =
    timesheet.id !== null
      ? timesheet.status === 'draft' || timesheet.status === 'rejected'
      : !isBeforeCurrentWeek(timesheet.weekStart)
  const days = showWeekend ? DAYS : WEEKDAYS
  const totals = dailyTotals(lineItems.map((item) => item.hours))
  const overLimitDays = Object.entries(daysOverLimit(totals))

  async function handleSave() {
    setSaveError(null)
    try {
      await save(toInputs(lineItems))
    } catch (caught) {
      setSaveError(errorMessage(caught, 'could not save the timesheet'))
    }
  }

  async function handleSubmit() {
    setSaveError(null)
    try {
      await save(toInputs(lineItems), { submit: true, message: message.trim() || undefined })
    } catch (caught) {
      setSaveError(errorMessage(caught, 'could not submit the timesheet'))
    }
  }

  return (
    <section className={styles.page}>
      <div className={styles.header}>
        <h2>Your timesheet — {me.displayName}</h2>
        <div className={styles.nav}>
          <button type="button" className={styles.navButton} onClick={goToPreviousWeek}>
            ← Previous
          </button>
          <span className={styles.weekLabel}>
            Week of {WEEK_LABEL_FORMAT.format(new Date(`${timesheet.weekStart}T00:00:00Z`))}
          </span>
          <button type="button" className={styles.navButton} onClick={goToThisWeek}>
            This week
          </button>
          <button type="button" className={styles.navButton} onClick={goToNextWeek} disabled={!canGoToNextWeek}>
            Next →
          </button>
        </div>
      </div>

      {timesheet.id === null && isBeforeCurrentWeek(timesheet.weekStart) && (
        <p className={styles.banner}>This week is in the past and was never filled in — read-only.</p>
      )}
      {timesheet.status === 'submitted' && <p className={styles.banner}>Submitted — read-only until reviewed.</p>}
      {timesheet.status === 'approved' && <p className={styles.banner}>Approved — read-only.</p>}
      {timesheet.status === 'rejected' && (
        <p className={`${styles.banner} ${styles.rejectedBanner}`}>
          Rejected{timesheet.reviewMessage ? `: ${timesheet.reviewMessage}` : ''}. Edit and resubmit below.
        </p>
      )}

      <label className={styles.weekendToggle}>
        <input type="checkbox" checked={showWeekend} onChange={(event) => setShowWeekend(event.target.checked)} />
        Show weekend
      </label>

      <WeekGrid
        weekStart={timesheet.weekStart}
        lineItems={lineItems}
        days={days}
        editable={editable}
        onHoursChange={(index, day, value) =>
          setLineItems((items) =>
            items.map((item, i) => (i === index ? { ...item, hours: { ...item.hours, [day]: value } } : item)),
          )
        }
        onRemoveLineItem={(index) => setLineItems((items) => items.filter((_, i) => i !== index))}
      />

      {editable && token && (
        <AddLineItemForm
          token={token}
          existingCodes={lineItems.map((item) => item.projectCode)}
          onAdd={(lineItem) => setLineItems((items) => [...items, lineItem])}
        />
      )}

      {editable && (
        <div className={styles.footer}>
          <input
            type="text"
            placeholder="Message for your manager (optional)"
            className={styles.messageInput}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />
          <button type="button" className={styles.secondaryButton} onClick={handleSave} disabled={saving}>
            Save
          </button>
          <button
            type="button"
            className={styles.button}
            onClick={handleSubmit}
            disabled={saving || overLimitDays.length > 0}
          >
            Submit
          </button>
        </div>
      )}

      {overLimitDays.length > 0 && (
        <p className={styles.overLimitError}>
          {overLimitDays.map(([day, total]) => `${day} is at ${total} hours — a day cannot exceed 24`).join('; ')}
        </p>
      )}
      {saveError && <p className={styles.saveError}>{saveError}</p>}
    </section>
  )
}
