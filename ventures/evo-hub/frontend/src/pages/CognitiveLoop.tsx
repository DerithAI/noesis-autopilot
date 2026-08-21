import { useState } from 'react'

export default function CognitiveLoop() {
  const [input, setInput] = useState('')
  const [stages, setStages] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    if (!input.trim() || busy) return
    setBusy(true)
    setError('')
    setStages([])
    try {
      const resp = await fetch('/cognitive/loop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input }),
      })
      const data = await resp.json()
      if (!resp.ok) throw new Error(data.detail || `HTTP ${resp.status}`)
      setStages(data.stages ?? [])
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <h2>Cognitive Loop</h2>
      <div className="row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What should LUMEN think about?"
          onKeyDown={(e) => e.key === 'Enter' && run()}
        />
        <button onClick={run} disabled={busy || !input.trim()}>
          {busy ? 'thinking…' : 'Run loop'}
        </button>
      </div>
      {error && <p className="bad">{error}</p>}
      {stages.length > 0 && (
        <ul className="stages">
          {stages.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
