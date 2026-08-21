import { useState } from 'react'

interface MemoryHit {
  key?: string
  text?: string
  metadata?: Record<string, unknown>
}

export default function MemorySearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<MemoryHit[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const search = async () => {
    if (!query.trim() || busy) return
    setBusy(true)
    setError('')
    setResults([])
    try {
      const resp = await fetch(`/memory/search?query=${encodeURIComponent(query)}&limit=5`)
      const data = await resp.json()
      if (!resp.ok) throw new Error(data.detail || `HTTP ${resp.status}`)
      setResults(data.results ?? [])
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <h2>Memory Search</h2>
      <div className="row">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search LUMEN semantic memory…"
          onKeyDown={(e) => e.key === 'Enter' && search()}
        />
        <button onClick={search} disabled={busy || !query.trim()}>
          {busy ? 'searching…' : 'Search'}
        </button>
      </div>
      {error && <p className="bad">{error}</p>}
      {results.length > 0 && (
        <ul className="results">
          {results.map((r, i) => (
            <li key={i}>
              <code>{r.key}</code>
              <p>{(r.text ?? '').slice(0, 160)}</p>
            </li>
          ))}
        </ul>
      )}
      {!busy && !error && results.length === 0 && <p className="dim">No results yet.</p>}
    </section>
  )
}
