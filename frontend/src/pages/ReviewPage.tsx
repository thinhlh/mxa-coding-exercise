import type { Me } from '../types/me'

interface ReviewPageProps {
  me: Me
}

export function ReviewPage({ me }: ReviewPageProps) {
  return (
    <section>
      <h2>Review queue</h2>
      <p>Signed in as {me.displayName}.</p>
    </section>
  )
}
