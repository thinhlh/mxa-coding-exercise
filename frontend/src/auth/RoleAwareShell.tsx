import { Navigate, Route, Routes } from 'react-router-dom'
import { useMe } from '../hooks/useMe'
import { ProjectsPage } from '../pages/ProjectsPage'
import { ReviewPage } from '../pages/ReviewPage'
import { TimesheetWeekPage } from '../pages/TimesheetWeekPage'

export function RoleAwareShell() {
  const { me, loading, error } = useMe()

  if (loading) {
    return <p>Loading your profile…</p>
  }

  if (error || !me) {
    return <p role="alert">Could not load your profile.</p>
  }

  const homePath = me.role === 'manager' ? '/projects' : '/timesheet'

  return (
    <Routes>
      <Route path="/" element={<Navigate to={homePath} replace />} />
      {me.role === 'employee' && <Route path="/timesheet" element={<TimesheetWeekPage me={me} />} />}
      {me.role === 'manager' && (
        <>
          <Route path="/projects" element={<ProjectsPage me={me} />} />
          <Route path="/review" element={<ReviewPage me={me} />} />
        </>
      )}
      <Route path="*" element={<Navigate to={homePath} replace />} />
    </Routes>
  )
}
