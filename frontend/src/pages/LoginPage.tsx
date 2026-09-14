import styles from './LoginPage.module.css'

interface LoginPageProps {
  onSignIn: () => void
}

// One action only: no email or password field, no "forgot" link — Keycloak
// owns identity and returns the user here once authenticated.
export function LoginPage({ onSignIn }: LoginPageProps) {
  return (
    <div className={styles.login}>
      <div className={styles.brand}>
        <span className={styles.brandName}>MXA Consulting</span>
        <div>
          <div className={styles.rule} />
          <h1 className={styles.title}>Timesheet</h1>
          <p className={styles.tagline}>Log your week against project codes and send it for approval.</p>
        </div>
        <span className={styles.footnote}>Internal use only</span>
      </div>
      <div className={styles.panel}>
        <h2 className={styles.panelHeading}>Sign in to continue</h2>
        <button type="button" className={`btn btn-primary btn-block ${styles.button}`} onClick={onSignIn}>
          Continue with company account
          <span className={styles.buttonArrow} aria-hidden="true">
            →
          </span>
        </button>
        <p className={styles.panelNote}>
          You will be redirected to the MXA identity console and returned here once authenticated.
        </p>
      </div>
    </div>
  )
}
