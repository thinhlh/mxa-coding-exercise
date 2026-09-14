// Line item hours and the daily total they sum to.

import { DAYS, type Weekday } from './week'

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
