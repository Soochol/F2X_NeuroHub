/**
 * Enhanced KPI Card Component
 * Displays a key performance indicator with trend and status
 */

import type { ReactNode } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import styles from './EnhancedKPICard.module.css';

export type KPIStatus = 'success' | 'warning' | 'error' | 'info' | 'neutral';
export type TrendDirection = 'up' | 'down' | 'neutral';

interface EnhancedKPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: TrendDirection;
  trendValue?: string;
  trendLabel?: string;
  status?: KPIStatus;
  onClick?: () => void;
  className?: string;
}

export const EnhancedKPICard = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
  trendLabel,
  status = 'neutral',
  onClick,
  className,
}: EnhancedKPICardProps) => {
  const getTrendIcon = () => {
    if (!trend) return null;

    switch (trend) {
      case 'up':
        return <TrendingUp size={14} />;
      case 'down':
        return <TrendingDown size={14} />;
      case 'neutral':
        return <Minus size={14} />;
    }
  };

  const getTrendClass = () => {
    if (!trend) return '';

    switch (trend) {
      case 'up':
        return styles.trendUp;
      case 'down':
        return styles.trendDown;
      case 'neutral':
        return styles.trendNeutral;
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case 'success':
        return styles.statusSuccess;
      case 'warning':
        return styles.statusWarning;
      case 'error':
        return styles.statusError;
      case 'info':
        return styles.statusInfo;
      default:
        return styles.statusNeutral;
    }
  };

  return (
    <div
      className={`${styles.card} ${getStatusClass()} ${onClick ? styles.clickable : ''} ${className || ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className={styles.header}>
        <span className={styles.title}>{title}</span>
        {icon && <span className={styles.icon}>{icon}</span>}
      </div>

      <div className={styles.valueContainer}>
        <span className={styles.value}>{value}</span>
        {subtitle && <span className={styles.subtitle}>{subtitle}</span>}
      </div>

      {(trend || trendValue) && (
        <div className={`${styles.trend} ${getTrendClass()}`}>
          {getTrendIcon()}
          {trendValue && <span className={styles.trendValue}>{trendValue}</span>}
          {trendLabel && <span className={styles.trendLabel}>{trendLabel}</span>}
        </div>
      )}
    </div>
  );
};
