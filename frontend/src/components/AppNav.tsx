import { NavLink } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import type { Me } from '../types/me'
import styles from './AppNav.module.css'

interface AppNavProps {
  me: Me
}

const LINKS = {
  employee: [{ to: '/timesheet', label: 'Timesheet' }],
  manager: [
    { to: '/projects', label: 'Projects' },
    { to: '/review', label: 'Review' },
  ],
}

// The design system's .nav already highlights the current page via
// `a[aria-current='page']`, which NavLink sets on the active route — so there is no
// active class to pass here.
export function AppNav({ me }: AppNavProps) {
  const { signoutRedirect } = useAuth()

  return (
    <header className={`nav ${styles.nav}`}>
      <span className="nav-brand">MXA Timesheet</span>

      <nav className={styles.links}>
        {LINKS[me.role].map((link) => (
          <NavLink key={link.to} to={link.to}>
            {link.label}
          </NavLink>
        ))}
      </nav>

      <span className={styles.user}>
        {me.displayName}
        <span className="tag tag-accent">{me.role}</span>
      </span>

      <button type="button" className="btn btn-secondary" onClick={() => void signoutRedirect()}>
        Sign out
      </button>
    </header>
  )
}
