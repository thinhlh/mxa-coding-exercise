import { useEffect } from 'react'
import { useAuth } from 'react-oidc-context'
import { RoleAwareShell } from './RoleAwareShell'

export function AuthGate() {
  const auth = useAuth()
  const { isLoading, isAuthenticated, activeNavigator, error, events, signinRedirect } = auth

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !activeNavigator && !error) {
      signinRedirect().catch(() => {
        // A failed redirect surfaces through auth.error on the next render.
      })
    }
  }, [isLoading, isAuthenticated, activeNavigator, error, signinRedirect])

  useEffect(
    () =>
      events.addAccessTokenExpired(() => {
        signinRedirect().catch(() => {
          // A failed redirect surfaces through auth.error on the next render.
        })
      }),
    [events, signinRedirect],
  )

  if (error) {
    return <p role="alert">Sign-in failed: {error.message}</p>
  }

  if (isLoading || !isAuthenticated) {
    return <p>Redirecting to sign in…</p>
  }

  return <RoleAwareShell />
}
