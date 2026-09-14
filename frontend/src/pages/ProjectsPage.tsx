import { useState } from 'react'
import { Modal } from '../components/Modal'
import { ProjectForm } from '../components/ProjectForm'
import { useProjects } from '../hooks/useProjects'
import type { Me } from '../types/me'
import type { Project, ProjectCreateRequest } from '../types/project'
import styles from './ProjectsPage.module.css'

interface ProjectsPageProps {
  me: Me
}

const START_DATE_FORMAT = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
})

function formatStartDate(startDate: string): string {
  return START_DATE_FORMAT.format(new Date(`${startDate}T00:00:00Z`))
}

export function ProjectsPage({ me }: ProjectsPageProps) {
  const { projects, loading, error, create, creating } = useProjects()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [created, setCreated] = useState<Project | null>(null)
  const [copied, setCopied] = useState(false)

  // The dialog closes on success only — a failed create keeps the filled-in fields on
  // screen so the manager can correct them.
  async function handleCreate(body: ProjectCreateRequest): Promise<Project> {
    const project = await create(body)
    setCreated(project)
    setCopied(false)
    setDialogOpen(false)
    return project
  }

  async function handleCopy(code: string) {
    await navigator.clipboard.writeText(code)
    setCopied(true)
  }

  return (
    <section className={styles.page}>
      <div className={styles.header}>
        <div>
          <h2>Your projects</h2>
          <span className="text-muted">Manager: {me.displayName}</span>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => setDialogOpen(true)}>
          New project
        </button>
      </div>

      {dialogOpen && (
        <Modal title="New project" onClose={() => setDialogOpen(false)}>
          <ProjectForm creating={creating} onCreate={handleCreate} onCancel={() => setDialogOpen(false)} />
        </Modal>
      )}

      {created && (
        <div className={styles.createdBanner} role="status">
          <span className={styles.createdLabel}>{created.name} is ready. Its project code is</span>
          <span className={`code-text ${styles.createdCode}`}>{created.code}</span>
          <button type="button" className="btn btn-secondary" onClick={() => handleCopy(created.code)}>
            {copied ? 'Copied' : 'Copy code'}
          </button>
          <span className={styles.createdHint}>Employees add a line item with this code.</span>
        </div>
      )}

      {loading && <p>Loading your projects…</p>}
      {error && <p role="alert">Could not load your projects.</p>}

      {!loading && !error && projects.length === 0 && (
        <p className={styles.empty}>No projects yet — create your first one with “New project”.</p>
      )}

      {projects.length > 0 && (
        <div className={styles.wrapper}>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Code</th>
                <th scope="col">Project</th>
                <th scope="col">Start date</th>
                <th scope="col">Description</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id}>
                  <td className={`code-text ${styles.code}`}>{project.code}</td>
                  <td className={styles.name}>{project.name}</td>
                  <td>{formatStartDate(project.startDate)}</td>
                  <td className="text-muted">{project.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
