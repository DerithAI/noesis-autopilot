import React, { useState } from 'react';
import styles from './Council.module.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

interface Voice {
  role: string;
  recommendation: string;
  confidence: number;
  reasoning: string;
}

interface DeliberationResult {
  recommendation: string;
  confidence: number;
  unanimous: boolean;
  voices: Voice[];
  context: string;
}

const Council: React.FC = () => {
  const [decision, setDecision] = useState('');
  const [context, setContext] = useState('');
  const [requireUnanimous, setRequireUnanimous] = useState(false);
  const [result, setResult] = useState<DeliberationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleDeliberate = async () => {
    if (!decision.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/council/deliberate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          context: context || undefined,
          require_unanimous: requireUnanimous
        })
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error('Council error:', e);
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'architect': return '🏗️';
      case 'skeptic': return '🛡️';
      case 'pragmatist': return '⚡';
      case 'creative': return '💡';
      default: return '👤';
    }
  };

  const getRecColor = (rec: string) => {
    switch (rec) {
      case 'proceed': case 'ship_it': return styles.recGreen;
      case 'iterate': case 'explore': return styles.recYellow;
      case 'hold': case 'stop': case 'discuss_further': return styles.recRed;
      default: return styles.recNeutral;
    }
  };

  return (
    <div className={styles.council}>
      <header className={styles.header}>
        <h1>🏛️ Cognitive Council</h1>
        <p className={styles.subtitle}>4-voice deliberation engine — SUPERPOWERS L3</p>
      </header>

      <section className={styles.inputSection}>
        <h2>What decision needs deliberation?</h2>
        <textarea
          className={styles.textarea}
          placeholder="e.g. Should we deploy evo-hub to production? Should we add WebSocket support?..."
          value={decision}
          onChange={e => setDecision(e.target.value)}
          rows={3}
        />
        <textarea
          className={styles.textarea}
          placeholder="Optional context (constraints, background, goals)..."
          value={context}
          onChange={e => setContext(e.target.value)}
          rows={2}
        />
        <label className={styles.checkbox}>
          <input
            type="checkbox"
            checked={requireUnanimous}
            onChange={e => setRequireUnanimous(e.target.checked)}
          />
          Require unanimous consensus (otherwise → discuss further)
        </label>
        <button
          className={styles.btnPrimary}
          onClick={handleDeliberate}
          disabled={loading || !decision.trim()}
        >
          {loading ? '🧠 Deliberating...' : '🔮 Start Council'}
        </button>
      </section>

      {result && (
        <section className={styles.resultSection}>
          <div className={styles.synthesis}>
            <h2>Synthesis</h2>
            <div className={styles.synthHeader}>
              <span className={`${styles.synthRec} ${getRecColor(result.recommendation)}`}>
                {result.recommendation.toUpperCase()}
              </span>
              <span className={styles.synthConfidence}>
                Confidence: {result.confidence}%
              </span>
              <span className={styles.synthConsensus}>
                {result.unanimous ? '✅ Unanimous' : '⚠️ Split'}
              </span>
            </div>
          </div>

          <div className={styles.voicesGrid}>
            {result.voices.map((voice, i) => (
              <div key={i} className={styles.voiceCard}>
                <div className={styles.voiceHeader}>
                  <span className={styles.voiceIcon}>{getRoleIcon(voice.role)}</span>
                  <span className={styles.voiceRole}>{voice.role.toUpperCase()}</span>
                  <span className={`${styles.voiceRec} ${getRecColor(voice.recommendation)}`}>
                    {voice.recommendation}
                  </span>
                </div>
                <div className={styles.voiceConfidence}>
                  Confidence: {voice.confidence}%
                </div>
                <p className={styles.voiceReasoning}>{voice.reasoning}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className={styles.infoSection}>
        <h3>📖 How it works</h3>
        <div className={styles.infoGrid}>
          <div className={styles.infoCard}>
            <span className={styles.infoIcon}>🏗️</span>
            <strong>Architect</strong>
            <p>Long-term structure, scalability, technical debt</p>
          </div>
          <div className={styles.infoCard}>
            <span className={styles.infoIcon}>🛡️</span>
            <strong>Skeptic</strong>
            <p>Risks, failure modes, hidden assumptions</p>
          </div>
          <div className={styles.infoCard}>
            <span className={styles.infoIcon}>⚡</span>
            <strong>Pragmatist</strong>
            <p>Shipping speed, constraints, practical tools</p>
          </div>
          <div className={styles.infoCard}>
            <span className={styles.infoIcon}>💡</span>
            <strong>Creative</strong>
            <p>Alternatives, opportunities, wildcard paths</p>
          </div>
        </div>
        <p className={styles.infoNote}>
          Weighted voting: Architect 30%, Pragmatist 30%, Skeptic 25%, Creative 15%.
          Skeptic holds veto power — if they say stop, the council holds.
        </p>
      </section>
    </div>
  );
};

export default Council;
