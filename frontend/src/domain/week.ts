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
