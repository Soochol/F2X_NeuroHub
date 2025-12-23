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
        'grid grid-cols-2 lg:grid-cols-4 gap-4',
        'w-full',
        className
      )}
    >
      {statItems.map((item) => (
        <div
          key={item.label}
          className={cn(
            'glass-card p-4 text-center group relative overflow-hidden',
            'hover:bg-white/10 transition-all duration-300'
          )}
        >
          {/* Subtle accent line */}
          <div className={cn('absolute top-0 left-0 w-full h-1 opacity-50', item.bgClass.replace('bg-', 'bg-').replace('50', '500'))} />

          <div className={cn('flex items-center justify-center mb-2 opacity-80 group-hover:opacity-100 transition-opacity', item.colorClass.replace('-600', '-400'))}>
            {item.icon}
          </div>
          <div
            className={cn(
              'text-3xl font-black leading-none mb-1 tracking-tight',
              'text-white group-hover:scale-110 transition-transform'
            )}
          >
            {item.value}
          </div>
          <div className="text-xs font-bold text-neutral-500 uppercase tracking-widest">
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
};
