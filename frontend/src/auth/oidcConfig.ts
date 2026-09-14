import type { AuthProviderProps } from 'react-oidc-context'

// Local-dev defaults match deploy/keycloak/realm-mxa.json (realm `mxa`, client
// `mxa-web`) and the ports docker-compose publishes. Override with VITE_*
// env vars for any other environment.
export const oidcConfig: AuthProviderProps = {
  authority: import.meta.env.VITE_KEYCLOAK_ISSUER ?? 'http://localhost:8080/realms/mxa',
  client_id: import.meta.env.VITE_KEYCLOAK_CLIENT_ID ?? 'mxa-web',
  redirect_uri: import.meta.env.VITE_REDIRECT_URI ?? 'http://localhost:5173/',
  // Off so a lapsed token sends the user through a full Keycloak login
  // rather than a background iframe renew.
  automaticSilentRenew: false,
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname)
  },
}
