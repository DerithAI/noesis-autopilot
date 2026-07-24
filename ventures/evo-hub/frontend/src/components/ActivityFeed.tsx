/**
 * Activity Feed — tracks recent actions in EVO-DASH.
 * Phase 3.4: Activity feed
 */
import { useCallback, useRef, useState } from 'react';
import styles from './ActivityFeed.module.css';

export interface ActivityEntry {
  id: number;
  type: 'generate' | 'test' | 'cognitive' | 'howl' | 'insights' | 'deploy';
  message: string;
  timestamp: Date;
  success?: boolean;
}

interface ActivityFeedProps {
  entries: ActivityEntry[];
  maxVisible?: number;
}

export const ActivityFeed = ({ entries, maxVisible = 10 }: ActivityFeedProps) => {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? entries : entries.slice(0, maxVisible);

  const typeIcon = (type: ActivityEntry['type']) => {
    switch (type) {
      case 'generate': return '🚀';
      case 'test': return '🧪';
      case 'cognitive': return '🧠';
      case 'howl': return '🐺';
      case 'insights': return '📊';
      case 'deploy': return '📦';
      default: return '📌';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  if (entries.length === 0) return null;

  return (
    <section className={styles.feed}>
      <div className={styles.feedHeader}>
        <h3>📋 Activity Feed</h3>
        {entries.length > maxVisible && (
          <button className={styles.expandBtn} onClick={() => setExpanded(!expanded)}>
            {expanded ? 'Show less' : `Show all (${entries.length})`}
          </button>
        )}
      </div>
      <ul className={styles.feedList}>
        {visible.map((entry) => (
          <li key={entry.id} className={`${styles.feedItem} ${entry.success === false ? styles.failed : ''}`}>
            <span className={styles.feedIcon}>{typeIcon(entry.type)}</span>
            <span className={styles.feedMessage}>{entry.message}</span>
            <span className={styles.feedTime}>{formatTime(entry.timestamp)}</span>
            {entry.success === false && <span className={styles.feedFail}>failed</span>}
          </li>
        ))}
      </ul>
    </section>
  );
};

let nextId = 0;

export function useActivityFeed() {
  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const entriesRef = useRef<ActivityEntry[]>([]);

  const add = useCallback((type: ActivityEntry['type'], message: string, success?: boolean) => {
    const entry: ActivityEntry = {
      id: nextId++,
      type,
      message,
      timestamp: new Date(),
      success,
    };
    entriesRef.current = [entry, ...entriesRef.current].slice(0, 100);
    setEntries([...entriesRef.current]);
  }, []);

  const clear = useCallback(() => {
    entriesRef.current = [];
    setEntries([]);
  }, []);

  return { entries, add, clear };
}
