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
  it('shows the login page to an unauthenticated visitor', () => {
    renderApp()
    expect(screen.getByRole('button', { name: 'Continue with company account' })).toBeInTheDocument()
  })
})
