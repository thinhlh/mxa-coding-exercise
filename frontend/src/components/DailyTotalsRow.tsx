import type { Weekday } from '../domain/week'
import styles from './DailyTotalsRow.module.css'

interface DailyTotalsRowProps {
  days: readonly Weekday[]
  totals: Record<Weekday, number>
  flagged: Weekday[]
  overLimit: Partial<Record<Weekday, number>>
}

// The background *and* the warning glyph mark a flagged day — never colour alone.
export function DailyTotalsRow({ days, totals, flagged, overLimit }: DailyTotalsRowProps) {
  return (
    <tr className={styles.row}>
      <td className={styles.label}>Total</td>
      {days.map((day) => {
        const isOverLimit = day in overLimit
        const isFlagged = !isOverLimit && flagged.includes(day)
        const cellClass = [styles.cell, isOverLimit && styles.overLimit, isFlagged && styles.flagged]
          .filter(Boolean)
          .join(' ')
        return (
          <td key={day} className={cellClass}>
            {totals[day]}
          </td>
        )
      })}
    </tr>
  )
}
