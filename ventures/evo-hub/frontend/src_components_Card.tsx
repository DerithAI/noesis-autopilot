```tsx
import React from 'react';
import styles from './Card.module.css';

interface CardProps {
  title?: string;
}

const Card: React.FC<CardProps> = ({ title, children }) => {
  return (
    <div className={styles.card}>
      {title && <h3>{title}</h3>}
      {children}
    </div>
  );
};

export default Card;
```