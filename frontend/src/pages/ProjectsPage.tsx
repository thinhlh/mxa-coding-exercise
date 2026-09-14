import type { Me } from '../types/me'

interface ProjectsPageProps {
  me: Me
}

export function ProjectsPage({ me }: ProjectsPageProps) {
  return (
    <section>
      <h2>Your projects</h2>
      <p>Signed in as {me.displayName}.</p>
    </section>
  )
}
