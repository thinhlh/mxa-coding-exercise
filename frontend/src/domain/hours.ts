// Line item hours and the daily total they sum to.

import { DAYS, WEEKDAYS, type Weekday } from './week'

export type LineItemHours = Record<Weekday, number>

export const ZERO_HOURS: LineItemHours = {
  monday: 0,
  tuesday: 0,
  wednesday: 0,
  thursday: 0,
  friday: 0,
  saturday: 0,
  sunday: 0,
}

// Sum every line item's hours entry for each day of the week.
export function dailyTotals(lineItems: LineItemHours[]): Record<Weekday, number> {
  const totals = { ...ZERO_HOURS }
  for (const day of DAYS) {
    totals[day] = lineItems.reduce((sum, item) => sum + item[day], 0)
  }
  return totals
}

// Weekdays whose total isn't exactly 8 — a warning only, never blocks save or submit.
export function flaggedDays(totals: Record<Weekday, number>): Weekday[] {
  return WEEKDAYS.filter((day) => totals[day] !== 8)
}

// Days whose total exceeds the 24-hour cap, mapped to that total — blocks submit.
export function daysOverLimit(totals: Record<Weekday, number>): Partial<Record<Weekday, number>> {
  const over: Partial<Record<Weekday, number>> = {}
  for (const day of DAYS) {
    if (totals[day] > 24) over[day] = totals[day]
  }
  return over
}
