import React, { useEffect, useState, useMemo, useCallback } from 'react';
import styles from './Dashboard.module.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

interface Venture {
  name: string;
  seed: string;
  stack: string;
  files: number;
  status: string;
}

interface ITDDEntry {
  venture: string;
  compliant: boolean;
  tests: number;
  passed: number;
  failed: number;
  note?: string;
}

interface SystemStatus {
  evo_hub: boolean;
  lumen: boolean;
  ollama: boolean;
  ventures: number;
}

interface Pipeline {
  steps: string[];
  current: string;
  active_venture: string;
}

interface TestSuite {
  suite: string;
  passed: boolean;
  output?: string;
  error?: string;
}

const Dashboard: React.FC = () => {
  const [ventures, setVentures] = useState<Venture[]>([]);
  const [itddBoard, setItddBoard] = useState<ITDDEntry[]>([]);
  const [sysStatus, setSysStatus] = useState<SystemStatus | null>(null);
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [loading, setLoading] = useState(true);

  // Action states
  const [generating, setGenerating] = useState(false);
  const [testing, setTesting] = useState(false);
  const [cogRunning, setCogRunning] = useState(false);
  const [howling, setHowling] = useState(false);
  const [insighting, setInsighting] = useState(false);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const [showGenModal, setShowGenModal] = useState(false);
  const [genSeed, setGenSeed] = useState('');
  const [genModel, setGenModel] = useState('qwen2.5:7b');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [venturesRes, statusRes, pipelineRes, itddRes] = await Promise.all([
          fetch(`${API_BASE}/api/ventures`).catch(() => null),
          fetch(`${API_BASE}/api/status`).catch(() => null),
          fetch(`${API_BASE}/api/pipeline`).catch(() => null),
          fetch(`${API_BASE}/api/itdd/status`).catch(() => null),
        ]);

        if (venturesRes?.ok) setVentures(await venturesRes.json());
        if (statusRes?.ok) setSysStatus(await statusRes.json());
        if (pipelineRes?.ok) setPipeline(await pipelineRes.json());
        if (itddRes?.ok) {
          const itddData = await itddRes.json();
          setItddBoard(itddData.scoreboard || []);
        }
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // WebSocket for real-time status updates
    const ws = new WebSocket(`ws://${API_BASE.replace(/^http:\/\//, '')}/ws/dashboard`);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'status' && msg.data) {
          setSysStatus(prev => prev ? { ...prev, ...msg.data } : msg.data);
        }
      } catch {
        // ignore malformed ws messages
      }
    };
    ws.onerror = () => {
      // fallback to polling if ws fails
    };

    return () => {
      ws.close();
    };
  }, []);

  const getItddFor = useCallback((name: string) => itddBoard.find(b => b.venture === name), [itddBoard]);

  const handleGenerate = async () => {
    if (!genSeed.trim()) return;
    setGenerating(true);
    setActionResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/action/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: genSeed, model: genModel })
      });
      const data = await res.json();
      setActionResult(data.success
        ? `✅ Generated venture from seed: "${genSeed}"`
        : `❌ Failed: ${data.error || data.stderr || 'unknown error'}`
      );
      setShowGenModal(false);
      setGenSeed('');
    } catch (e) {
      setActionResult(`❌ Error: ${e}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setActionResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/action/tests`);
      const data = await res.json();
      const summary = `${data.total_passed}/${data.total_suites} test suites passed`;
      setActionResult(`🔄 ${summary}\n${(data.suites as TestSuite[]).map((s) => `${s.passed ? '✅' : '❌'} ${s.suite}`).join('\n')}`);
    } catch (e) {
      setActionResult(`❌ Error: ${e}`);
    } finally {
      setTesting(false);
    }
  };

  const handleCognitive = async () => {
    setCogRunning(true);
    setActionResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/action/cognitive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: 'Analyze current venture portfolio and suggest next priority', mode: 'analyze' })
      });
      const data = await res.json();
      setActionResult(`🧠 Cognitive Loop: ${data.stages?.length || 0} stages processed`);
    } catch (e) {
      setActionResult(`❌ Error: ${e}`);
    } finally {
      setCogRunning(false);
    }
  };

  const handleHowl = async () => {
    setHowling(true);
    setActionResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/action/howl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Dashboard action fired: WOLF HOWL', frequency: 'high' })
      });
      const data = await res.json();
      setActionResult(data.sent ? '🐺 Howl sent to WOLF pack!' : `❌ Howl failed: ${data.error}`);
    } catch (e) {
      setActionResult(`❌ Error: ${e}`);
    } finally {
      setHowling(false);
    }
  };

  const handleInsights = async () => {
    setInsighting(true);
    setActionResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/action/insights`);
      const data = await res.json();
      setActionResult(data.generated
        ? `📊 Insights generated (${data.insights?.length || 0} chars)`
        : `❌ Insights failed: ${data.error}`
      );
    } catch (e) {
      setActionResult(`❌ Error: ${e}`);
    } finally {
      setInsighting(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.loading}>🔄 Loading EVO-DASH...</div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <h1>EVO-DASH</h1>
        <p className={styles.subtitle}>Master Command Center — {ventures.length} Ventures, Live Systems, 1 Brain</p>
      </header>

      {/* Action Result Banner */}
      {actionResult && (
        <div className={styles.resultBanner}>
          <pre>{actionResult}</pre>
          <button className={styles.closeBtn} onClick={() => setActionResult(null)} aria-label="Dismiss notification">×</button>
        </div>
      )}

      {/* System Status Bar */}
      {sysStatus && (
        <section className={styles.statusBar}>
          <div className={`${styles.statusCard} ${sysStatus.evo_hub ? styles.online : styles.offline}`}>
            <span className={styles.statusIcon}>⚡</span>
            <div>
              <strong>EVO-HUB API</strong>
              <span>{sysStatus.evo_hub ? 'Online' : 'Offline'}</span>
            </div>
          </div>
          <div className={`${styles.statusCard} ${sysStatus.lumen ? styles.online : styles.offline}`}>
            <span className={styles.statusIcon}>🧠</span>
            <div>
              <strong>LUMEN OS</strong>
              <span>{sysStatus.lumen ? 'Phase 3A' : 'Offline'}</span>
            </div>
          </div>
          <div className={`${styles.statusCard} ${sysStatus.ollama ? styles.online : styles.offline}`}>
            <span className={styles.statusIcon}>🤖</span>
            <div>
              <strong>Ollama</strong>
              <span>{sysStatus.ollama ? '14 Models' : 'Offline'}</span>
            </div>
          </div>
          <div className={styles.statusCard}>
            <span className={styles.statusIcon}>📦</span>
            <div>
              <strong>Ventures</strong>
              <span>{sysStatus.ventures} Total</span>
            </div>
          </div>
        </section>
      )}

      {/* Pipeline Monitor */}
      {pipeline && (
        <section className={styles.pipeline}>
          <h2>🚀 Live Pipeline — {pipeline.active_venture}</h2>
          <div className={styles.pipelineSteps}>
            {pipeline.steps.map((step, i) => (
              <React.Fragment key={step}>
                <div className={`${styles.step} ${step === pipeline.current ? styles.active : ''}`}>
                  {step}
                </div>
                {i < pipeline.steps.length - 1 && <span>→</span>}
              </React.Fragment>
            ))}
          </div>
        </section>
      )}

      {/* ITDD Scoreboard */}
      <section className={styles.itddSection}>
        <h2>🧪 ITDD Compliance Scoreboard</h2>
        <div className={styles.itddGrid}>
          {itddBoard.map((entry, i) => (
            <div key={i} className={`${styles.itddCard} ${entry.compliant ? styles.itddGreen : entry.tests > 0 ? styles.itddRed : styles.itddGray}`}>
              <div className={styles.itddHeader}>
                <span className={styles.itddIcon}>{entry.compliant ? '✅' : entry.tests > 0 ? '❌' : '⚪'}</span>
                <span className={styles.itddName}>{entry.venture}</span>
              </div>
              <div className={styles.itddStats}>
                {entry.tests > 0 ? (
                  <>
                    <span>{entry.passed}/{entry.tests} passed</span>
                    {entry.failed > 0 && <span className={styles.itddFail}>{entry.failed} failed</span>}
                  </>
                ) : (
                  <span className={styles.itddNote}>{entry.note || 'No tests'}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Ventures Grid */}
      <section className={styles.venturesSection}>
        <h2>📁 Ventures Portfolio</h2>
        <div className={styles.venturesGrid}>
          {ventures.map((v, i) => {
            const itdd = getItddFor(v.name);
            return (
              <div key={i} className={styles.ventureCard}>
                <div className={styles.ventureHeader}>
                  <h3>{v.name}</h3>
                  <span className={`${styles.badge} ${v.status === 'live' ? styles.badgeLive : styles.badgeDeployed}`}>
                    {v.status.toUpperCase()}
                  </span>
                </div>
                <div className={styles.ventureBody}>
                  <div className={styles.ventureMeta}>
                    <span>🌱 {v.seed}</span>
                    <span>⚙️ {v.stack}</span>
                    <span>📄 {v.files} files</span>
                    {itdd && (
                      <span className={`${styles.itddMini} ${itdd.compliant ? styles.itddMiniGreen : itdd.tests > 0 ? styles.itddMiniRed : ''}`}>
                        🧪 {itdd.passed}/{itdd.tests}
                      </span>
                    )}
                  </div>
                  <div className={styles.ventureActions}>
                    <button className={styles.btnPrimary} aria-label={`Open ${v.name}`}>Open</button>
                    <button className={styles.btnSecondary} aria-label={`Test ${v.name}`}>Test</button>
                    <button className={styles.btnSecondary} aria-label={`Deploy ${v.name}`}>Deploy</button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Action Bar */}
      <section className={styles.actionBar}>
        <h2>🎛️ Actions</h2>
        <div className={styles.actionButtons}>
          <button
            className={styles.btnAction}
            onClick={() => setShowGenModal(true)}
            disabled={generating}
            aria-label="Generate a new venture using Venture-Swarm"
            aria-haspopup="dialog"
          >
            {generating ? '🔄 Generating...' : '+ Generate Venture'}
          </button>
          <button
            className={styles.btnAction}
            onClick={handleTest}
            disabled={testing}
            aria-label="Run all test suites across ventures"
          >
            {testing ? '🔄 Testing...' : '🔄 Run Tests'}
          </button>
          <button
            className={styles.btnAction}
            onClick={handleCognitive}
            disabled={cogRunning}
            aria-label="Run EVO Agent cognitive loop"
          >
            {cogRunning ? '🔄 Thinking...' : '🧠 Cognitive Loop'}
          </button>
          <button
            className={styles.btnAction}
            onClick={handleHowl}
            disabled={howling}
            aria-label="Send a howl message to WOLF pack"
          >
            {howling ? '🔄 Howling...' : '🐺 WOLF Howl'}
          </button>
          <button
            className={styles.btnAction}
            onClick={handleInsights}
            disabled={insighting}
            aria-label="Generate NOESIS insights from memory"
          >
            {insighting ? '🔄 Analyzing...' : '📊 Insights'}
          </button>
        </div>
      </section>

      {/* Generate Venture Modal */}
      {showGenModal && (
        <div className={styles.modalOverlay} onClick={() => setShowGenModal(false)} role="presentation">
          <div
            className={styles.modal}
            onClick={e => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="gen-modal-title"
          >
            <h3 id="gen-modal-title">🚀 Generate New Venture</h3>
            <input
              type="text"
              placeholder="Enter seed idea (e.g. 'e-commerce api')"
              value={genSeed}
              onChange={e => setGenSeed(e.target.value)}
              className={styles.input}
              onKeyDown={e => e.key === 'Enter' && handleGenerate()}
              aria-label="Venture seed idea"
              aria-required="true"
            />
            <select
              value={genModel}
              onChange={e => setGenModel(e.target.value)}
              className={styles.select}
              aria-label="Ollama model selection"
            >
              <option value="qwen2.5:7b">qwen2.5:7b (balanced)</option>
              <option value="qwen2.5:3b">qwen2.5:3b (fast)</option>
              <option value="deepseek-r1">deepseek-r1 (smart)</option>
              <option value="qwen3:8b">qwen3:8b (advanced)</option>
            </select>
            <div className={styles.modalActions}>
              <button className={styles.btnPrimary} onClick={handleGenerate} disabled={!genSeed.trim()} aria-label="Generate venture">
                Generate
              </button>
              <button className={styles.btnSecondary} onClick={() => setShowGenModal(false)} aria-label="Cancel generation">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
