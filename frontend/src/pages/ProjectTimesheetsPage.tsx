import { Link, useParams } from 'react-router-dom'
import { flaggedDays } from '../domain/hours'
import { formatWeekStart } from '../domain/week'
import { useProjectTimesheets } from '../hooks/useProjectTimesheets'
import { useProjects } from '../hooks/useProjects'
import type { Me } from '../types/me'
import type { Timesheet } from '../types/timesheet'
import styles from './ProjectTimesheetsPage.module.css'

interface ProjectTimesheetsPageProps {
  me: Me
}

function FlaggedDaysCell({ timesheet }: { timesheet: Timesheet }) {
  const flagged = flaggedDays(timesheet.dailyTotals)

  if (flagged.length === 0) {
    return <span className="text-muted">None</span>
  }

  return <span className={styles.flaggedDays}>{flagged.map((day) => day.slice(0, 3)).join(', ')}</span>
}

export function ProjectTimesheetsPage({ me }: ProjectTimesheetsPageProps) {
  const { projectId } = useParams()
  const { projects, loading: projectsLoading } = useProjects()
  const { timesheets, loading, error } = useProjectTimesheets(projectId)

  const project = projects.find((candidate) => candidate.id === projectId)

  if (!projectsLoading && !project) {
    return (
      <section className={styles.page}>
        <p className={styles.gone}>This project could not be found.</p>
        <Link className="btn btn-secondary" to="/projects">
          Back to projects
        </Link>
      </section>
    )
  }

  return (
    <section className={styles.page}>
      <Link className={styles.back} to="/projects">
        ← Projects
      </Link>

      <div className={styles.header}>
        <div>
          <h2>{project ? project.name : 'Loading…'}</h2>
          {project && <span className={`code-text ${styles.code}`}>{project.code}</span>}
        </div>
        <span className="text-muted">Manager: {me.displayName}</span>
      </div>

      {(loading || projectsLoading) && <p>Loading submitted timesheets…</p>}
      {error && <p role="alert">Could not load submitted timesheets for this project.</p>}

      {!loading && !error && timesheets.length === 0 && (
        <p className={styles.empty}>No submitted timesheets for this project.</p>
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
        </div>
      )}
    </section>
  )
}
