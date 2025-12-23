/**
 * Statistics Card Component
 *
 * Shows today's work statistics with modern styling
 */
import { Play, CheckCircle, ThumbsUp, ThumbsDown } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { TodayStatistics } from '@/types';

interface StatsCardProps {
  stats: TodayStatistics;
  className?: string;
}

interface StatItem {
  label: string;
  value: number;
  icon: React.ReactNode;
  colorClass: string;
  bgClass: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({ stats, className }) => {
  const statItems: StatItem[] = [
    {
      label: '착공',
      value: stats.started,
      icon: <Play className="w-4 h-4" />,
      colorClass: 'text-primary-600',
      bgClass: 'bg-primary-50',
    },
    {
      label: '완공',
      value: stats.completed,
      icon: <CheckCircle className="w-4 h-4" />,
      colorClass: 'text-violet-600',
      bgClass: 'bg-violet-50',
    },
    {
      label: '합격',
      value: stats.passed,
      icon: <ThumbsUp className="w-4 h-4" />,
      colorClass: 'text-success-600',
      bgClass: 'bg-success-50',
    },
    {
      label: '불량',
      value: stats.failed,
      icon: <ThumbsDown className="w-4 h-4" />,
      colorClass: 'text-danger-600',
      bgClass: 'bg-danger-50',
    },
  ];

  return (
    <div
      className={cn(
        'grid grid-cols-4 gap-2',
        'w-full',
        className
      )}
    >
      {statItems.map((item) => (
        <div
          key={item.label}
          className={cn(
            'rounded-lg py-3 px-2 text-center',
            item.bgClass
          )}
        >
          <div className={cn('flex items-center justify-center mb-1', item.colorClass)}>
            {item.icon}
          </div>
          <div
            className={cn(
              'text-2xl font-bold leading-none',
              item.colorClass
            )}
          >
            {item.value}
          </div>
          <div className="text-xs text-neutral-500 mt-1">
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
};
