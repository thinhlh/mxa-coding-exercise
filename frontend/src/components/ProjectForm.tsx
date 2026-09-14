import { useId, useState, type FormEvent } from 'react'
import type { Project, ProjectCreateRequest } from '../types/project'
import styles from './ProjectForm.module.css'

interface ProjectFormProps {
  creating: boolean
  onCreate: (body: ProjectCreateRequest) => Promise<Project>
  onCancel: () => void
}

// The body of the "New project" dialog — the fields and the dialog's own action row.
// The surface around it is <Modal>, which the page owns.
export function ProjectForm({ creating, onCreate, onCancel }: ProjectFormProps) {
  const nameId = useId()
  const startDateId = useId()
  const descriptionId = useId()

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [startDate, setStartDate] = useState('')
  const [error, setError] = useState<string | null>(null)

  const complete = name.trim() !== '' && startDate !== ''

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!complete) return

    setError(null)
    try {
      await onCreate({ name: name.trim(), description: description.trim(), startDate })
    } catch {
      setError('could not create the project — check the fields and try again')
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor={nameId}>Project name</label>
        <input
          id={nameId}
          type="text"
          className="input"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
      </div>

      <div className="field">
        <label htmlFor={startDateId}>Start date</label>
        <input
          id={startDateId}
          type="date"
          className="input"
          value={startDate}
          onChange={(event) => setStartDate(event.target.value)}
          required
        />
      </div>

      <div className="field">
        <label htmlFor={descriptionId}>Description</label>
        <textarea
          id={descriptionId}
          className="input"
          rows={3}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>

      <p className="dialog-body">The platform generates the 6-character project code once the project is created.</p>

      {error && (
        <p role="alert" className={styles.error}>
          {error}
        </p>
      )}

      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={creating}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={creating || !complete}>
          {creating ? 'Creating…' : 'Create project'}
        </button>
      </div>
    </form>
  )
}
