/**
 * Reusable Card Component
 */

import { type ReactNode, type CSSProperties } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  style?: CSSProperties;
}

export const Card = ({ children, title, style }: CardProps) => {
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        ...style,
      }}
    >
      {title && (
        <div
          style={{
            padding: '15px 20px',
            borderBottom: '1px solid #e0e0e0',
            fontWeight: 'bold',
            fontSize: '16px',
          }}
        >
          {title}
        </div>
      )}
      <div style={{ padding: '20px' }}>{children}</div>
    </div>
  );
};
