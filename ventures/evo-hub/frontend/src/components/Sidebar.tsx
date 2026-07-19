import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './Sidebar.module.css';

const Sidebar: React.FC = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/dashboard', label: '📊 Dashboard', icon: '📊' },
    { path: '/council', label: '🏛️ Council', icon: '🏛️' },
    { path: '/charts', label: '📈 Charts', icon: '📈' },
    { path: '/tables', label: '📋 Tables', icon: '📋' },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>EVO-HUB</div>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`${styles.link} ${location.pathname === item.path ? styles.active : ''}`}
          >
            <span className={styles.icon}>{item.icon}</span>
            <span className={styles.label}>{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className={styles.footer}>
        <span className={styles.version}>v1.0.0</span>
        <span className={styles.status}>🟢 Live</span>
      </div>
    </aside>
  );
};

export default Sidebar;
