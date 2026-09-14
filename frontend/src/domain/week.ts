// Week vocabulary: day ordering and resolving a timestamp to its Monday.

export const DAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
] as const

export const WEEKDAYS = DAYS.slice(0, 5) as readonly Weekday[]

export type Weekday = (typeof DAYS)[number]

// Resolve seconds since epoch, in UTC, to the Monday of that week (ADR 0002).
export function weekStartFor(epochSeconds: number): Date {
  const date = new Date(epochSeconds * 1000)
  const utcDay = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()))
  const weekday = (utcDay.getUTCDay() + 6) % 7 // Monday = 0 .. Sunday = 6
  utcDay.setUTCDate(utcDay.getUTCDate() - weekday)
  return utcDay
}

// True once the given Monday (as an ISO date string) is before the current week's.
export function isBeforeCurrentWeek(weekStartIso: string): boolean {
  const [year, month, day] = weekStartIso.split('-').map(Number)
  const weekStart = Date.UTC(year, month - 1, day)
  const currentWeekStart = weekStartFor(Math.floor(Date.now() / 1000)).getTime()
  return weekStart < currentWeekStart
}

// The calendar date for each day of the week, given its Monday as an ISO date string.
export function datesForWeek(weekStartIso: string): Record<Weekday, Date> {
  const [year, month, day] = weekStartIso.split('-').map(Number)
  const monday = new Date(Date.UTC(year, month - 1, day))

  const dates = {} as Record<Weekday, Date>
  DAYS.forEach((weekday, index) => {
    const date = new Date(monday)
    date.setUTCDate(monday.getUTCDate() + index)
    dates[weekday] = date
  })
  return dates
}
