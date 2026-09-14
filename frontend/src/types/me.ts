export type Role = 'employee' | 'manager'

export interface Me {
  employeeId: string
  displayName: string
  role: Role
}
