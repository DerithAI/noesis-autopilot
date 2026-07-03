```tsx
import React from 'react';
import { ThemeMode } from '../types';

interface HeaderProps {
  themeMode: ThemeMode;
}

const Header: React.FC<HeaderProps> = ({ themeMode, ...props }) => {
  const handleToggleTheme = () => {
    setThemeMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <header className={`header ${themeMode}`}>
      <h1>Personalized Evo Learning Path</h1>
      <button onClick={handleToggleTheme}>Toggle Theme</button>
    </header>
  );
};

export default Header;
```