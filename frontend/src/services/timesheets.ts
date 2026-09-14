import { apiFetch } from './api'
import type { Timesheet, TimesheetStatus, TimesheetWriteRequest } from '../types/timesheet'

export function getTimesheetForWeek(token: string, at: number): Promise<Timesheet> {
  return apiFetch<Timesheet>(`/timesheets?at=${at}`, { token })
}

export function listTimesheetsByStatus(
  token: string,
  timesheetStatus: TimesheetStatus,
  projectId?: string,
): Promise<Timesheet[]> {
  const query = projectId ? `?projectId=${encodeURIComponent(projectId)}` : ''
  return apiFetch<Timesheet[]>(`/timesheets/${timesheetStatus}${query}`, { token })
}

export function writeTimesheet(
  token: string,
  targetStatus: TimesheetStatus,
  body: TimesheetWriteRequest,
): Promise<Timesheet> {
  return apiFetch<Timesheet>(`/timesheets/${targetStatus}`, {
    token,
    method: 'POST',
    body: JSON.stringify(body),
  })
}
