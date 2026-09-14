import { apiFetch } from './api'
import type { Project } from '../types/project'

export function getProjectByCode(token: string, code: string): Promise<Project> {
  return apiFetch<Project>(`/projects/by-code/${encodeURIComponent(code)}`, { token })
}
