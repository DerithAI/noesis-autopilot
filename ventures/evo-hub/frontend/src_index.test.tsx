```tsx
import React from 'react';
import { render } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    const { getByText } = render(<App />);
    expect(getByText('Personalized Evo Learning Path')).toBeInTheDocument();
  });
});
```