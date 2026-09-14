import type { Me } from '../types/me'

interface TimesheetPageProps {
  me: Me
}

export function TimesheetPage({ me }: TimesheetPageProps) {
  return (
    <section>
      <h2>Your timesheet</h2>
      <p>Signed in as {me.displayName}.</p>
    </section>
  )
}
