import { apiFetch } from './api'
import type { Project, ProjectCreateRequest } from '../types/project'

export function getProjectByCode(token: string, code: string): Promise<Project> {
  return apiFetch<Project>(`/projects/by-code/${encodeURIComponent(code)}`, { token })
}

export function listProjects(token: string): Promise<Project[]> {
  return apiFetch<Project[]>('/projects', { token })
}

export function createProject(token: string, body: ProjectCreateRequest): Promise<Project> {
  return apiFetch<Project>('/projects', {
    token,
    method: 'POST',
    body: JSON.stringify(body),
  })
}
