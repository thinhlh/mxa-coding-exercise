import { useState, type FormEvent } from 'react'
import { ZERO_HOURS } from '../domain/hours'
import { getProjectByCode } from '../services/projects'
import type { LineItem } from '../types/timesheet'
import styles from './AddLineItemForm.module.css'

interface AddLineItemFormProps {
  token: string
  existingCodes: string[]
  onAdd: (lineItem: LineItem) => void
}

export function AddLineItemForm({ token, existingCodes, onAdd }: AddLineItemFormProps) {
  const [code, setCode] = useState('')
  const [resolving, setResolving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = code.trim().toUpperCase()
    if (!trimmed) return

    if (existingCodes.includes(trimmed)) {
      setError('that project code is already on this timesheet')
      return
    }

    setResolving(true)
    setError(null)
    try {
      const project = await getProjectByCode(token, trimmed)
      onAdd({ projectCode: project.code, projectName: project.name, hours: { ...ZERO_HOURS } })
      setCode('')
    } catch {
      setError('no project has that code')
    } finally {
      setResolving(false)
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project code"
        className={styles.input}
        value={code}
        onChange={(event) => setCode(event.target.value)}
        maxLength={6}
      />
      <button type="submit" className={styles.button} disabled={resolving || !code.trim()}>
        Add line item
      </button>
      {error && <span className={styles.error}>{error}</span>}
    </form>
  )
}
