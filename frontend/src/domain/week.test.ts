// weekStartFor resolves any timestamp to that week's Monday.

import { describe, expect, it } from 'vitest'
import { DAYS, WEEKDAYS, weekStartFor } from './week'

function utcEpochSeconds(
  year: number,
  month: number,
  day: number,
  hour = 0,
  minute = 0,
  second = 0,
): number {
  return Date.UTC(year, month - 1, day, hour, minute, second) / 1000
}

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

describe('week', () => {
  it('orders days Monday first', () => {
    expect(DAYS).toEqual([
      'monday',
      'tuesday',
      'wednesday',
      'thursday',
      'friday',
      'saturday',
      'sunday',
    ])
    expect(WEEKDAYS).toEqual(['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
  })

  it('resolves a mid-week timestamp to its Monday', () => {
    // Wednesday 2026-09-16
    const ts = utcEpochSeconds(2026, 9, 16, 12)
    expect(isoDate(weekStartFor(ts))).toBe('2026-09-14')
  })

  it('resolves a Sunday to the prior Monday', () => {
    const ts = utcEpochSeconds(2026, 9, 20, 23, 59)
    expect(isoDate(weekStartFor(ts))).toBe('2026-09-14')
  })

  it('resolves across a week boundary', () => {
    const monday = utcEpochSeconds(2026, 9, 21, 0, 0)
    const sundayBefore = utcEpochSeconds(2026, 9, 20, 23, 59, 59)
    expect(isoDate(weekStartFor(sundayBefore))).toBe('2026-09-14')
    expect(isoDate(weekStartFor(monday))).toBe('2026-09-21')
  })

  it('resolves across a year boundary', () => {
    // 2025-12-31 is a Wednesday, week starts Monday 2025-12-29.
    // 2026-01-01 is a Thursday, still in that same week.
    const dec31 = utcEpochSeconds(2025, 12, 31, 6)
    const jan1 = utcEpochSeconds(2026, 1, 1, 6)
    expect(isoDate(weekStartFor(dec31))).toBe('2025-12-29')
    expect(isoDate(weekStartFor(jan1))).toBe('2025-12-29')
  })
})
