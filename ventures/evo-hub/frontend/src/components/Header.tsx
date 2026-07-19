import React from 'react';
import { ThemeMode } from '../types';

interface HeaderProps {
  themeMode: ThemeMode;
  onToggleTheme: () => void;
}

const Header: React.FC<HeaderProps> = ({ themeMode, onToggleTheme }) => {
  return (
    <header className={`header ${themeMode}`}>
      <h1>EVO-HUB</h1>
      <button onClick={onToggleTheme} aria-label="Toggle theme">
        {themeMode === 'dark' ? '☀️' : '🌙'}
      </button>
    </header>
  );
};

export default Header;
