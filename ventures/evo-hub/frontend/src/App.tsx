import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import { ToastProvider } from './components/Toast';
import Dashboard from './pages/Dashboard';
import Charts from './pages/Charts';
import Tables from './pages/Tables';
import Council from './pages/Council';
import VentureDetail from './pages/VentureDetail';
import { ThemeMode } from './types';

const App: React.FC = () => {
  const [themeMode, setThemeMode] = useState<ThemeMode>('dark');
  const toggleTheme = () => setThemeMode((prev) => (prev === 'light' ? 'dark' : 'light'));

  return (
    <Router>
      <div className={`app ${themeMode}`}>
        <ToastProvider>
          <Header themeMode={themeMode} onToggleTheme={toggleTheme} />
          <Sidebar />
          <main className="content">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/council" element={<Council />} />
              <Route path="/charts" element={<Charts />} />
              <Route path="/tables" element={<Tables />} />
              <Route path="/venture/:name" element={<VentureDetail />} />
            </Routes>
          </main>
        </ToastProvider>
      </div>
    </Router>
  );
};

export default App;
