import { Link } from 'react-router-dom'
import { flaggedDays } from '../domain/hours'
import { formatWeekStart } from '../domain/week'
import { useSubmittedTimesheets } from '../hooks/useSubmittedTimesheets'
import type { Me } from '../types/me'
import type { Timesheet } from '../types/timesheet'
import styles from './ReviewQueuePage.module.css'

interface ReviewQueuePageProps {
  me: Me
}

function FlaggedDaysCell({ timesheet }: { timesheet: Timesheet }) {
  const flagged = flaggedDays(timesheet.dailyTotals)

  if (flagged.length === 0) {
    return <span className="text-muted">None</span>
  }

  return <span className={styles.flaggedDays}>{flagged.map((day) => day.slice(0, 3)).join(', ')}</span>
}

export function ReviewQueuePage({ me }: ReviewQueuePageProps) {
  const { timesheets, loading, error } = useSubmittedTimesheets()

  return (
    <section className={styles.page}>
      <div className={styles.header}>
        <h2>Review queue</h2>
        <span className="text-muted">Manager: {me.displayName}</span>
      </div>

      {loading && <p>Loading submitted timesheets…</p>}
      {error && <p role="alert">Could not load the review queue.</p>}

      {!loading && !error && timesheets.length === 0 && (
        <p className={styles.empty}>Nothing to review — no timesheet is waiting.</p>
      )}

      {timesheets.length > 0 && (
        <div className={styles.wrapper}>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Employee</th>
                <th scope="col">Week</th>
                <th scope="col">Total hours</th>
                <th scope="col">Flagged days</th>
                <th scope="col">Message</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {timesheets.map((timesheet) => (
                <tr key={timesheet.id}>
                  <td className={styles.employee}>{timesheet.employeeName}</td>
                  <td className={styles.week}>{formatWeekStart(timesheet.weekStart)}</td>
                  <td>{timesheet.totalHours}</td>
                  <td>
                    <FlaggedDaysCell timesheet={timesheet} />
                  </td>
                  <td className="text-muted">{timesheet.submitMessage ?? '—'}</td>
                  <td className={styles.action}>
                    <Link className="btn btn-secondary" to={`/review/${timesheet.id}`}>
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={styles.legend}>A flagged day is a weekday that does not total 8 hours.</p>
        </div>
      )}
    </section>
  )
}
