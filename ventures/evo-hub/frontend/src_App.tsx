```tsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Charts from './pages/Charts';
import Tables from './pages/Tables';

const App: React.FC = () => {
  const [themeMode, setThemeMode] = useState('light');

  return (
    <Router>
      <Header themeMode={themeMode} />
      <Sidebar />
      <main className="content">
        <Switch>
          <Route path="/dashboard" exact component={Dashboard} />
          <Route path="/charts" exact component={Charts} />
          <Route path="/tables" exact component={Tables} />
        </Switch>
      </main>
    </Router>
  );
};

export default App;
```