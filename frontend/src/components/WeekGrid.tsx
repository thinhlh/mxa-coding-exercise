import { dailyTotals, daysOverLimit, flaggedDays } from '../domain/hours'
import { datesForWeek, type Weekday } from '../domain/week'
import type { LineItem } from '../types/timesheet'
import { DailyTotalsRow } from './DailyTotalsRow'
import { LineItemRow } from './LineItemRow'
import styles from './WeekGrid.module.css'

interface WeekGridProps {
  weekStart: string
  lineItems: LineItem[]
  days: readonly Weekday[]
  editable: boolean
  onHoursChange?: (index: number, day: Weekday, value: number) => void
  onRemoveLineItem?: (index: number) => void
}

const DATE_FORMAT = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', timeZone: 'UTC' })

// The totals row recomputes from `lineItems` on every render — the employee sees it change as they type.
// A read-only grid (a manager reviewing a week) passes neither callback.
export function WeekGrid({ weekStart, lineItems, days, editable, onHoursChange, onRemoveLineItem }: WeekGridProps) {
  const dates = datesForWeek(weekStart)
  const totals = dailyTotals(lineItems.map((item) => item.hours))
  const flagged = flaggedDays(totals)
  const overLimit = daysOverLimit(totals)

  return (
    <div className={styles.wrapper}>
      <table className={`table ${styles.table}`}>
        <thead>
          <tr>
            <th>Project</th>
            {days.map((day) => (
              <th key={day} className={styles.dayName}>
                {day.slice(0, 3)}
                <span className={styles.dayDate}>{DATE_FORMAT.format(dates[day])}</span>
              </th>
            ))}
            <th />
          </tr>
        </thead>
        <tbody>
          {lineItems.length === 0 ? (
            <tr>
              <td colSpan={days.length + 2} className={styles.empty}>
                No line items yet — add a project code below.
              </td>
            </tr>
          ) : (
            lineItems.map((lineItem, index) => (
              <LineItemRow
                key={lineItem.projectCode}
                lineItem={lineItem}
                days={days}
                editable={editable}
                onHoursChange={(day, value) => onHoursChange?.(index, day, value)}
                onRemove={() => onRemoveLineItem?.(index)}
              />
            ))
          )}
        </tbody>
        <tfoot>
          <DailyTotalsRow days={days} totals={totals} flagged={flagged} overLimit={overLimit} />
        </tfoot>
      </table>
      <p className={styles.legend}>A flagged weekday should total 8 hours.</p>
    </div>
  )
}
