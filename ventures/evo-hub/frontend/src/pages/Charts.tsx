import { useEffect, useMemo, useState } from 'react';
import { ChartData, ChartOptions } from 'chart.js/auto';
import Chart from '../components/Chart';
import styles from './Charts.module.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Palette validated for CVD separation + contrast on both themes (dataviz six-checks).
const COLOR_PASSED = '#2f9e6b';
const COLOR_FAILED = '#d64550';
const COLOR_NO_TESTS = '#8b90a0';

interface ItddEntry {
  venture: string;
  compliant: boolean;
  tests: number;
  passed: number;
  failed: number;
  note?: string;
}

interface ItddStatus {
  total_ventures: number;
  compliant: number;
  with_tests: number;
  coverage_ratio: number;
  compliance_ratio: number;
  scoreboard: ItddEntry[];
}

interface Venture {
  name: string;
  seed?: string;
  stack?: string;
  files?: number;
  status?: string;
}

type LoadState = 'loading' | 'ready' | 'offline';

/** Read a design token from the themed .app root so charts follow light/dark mode. */
function readToken(name: string, fallback: string): string {
  if (typeof document === 'undefined') return fallback;
  const el = document.querySelector('.app') ?? document.documentElement;
  const value = getComputedStyle(el).getPropertyValue(name).trim();
  return value || fallback;
}

const Charts = () => {
  const [state, setState] = useState<LoadState>('loading');
  const [itdd, setItdd] = useState<ItddStatus | null>(null);
  const [ventures, setVentures] = useState<Venture[]>([]);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      // Promise.allSettled never rejects — a dead backend yields 'rejected'
      // entries here instead of an unhandled promise rejection.
      const [itddRes, venturesRes] = await Promise.allSettled([
        fetch(`${API_BASE}/api/itdd/status`).then(r => {
          if (!r.ok) throw new Error(`itdd/status ${r.status}`);
          return r.json() as Promise<ItddStatus>;
        }),
        fetch(`${API_BASE}/api/ventures`).then(r => {
          if (!r.ok) throw new Error(`ventures ${r.status}`);
          return r.json() as Promise<Venture[]>;
        }),
      ]);
      if (cancelled) return;
      if (venturesRes.status === 'fulfilled' && Array.isArray(venturesRes.value)) {
        setVentures(venturesRes.value);
      }
      if (itddRes.status === 'fulfilled' && Array.isArray(itddRes.value?.scoreboard)) {
        setItdd(itddRes.value);
        setState('ready');
      } else {
        setState('offline');
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const barData = useMemo<ChartData<'bar'> | null>(() => {
    if (!itdd || itdd.scoreboard.length === 0) return null;
    return {
      labels: itdd.scoreboard.map(e => e.venture),
      datasets: [
        {
          label: 'Passed',
          data: itdd.scoreboard.map(e => e.passed),
          backgroundColor: COLOR_PASSED,
          borderRadius: 4,
          maxBarThickness: 26,
        },
        {
          label: 'Failed',
          data: itdd.scoreboard.map(e => e.failed),
          backgroundColor: COLOR_FAILED,
          borderRadius: 4,
          maxBarThickness: 26,
        },
      ],
    };
  }, [itdd]);

  const barOptions = useMemo<ChartOptions<'bar'>>(() => {
    const tick = readToken('--text-secondary', '#9aa1b5');
    const grid = readToken('--border', '#2a2e3d');
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { color: tick, boxWidth: 12, boxHeight: 12 } },
      },
      scales: {
        x: {
          ticks: { color: tick, autoSkip: false, maxRotation: 40 },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: { color: tick, precision: 0 },
          grid: { color: grid },
        },
      },
    };
  }, [itdd]);

  const doughnutData = useMemo<ChartData<'doughnut'> | null>(() => {
    if (!itdd || itdd.scoreboard.length === 0) return null;
    const compliant = itdd.scoreboard.filter(e => e.compliant).length;
    const failing = itdd.scoreboard.filter(e => !e.compliant && e.tests > 0).length;
    const noTests = itdd.scoreboard.length - compliant - failing;
    return {
      labels: ['Compliant', 'Failing', 'No tests'],
      datasets: [
        {
          data: [compliant, failing, noTests],
          backgroundColor: [COLOR_PASSED, COLOR_FAILED, COLOR_NO_TESTS],
          borderColor: readToken('--surface', '#1a1d27'),
          borderWidth: 2,
          hoverOffset: 6,
        },
      ],
    };
  }, [itdd]);

  const doughnutOptions = useMemo<ChartOptions<'doughnut'>>(() => {
    const tick = readToken('--text-secondary', '#9aa1b5');
    return {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '58%',
      plugins: {
        legend: { position: 'bottom', labels: { color: tick, boxWidth: 12, boxHeight: 12 } },
      },
    };
  }, [itdd]);

  const totalVentures = ventures.length || itdd?.total_ventures || 0;

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h2>Charts</h2>
        <p>ITDD test metrics across the venture portfolio</p>
      </div>

      {state === 'loading' && <div className={styles.loading}>Loading metrics…</div>}

      {state === 'offline' && (
        <div className={styles.offline}>
          <strong>Backend offline</strong>
          Start the EVO-HUB backend on :8000 to see live ITDD metrics.
        </div>
      )}

      {state === 'ready' && itdd && (
        <>
          <div className={styles.statRow}>
            <div className={styles.stat}>
              <div className={styles.statValue}>{totalVentures}</div>
              <div className={styles.statLabel}>Ventures</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{itdd.with_tests}</div>
              <div className={styles.statLabel}>With tests</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{itdd.compliant}</div>
              <div className={styles.statLabel}>Compliant</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{Math.round(itdd.compliance_ratio * 100)}%</div>
              <div className={styles.statLabel}>Compliance</div>
            </div>
          </div>

          {barData ? (
            <div className={styles.chartsGrid}>
              <div className={styles.card}>
                <h3>Tests per venture</h3>
                <p className={styles.cardSub}>Passed vs failed test counts from the ITDD scoreboard</p>
                <div className={styles.chartBox}>
                  <Chart
                    type="bar"
                    data={barData}
                    options={barOptions}
                    ariaLabel="Bar chart of passed and failed tests per venture"
                  />
                </div>
              </div>
              <div className={styles.card}>
                <h3>Compliance breakdown</h3>
                <p className={styles.cardSub}>Ventures by ITDD state</p>
                <div className={styles.chartBox}>
                  {doughnutData && (
                    <Chart
                      type="doughnut"
                      data={doughnutData}
                      options={doughnutOptions}
                      ariaLabel="Doughnut chart of ventures that are compliant, failing, or without tests"
                    />
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className={styles.offline}>
              <strong>No scoreboard data</strong>
              The ITDD scoreboard returned no ventures.
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Charts;
