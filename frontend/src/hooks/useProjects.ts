import { useCallback, useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import { createProject, listProjects } from '../services/projects'
import type { Project, ProjectCreateRequest } from '../types/project'

interface UseProjectsResult {
  projects: Project[]
  loading: boolean
  error: unknown
  create: (body: ProjectCreateRequest) => Promise<Project>
  creating: boolean
}

// The signed-in manager's own projects: loads the list once, and prepends whatever `create` returns
// so the generated code is on screen without a refetch.
export function useProjects(): UseProjectsResult {
  const { user } = useAuth()
  const token = user?.access_token
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    listProjects(token)
      .then((result) => {
        if (!cancelled) setProjects(result)
      })
      .catch((caught: unknown) => {
        if (!cancelled) setError(caught)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [token])

  const create = useCallback(
    async (body: ProjectCreateRequest): Promise<Project> => {
      if (!token) throw new Error('not signed in')
      setCreating(true)
      try {
        const project = await createProject(token, body)
        setProjects((current) => [project, ...current])
        return project
      } finally {
        setCreating(false)
      }
    },
    [token],
  )

  return { projects, loading, error, create, creating }
}
