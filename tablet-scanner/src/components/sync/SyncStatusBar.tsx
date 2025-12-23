/**
 * Sync Status Bar Component
 *
 * 상단 동기화 상태 표시 바
 * - 온라인/오프라인 상태
 * - 동기화 진행률
 * - 큐 개수 표시
 */
import {
  WifiOff,
  Cloud,
  CloudOff,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
} from 'lucide-react';
import { cn } from '@/lib/cn';

type SyncStatus = 'synced' | 'syncing' | 'pending' | 'error' | 'offline';

interface SyncStatusBarProps {
  /** 온라인 여부 */
  isOnline: boolean;
  /** WebSocket 연결 여부 */
  isConnected?: boolean;
  /** 동기화 상태 */
  syncStatus: SyncStatus;
  /** 대기 중인 항목 수 */
  pendingCount: number;
  /** 동기화 진행률 (0-100) */
  progress?: number;
  /** 마지막 동기화 시간 */
  lastSyncTime?: Date;
  /** 클릭시 상세 패널 열기 */
  onClick?: () => void;
  /** 커스텀 클래스 */
  className?: string;
}

export const SyncStatusBar: React.FC<SyncStatusBarProps> = ({
  isOnline,
  isConnected = false,
  syncStatus,
  pendingCount,
  progress,
  lastSyncTime,
  onClick,
  className,
}) => {
  // 상태별 스타일
  const getStatusStyle = () => {
    if (!isOnline) {
      return {
        bg: 'bg-neutral-100',
        text: 'text-neutral-600',
        icon: <WifiOff className="w-4 h-4" />,
        label: '오프라인',
      };
    }

    switch (syncStatus) {
      case 'synced':
        return {
          bg: 'bg-success-50',
          text: 'text-success-700',
          icon: <CheckCircle2 className="w-4 h-4" />,
          label: '동기화 완료',
        };
      case 'syncing':
        return {
          bg: 'bg-primary-50',
          text: 'text-primary-700',
          icon: <RefreshCw className="w-4 h-4 animate-spin" />,
          label: '동기화 중...',
        };
      case 'pending':
        return {
          bg: 'bg-warning-50',
          text: 'text-warning-700',
          icon: <Cloud className="w-4 h-4" />,
          label: `${pendingCount}개 대기 중`,
        };
      case 'error':
        return {
          bg: 'bg-danger-50',
          text: 'text-danger-700',
          icon: <AlertTriangle className="w-4 h-4" />,
          label: '동기화 오류',
        };
      default:
        return {
          bg: 'bg-neutral-100',
          text: 'text-neutral-600',
          icon: <CloudOff className="w-4 h-4" />,
          label: '연결 끊김',
        };
    }
  };

  const status = getStatusStyle();

  // 시간 포맷
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center justify-between',
        'px-4 py-2',
        'border-b',
        'transition-colors duration-300',
        status.bg,
        status.text,
        onClick && 'cursor-pointer hover:opacity-90',
        className
      )}
    >
      {/* 좌측: 상태 아이콘 & 라벨 */}
      <div className="flex items-center gap-2">
        {status.icon}
        <span className="text-sm font-medium">{status.label}</span>

        {/* 진행률 바 */}
        {syncStatus === 'syncing' && progress !== undefined && (
          <div className="w-24 h-1.5 bg-primary-200 rounded-full overflow-hidden ml-2">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      {/* 우측: 연결 상태 & 시간 */}
      <div className="flex items-center gap-3 text-xs opacity-70">
        {/* WebSocket 연결 상태 */}
        {isOnline && (
          <div className="flex items-center gap-1">
            <span
              className={cn(
                'w-1.5 h-1.5 rounded-full',
                isConnected ? 'bg-success-500 animate-pulse' : 'bg-neutral-400'
              )}
            />
            <span>{isConnected ? '실시간' : '폴링'}</span>
          </div>
        )}

        {/* 마지막 동기화 시간 */}
        {lastSyncTime && isOnline && (
          <span>마지막: {formatTime(lastSyncTime)}</span>
        )}

        {/* 확장 아이콘 */}
        {onClick && <ChevronDown className="w-4 h-4" />}
      </div>
    </button>
  );
};

/**
 * 컴팩트 동기화 인디케이터 (헤더용)
 */
interface SyncIndicatorProps {
  isOnline: boolean;
  syncStatus: SyncStatus;
  pendingCount: number;
  onClick?: () => void;
}

export const SyncIndicator: React.FC<SyncIndicatorProps> = ({
  isOnline,
  syncStatus,
  pendingCount,
  onClick,
}) => {
  const getIcon = () => {
    if (!isOnline) return <WifiOff className="w-5 h-5 text-neutral-400" />;

    switch (syncStatus) {
      case 'synced':
        return <Cloud className="w-5 h-5 text-success-500" />;
      case 'syncing':
        return <RefreshCw className="w-5 h-5 text-primary-500 animate-spin" />;
      case 'pending':
        return <Cloud className="w-5 h-5 text-warning-500" />;
      case 'error':
        return <CloudOff className="w-5 h-5 text-danger-500" />;
      default:
        return <CloudOff className="w-5 h-5 text-neutral-400" />;
    }
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        'relative p-2 rounded-full',
        'hover:bg-neutral-100',
        'transition-colors duration-200'
      )}
    >
      {getIcon()}

      {/* 대기 중 배지 */}
      {pendingCount > 0 && isOnline && (
        <span
          className={cn(
            'absolute -top-0.5 -right-0.5',
            'min-w-[18px] h-[18px] px-1',
            'flex items-center justify-center',
            'text-[10px] font-bold text-white',
            'bg-warning-500 rounded-full',
            'animate-pulse'
          )}
        >
          {pendingCount > 99 ? '99+' : pendingCount}
        </span>
      )}

      {/* 오프라인 배지 */}
      {!isOnline && (
        <span
          className={cn(
            'absolute -top-0.5 -right-0.5',
            'w-3 h-3',
            'bg-danger-500 rounded-full',
            'border-2 border-white'
          )}
        />
      )}
    </button>
  );
};

/**
 * 오프라인 배너
 */
interface OfflineBannerProps {
  isVisible: boolean;
  pendingCount: number;
  onRetry?: () => void;
}

export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  isVisible,
  pendingCount,
  onRetry,
}) => {
  if (!isVisible) return null;

  return (
    <div
      className={cn(
        'fixed top-0 left-0 right-0 z-50',
        'flex items-center justify-center gap-3',
        'px-4 py-3',
        'bg-neutral-800 text-white',
        'animate-slide-down'
      )}
    >
      <WifiOff className="w-5 h-5" />
      <span className="text-sm">
        오프라인 모드 - {pendingCount > 0 && `${pendingCount}개 항목 대기 중`}
      </span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1 text-sm bg-white/20 rounded-full hover:bg-white/30 transition-colors"
        >
          재시도
        </button>
      )}
    </div>
  );
};

export default SyncStatusBar;
