import type { Weekday } from '../domain/week'
import type { LineItem } from '../types/timesheet'
import styles from './LineItemRow.module.css'

interface LineItemRowProps {
  lineItem: LineItem
  days: readonly Weekday[]
  editable: boolean
  onHoursChange: (day: Weekday, value: number) => void
  onRemove: () => void
}

export function LineItemRow({ lineItem, days, editable, onHoursChange, onRemove }: LineItemRowProps) {
  return (
    <tr>
      <td className={styles.projectCell}>
        <span className={styles.projectCode}>{lineItem.projectCode}</span>
        <span className={styles.projectName}>{lineItem.projectName}</span>
      </td>
      {days.map((day) => (
        <td key={day}>
          {editable ? (
            <input
              type="number"
              min={0}
              step={1}
              className={`input ${styles.hourInput}`}
              value={lineItem.hours[day]}
              onChange={(event) => onHoursChange(day, Number(event.target.value))}
            />
          ) : (
            <span className={styles.readOnlyHour}>{lineItem.hours[day]}</span>
          )}
        </td>
      ))}
      <td>
        {editable && (
          <button type="button" className="btn btn-ghost" onClick={onRemove}>
            Remove
          </button>
        )}
      </td>
    </tr>
  )
}
