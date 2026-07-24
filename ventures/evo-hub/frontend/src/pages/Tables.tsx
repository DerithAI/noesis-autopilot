import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { useToast } from '../components/Toast';
import styles from './Tables.module.css';

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

type SortKey = keyof Venture;
type SortDir = 'asc' | 'desc';

const Tables = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [ventures, setVentures] = useState<Venture[]>([]);
  const [itdd, setItdd] = useState<ITDDEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [filter, setFilter] = useState('');
  const toast = useToast();

  useEffect(() => {
    const load = async () => {
      try {
        const [v, i] = await Promise.all([
          apiFetch<Venture[]>('/api/ventures'),
          apiFetch<{ scoreboard: ITDDEntry[] }>('/api/itdd/status'),
        ]);
        setVentures(v);
        setItdd(i.scoreboard);
      } catch (e) {
        toast.error('Failed to load table data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [toast]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sorted = useMemo(() => {
    const filtered = ventures.filter((v) =>
      filter
        ? v.name.toLowerCase().includes(filter.toLowerCase()) ||
          v.seed.toLowerCase().includes(filter.toLowerCase()) ||
          v.stack.toLowerCase().includes(filter.toLowerCase())
        : true,
    );
    return [...filtered].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      const cmp = typeof aVal === 'string' ? aVal.localeCompare(bVal as string) : (aVal as number) - (bVal as number);
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [ventures, filter, sortKey, sortDir]);

  const getItdd = (name: string) => itdd.find((e) => e.venture === name);

  if (loading) return <div className={styles.loading}>Loading tables...</div>;

  return (
    <div className={styles.tables}>
      <header className={styles.header}>
        <h2>📋 Ventures Table</h2>
        <input
          type="text"
          placeholder="Filter by name, seed, or stack..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className={styles.filter}
          aria-label="Filter ventures"
        />
      </header>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              {(['name', 'seed', 'stack', 'files', 'status'] as SortKey[]).map((key) => (
                <th key={key} onClick={() => handleSort(key)} className={styles.sortable}>
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                  {sortKey === key && <span className={styles.sortArrow}>{sortDir === 'asc' ? ' ↑' : ' ↓'}</span>}
                </th>
              ))}
              <th>ITDD</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((v) => {
              const it = getItdd(v.name);
              return (
                <tr key={v.name} onClick={() => navigate(`/venture/${encodeURIComponent(v.name)}`)} style={{ cursor: 'pointer' }} role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === 'Enter') navigate(`/venture/${encodeURIComponent(v.name)}`); }}>
                  <td>{v.name}</td>
                  <td>{v.seed}</td>
                  <td>{v.stack}</td>
                  <td>{v.files}</td>
                  <td>
                    <span className={`${styles.badge} ${v.status === 'live' ? styles.live : styles.deployed}`}>
                      {v.status}
                    </span>
                  </td>
                  <td>
                    {it ? (
                      <span className={it.compliant ? styles.green : styles.red}>
                        {it.passed}/{it.tests}
                      </span>
                    ) : (
                      <span className={styles.gray}>—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className={styles.footer}>
        Showing {sorted.length} of {ventures.length} ventures
      </p>
    </div>
  );
};

export default Tables;
