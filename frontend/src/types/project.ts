export interface Project {
  id: string
  code: string
  name: string
  managerName: string
  description: string
  startDate: string
}

export interface ProjectCreateRequest {
  name: string
  description: string
  startDate: string
}
