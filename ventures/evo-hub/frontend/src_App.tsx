import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Charts from './pages/Charts';
import Tables from './pages/Tables';
import Council from './pages/Council';

const App: React.FC = () => {
  const [themeMode, setThemeMode] = useState('dark');

  return (
    <Router>
      <Header themeMode={themeMode} />
      <Sidebar />
      <main className="content">
        <Switch>
          <Route path="/" exact>
            <Redirect to="/dashboard" />
          </Route>
          <Route path="/dashboard" exact component={Dashboard} />
          <Route path="/council" exact component={Council} />
          <Route path="/charts" exact component={Charts} />
          <Route path="/tables" exact component={Tables} />
        </Switch>
      </main>
    </Router>
  );
};

export default App;
