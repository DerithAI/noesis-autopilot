import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { useToast } from '../components/Toast';
import styles from './VentureDetail.module.css';

interface VentureFile {
  path: string;
  size: number;
  type: string;
}

interface VentureTestResult {
  suite: string;
  passed: boolean;
  output: string;
}

interface VentureDetail {
  name: string;
  seed: string;
  stack: string;
  files: number;
  status: string;
  created_at?: string;
  file_list?: VentureFile[];
  test_results?: VentureTestResult[];
  itdd?: {
    compliant: boolean;
    tests: number;
    passed: number;
    failed: number;
  };
}

const VentureDetail = () => {
  const { name } = useParams<{ name: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const [venture, setVenture] = useState<VentureDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [testOutput, setTestOutput] = useState<string | null>(null);

  const loadVenture = useCallback(async () => {
    if (!name) return;
    setLoading(true);
    try {
      const [v, itddRes] = await Promise.all([
        apiFetch<VentureDetail>(`/api/ventures/${encodeURIComponent(name)}`),
        apiFetch<{ scoreboard: { venture: string; compliant: boolean; tests: number; passed: number; failed: number }[] }>('/api/itdd/status'),
      ]);
      const itdd = itddRes.scoreboard.find((e) => e.venture === name);
      setVenture({ ...v, itdd: itdd || undefined });
    } catch (e) {
      toast.error('Failed to load venture details');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [name, navigate, toast]);

  useEffect(() => {
    loadVenture();
  }, [loadVenture]);

  const handleTest = async () => {
    if (!name || testing) return;
    setTesting(true);
    setTestOutput(null);
    try {
      const res = await apiFetch<{ suites: { suite: string; passed: boolean; output: string }[]; total_passed: number; total_suites: number }>(
        `/api/action/tests?venture=${encodeURIComponent(name)}`,
      );
      setTestOutput(
        `${res.total_passed}/${res.total_suites} suites passed\n` +
        res.suites.map((s) => `${s.passed ? '✅' : '❌'} ${s.suite}\n${s.output}`).join('\n'),
      );
      toast.success(`Tests complete: ${res.total_passed}/${res.total_suites} passed`);
      loadVenture(); // Refresh ITDD status
    } catch (e) {
      toast.error('Test run failed');
      setTestOutput('Test run failed. Check console for details.');
    } finally {
      setTesting(false);
    }
  };

  const handleDeploy = async () => {
    if (!name) return;
    toast.success(`Deploy triggered for "${name}"`);
  };

  if (loading) return <div className={styles.loading}>Loading venture details...</div>;
  if (!venture) return <div className={styles.notFound}>Venture not found</div>;

  return (
    <div className={styles.detail}>
      <header className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate('/dashboard')} aria-label="Back to dashboard">
          ← Back
        </button>
        <div className={styles.titleSection}>
          <h1>{venture.name}</h1>
          <span className={`${styles.badge} ${venture.status === 'live' ? styles.live : styles.deployed}`}>
            {venture.status}
          </span>
        </div>
      </header>

      <section className={styles.overview}>
        <div className={styles.card}>
          <h3>Seed</h3>
          <p>{venture.seed}</p>
        </div>
        <div className={styles.card}>
          <h3>Stack</h3>
          <p>{venture.stack}</p>
        </div>
        <div className={styles.card}>
          <h3>Files</h3>
          <p>{venture.files}</p>
        </div>
        <div className={styles.card}>
          <h3>ITDD</h3>
          {venture.itdd ? (
            <p className={venture.itdd.compliant ? styles.green : styles.red}>
              {venture.itdd.passed}/{venture.itdd.tests} tests
            </p>
          ) : (
            <p className={styles.gray}>No test data</p>
          )}
        </div>
      </section>

      <section className={styles.actions}>
        <button className={styles.btnPrimary} onClick={handleTest} disabled={testing}>
          {testing ? '🔄 Testing...' : '🧪 Run Tests'}
        </button>
        <button className={styles.btnSecondary} onClick={handleDeploy}>
          🚀 Deploy
        </button>
        <button className={styles.btnSecondary} onClick={loadVenture}>
          🔄 Refresh
        </button>
      </section>

      {testOutput && (
        <section className={styles.testOutput}>
          <h3>Test Results</h3>
          <pre>{testOutput}</pre>
        </section>
      )}

      {venture.file_list && venture.file_list.length > 0 && (
        <section className={styles.files}>
          <h3>Files ({venture.file_list.length})</h3>
          <ul className={styles.fileList}>
            {venture.file_list.map((f) => (
              <li key={f.path} className={styles.fileItem}>
                <span className={styles.fileIcon}>{f.type === 'py' ? '🐍' : f.type === 'ts' || f.type === 'tsx' ? '⚛️' : '📄'}</span>
                <span className={styles.filePath}>{f.path}</span>
                <span className={styles.fileSize}>{(f.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
};

export default VentureDetail;
