// dailyTotals sums every line item's hours entry for each day.

import { describe, expect, it } from 'vitest'
import { dailyTotals, ZERO_HOURS, type LineItemHours } from './hours'

function hoursOn(day: keyof LineItemHours, value: number): LineItemHours {
  return { ...ZERO_HOURS, [day]: value }
}

describe('dailyTotals', () => {
  it('sums multiple line items per day', () => {
    const totals = dailyTotals([hoursOn('monday', 20), hoursOn('monday', 5)])
    expect(totals.monday).toBe(25)
  })

  it('totals an untouched day at zero', () => {
    const totals = dailyTotals([ZERO_HOURS])
    expect(totals.monday).toBe(0)
    expect(totals.sunday).toBe(0)
  })

  it('sums whole-hour entries exactly to eight', () => {
    const totals = dailyTotals([hoursOn('monday', 5), hoursOn('monday', 3)])
    expect(totals.monday).toBe(8)
  })
})
