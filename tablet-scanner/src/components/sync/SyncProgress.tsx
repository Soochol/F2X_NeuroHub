/**
 * Sync Progress Component
 *
 * 원형 동기화 프로그레스
 * - 애니메이션 효과
 * - 상태별 색상
 * - 완료 시 체크마크
 */
import { useEffect, useState } from 'react';
import { Check, RefreshCw, AlertTriangle, WifiOff } from 'lucide-react';
import { cn } from '@/lib/cn';

type SyncState = 'idle' | 'syncing' | 'success' | 'error' | 'offline';

interface SyncProgressProps {
  /** 진행률 (0-100) */
  progress: number;
  /** 동기화 상태 */
  state: SyncState;
  /** 총 항목 수 */
  total?: number;
  /** 완료된 항목 수 */
  completed?: number;
  /** 크기 */
  size?: 'sm' | 'md' | 'lg';
  /** 두께 */
  strokeWidth?: number;
  /** 커스텀 클래스 */
  className?: string;
}

export const SyncProgress: React.FC<SyncProgressProps> = ({
  progress,
  state,
  total: _total,
  completed: _completed,
  size = 'md',
  strokeWidth,
  className,
}) => {
  // _total and _completed are passed through to SyncStatusCard but not used directly here
  void _total;
  void _completed;
  const [animatedProgress, setAnimatedProgress] = useState(0);

  // 애니메이션 효과
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  // 크기별 설정
  const sizeConfig = {
    sm: { diameter: 60, defaultStroke: 4, iconSize: 'w-4 h-4', textSize: 'text-xs' },
    md: { diameter: 100, defaultStroke: 6, iconSize: 'w-6 h-6', textSize: 'text-sm' },
    lg: { diameter: 140, defaultStroke: 8, iconSize: 'w-8 h-8', textSize: 'text-base' },
  };

  const config = sizeConfig[size];
  const actualStroke = strokeWidth || config.defaultStroke;
  const radius = (config.diameter - actualStroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (animatedProgress / 100) * circumference;

  // 상태별 색상
  const getStateColors = () => {
    switch (state) {
      case 'syncing':
        return {
          track: 'stroke-primary-100',
          progress: 'stroke-primary-500',
          icon: 'text-primary-500',
          bg: 'bg-primary-50',
        };
      case 'success':
        return {
          track: 'stroke-success-100',
          progress: 'stroke-success-500',
          icon: 'text-success-500',
          bg: 'bg-success-50',
        };
      case 'error':
        return {
          track: 'stroke-danger-100',
          progress: 'stroke-danger-500',
          icon: 'text-danger-500',
          bg: 'bg-danger-50',
        };
      case 'offline':
        return {
          track: 'stroke-neutral-200',
          progress: 'stroke-neutral-400',
          icon: 'text-neutral-500',
          bg: 'bg-neutral-100',
        };
      default:
        return {
          track: 'stroke-neutral-200',
          progress: 'stroke-neutral-400',
          icon: 'text-neutral-500',
          bg: 'bg-neutral-50',
        };
    }
  };

  const colors = getStateColors();

  // 중앙 아이콘
  const getCenterContent = () => {
    if (state === 'success') {
      return <Check className={cn(config.iconSize, colors.icon, 'animate-success-check')} />;
    }
    if (state === 'error') {
      return <AlertTriangle className={cn(config.iconSize, colors.icon)} />;
    }
    if (state === 'offline') {
      return <WifiOff className={cn(config.iconSize, colors.icon)} />;
    }
    if (state === 'syncing') {
      return (
        <div className="flex flex-col items-center">
          <RefreshCw className={cn(config.iconSize, colors.icon, 'animate-spin')} />
          <span className={cn(config.textSize, 'font-bold mt-1', colors.icon)}>
            {Math.round(animatedProgress)}%
          </span>
        </div>
      );
    }
    return (
      <span className={cn(config.textSize, 'font-bold text-neutral-600')}>
        {Math.round(animatedProgress)}%
      </span>
    );
  };

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={config.diameter}
        height={config.diameter}
        className="transform -rotate-90"
      >
        {/* 배경 트랙 */}
        <circle
          cx={config.diameter / 2}
          cy={config.diameter / 2}
          r={radius}
          fill="none"
          strokeWidth={actualStroke}
          className={colors.track}
        />
        {/* 프로그레스 */}
        <circle
          cx={config.diameter / 2}
          cy={config.diameter / 2}
          r={radius}
          fill="none"
          strokeWidth={actualStroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          className={cn(colors.progress, 'transition-all duration-500 ease-out')}
        />
      </svg>

      {/* 중앙 컨텐츠 */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {getCenterContent()}
      </div>
    </div>
  );
};

/**
 * 동기화 상태 카드
 */
interface SyncStatusCardProps {
  state: SyncState;
  progress: number;
  total: number;
  completed: number;
  onRetry?: () => void;
  className?: string;
}

export const SyncStatusCard: React.FC<SyncStatusCardProps> = ({
  state,
  progress,
  total,
  completed,
  onRetry,
  className,
}) => {
  const getStatusText = () => {
    switch (state) {
      case 'syncing':
        return '동기화 중...';
      case 'success':
        return '동기화 완료!';
      case 'error':
        return '동기화 실패';
      case 'offline':
        return '오프라인';
      default:
        return '대기 중';
    }
  };

  return (
    <div
      className={cn(
        'flex items-center gap-4 p-4 rounded-xl',
        'bg-white border border-neutral-200',
        className
      )}
    >
      <SyncProgress progress={progress} state={state} size="sm" />

      <div className="flex-1">
        <div className="font-medium text-neutral-800">{getStatusText()}</div>
        <div className="text-sm text-neutral-500">
          {completed} / {total} 항목
        </div>
      </div>

      {state === 'error' && onRetry && (
        <button
          onClick={onRetry}
          className={cn(
            'px-4 py-2 rounded-lg',
            'bg-primary-500 text-white text-sm font-medium',
            'hover:bg-primary-600 transition-colors'
          )}
        >
          재시도
        </button>
      )}
    </div>
  );
};

/**
 * 미니 동기화 프로그레스 (인라인용)
 */
interface MiniSyncProgressProps {
  progress: number;
  state: SyncState;
  className?: string;
}

export const MiniSyncProgress: React.FC<MiniSyncProgressProps> = ({
  progress,
  state,
  className,
}) => {
  const getColor = () => {
    switch (state) {
      case 'syncing':
        return 'bg-primary-500';
      case 'success':
        return 'bg-success-500';
      case 'error':
        return 'bg-danger-500';
      default:
        return 'bg-neutral-400';
    }
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {state === 'syncing' && (
        <RefreshCw className="w-3 h-3 text-primary-500 animate-spin" />
      )}
      <div className="w-16 h-1 bg-neutral-200 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-300', getColor())}
          style={{ width: `${progress}%` }}
        />
      </div>
      <span className="text-xs text-neutral-500">{Math.round(progress)}%</span>
    </div>
  );
};

export default SyncProgress;
