import { useCallback, useEffect } from 'react'
import { useAuth } from 'react-oidc-context'
import { LoginPage } from '../pages/LoginPage'
import { RoleAwareShell } from './RoleAwareShell'

export function AuthGate() {
  const auth = useAuth()
  const { isLoading, isAuthenticated, activeNavigator, error, events, signinRedirect } = auth

  const signIn = useCallback(
    () =>
      signinRedirect().catch(() => {
        // A failed redirect surfaces through auth.error on the next render.
      }),
    [signinRedirect],
  )

  useEffect(() => events.addAccessTokenExpired(signIn), [events, signIn])

  if (error) {
    return <p role="alert">Sign-in failed: {error.message}</p>
  }

  if (activeNavigator === 'signinRedirect') {
    return <p>Taking you to sign in…</p>
  }

  if (isLoading || !isAuthenticated) {
    return <LoginPage onSignIn={signIn} />
  }

  return <RoleAwareShell />
}
