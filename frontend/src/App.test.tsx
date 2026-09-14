import { render, screen } from '@testing-library/react'
import { AuthProvider } from 'react-oidc-context'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import App from './App'
import { oidcConfig } from './auth/oidcConfig'

function renderApp() {
  return render(
    <AuthProvider {...oidcConfig}>
      <MemoryRouter>
        <App />
      </MemoryRouter>
    </AuthProvider>,
  )
}

describe('App', () => {
  it('renders the app title', () => {
    renderApp()
    expect(screen.getByText('MXA Timesheet')).toBeInTheDocument()
  })

  it('sends an unauthenticated visitor to sign in', () => {
    renderApp()
    expect(screen.getByText('Redirecting to sign in…')).toBeInTheDocument()
  })
})
