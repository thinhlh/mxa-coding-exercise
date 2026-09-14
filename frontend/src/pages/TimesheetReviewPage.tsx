import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { WeekGrid } from '../components/WeekGrid'
import { DAYS, formatWeekStart, WEEKDAYS } from '../domain/week'
import { useSubmittedTimesheets, type ReviewOutcome } from '../hooks/useSubmittedTimesheets'
import { ApiError } from '../services/api'
import styles from './TimesheetReviewPage.module.css'

const OUTCOME_VERBS: Record<ReviewOutcome, string> = { approved: 'approve', rejected: 'reject' }

export function TimesheetReviewPage() {
  const { timesheetId } = useParams()
  const navigate = useNavigate()
  const { timesheets, loading, error, review, reviewing } = useSubmittedTimesheets()

  const [showWeekend, setShowWeekend] = useState(false)
  const [message, setMessage] = useState('')
  const [reviewError, setReviewError] = useState<string | null>(null)

  if (loading) {
    return <p>Loading the timesheet…</p>
  }

  if (error) {
    return <p role="alert">Could not load the review queue.</p>
  }

  const timesheet = timesheets.find((candidate) => candidate.id === timesheetId)

  if (!timesheetId || !timesheet) {
    return (
      <section className={styles.page}>
        <p className={styles.gone}>This timesheet is no longer waiting for review.</p>
        <Link className="btn btn-secondary" to="/review">
          Back to the queue
        </Link>
      </section>
    )
  }

  async function handleReview(outcome: ReviewOutcome) {
    setReviewError(null)
    try {
      await review(timesheetId, outcome, message.trim() || undefined)
      navigate('/review')
    } catch (caught) {
      const fallback = `could not ${OUTCOME_VERBS[outcome]} the timesheet`
      setReviewError(caught instanceof ApiError ? caught.detail : fallback)
    }
  }

  return (
    <section className={styles.page}>
      <Link className={styles.back} to="/review">
        ← Review queue
      </Link>

      <div className={styles.header}>
        <h2>{timesheet.employeeName}</h2>
        <span className="text-muted">
          Week of {formatWeekStart(timesheet.weekStart)} · {timesheet.totalHours} hours
        </span>
      </div>

      {timesheet.submitMessage && <p className={styles.submitMessage}>“{timesheet.submitMessage}”</p>}

      <label className={styles.weekendToggle}>
        <input type="checkbox" checked={showWeekend} onChange={(event) => setShowWeekend(event.target.checked)} />
        Show weekend
      </label>

      <WeekGrid
        weekStart={timesheet.weekStart}
        lineItems={timesheet.lineItems}
        days={showWeekend ? DAYS : WEEKDAYS}
        editable={false}
      />

      <div className={styles.footer}>
        <input
          type="text"
          placeholder="Message for the employee (optional)"
          className={`input ${styles.messageInput}`}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => handleReview('rejected')}
          disabled={reviewing}
        >
          Reject
        </button>
        <button type="button" className="btn btn-primary" onClick={() => handleReview('approved')} disabled={reviewing}>
          Approve
        </button>
      </div>

      {reviewError && <p className={styles.reviewError}>{reviewError}</p>}
    </section>
  )
}
