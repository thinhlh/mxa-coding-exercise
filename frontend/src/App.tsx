import { AuthGate } from './auth/AuthGate'

function App() {
  return (
    <main>
      <h1>MXA Timesheet</h1>
      <AuthGate />
    </main>
  )
}

export default App
