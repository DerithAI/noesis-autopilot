```tsx
import React from 'react';
import Card from '../components/Card';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <Card title="User Progress">
        <p>User progress data goes here.</p>
      </Card>
      <Card title="Course Information">
        <p>Course information data goes here.</p>
      </Card>
    </div>
  );
};

export default Dashboard;
```