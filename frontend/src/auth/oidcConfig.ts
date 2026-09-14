import type { AuthProviderProps } from 'react-oidc-context'

const redirectUri = import.meta.env.VITE_REDIRECT_URI || 'http://localhost:5173/'

export const oidcConfig: AuthProviderProps = {
  authority: import.meta.env.VITE_KEYCLOAK_ISSUER || 'http://localhost:8080/realms/mxa',
  client_id: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'mxa-web',
  redirect_uri: redirectUri,
  post_logout_redirect_uri: redirectUri,
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname)
  },
}
