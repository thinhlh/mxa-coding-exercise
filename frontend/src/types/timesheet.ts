export const WEEKDAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
] as const

export type Weekday = (typeof WEEKDAYS)[number]

export type DailyHours = Record<Weekday, number>

export type TimesheetStatus = 'draft' | 'submitted' | 'approved' | 'rejected'

export interface LineItem {
  projectCode: string
  projectName: string
  hours: DailyHours
}

export interface Timesheet {
  id: string | null
  weekStart: string
  status: TimesheetStatus
  employeeName: string
  lineItems: LineItem[]
  dailyTotals: DailyHours
  totalHours: number
  flaggedDays: Weekday[]
  submitMessage: string | null
  reviewMessage: string | null
  submittedAt: string | null
  reviewedAt: string | null
}

export interface LineItemInput {
  projectCode: string
  hours: DailyHours
}

export interface TimesheetWriteRequest {
  at?: number
  lineItems?: LineItemInput[]
  timesheetId?: string
  message?: string
}
