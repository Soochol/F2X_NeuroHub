/**
 * Offline Queue Panel Component
 *
 * 오프라인 큐 시각화 패널
 * - 대기 중인 항목 목록
 * - 항목별 상태 표시
 * - 재시도/삭제 기능
 */
import { useState } from 'react';
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Trash2,
  ChevronRight,
  Package,
  Settings,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/cn';

type QueueItemStatus = 'pending' | 'syncing' | 'success' | 'error' | 'retrying';
type QueueItemType = 'process_start' | 'process_complete' | 'measurement' | 'defect';

interface QueueItem {
  id: string;
  type: QueueItemType;
  status: QueueItemStatus;
  data: {
    wipNumber?: string;
    processName?: string;
    timestamp: Date;
  };
  retryCount: number;
  maxRetries: number;
  errorMessage?: string;
}

interface OfflineQueuePanelProps {
  /** 큐 항목 목록 */
  items: QueueItem[];
  /** 전체 동기화 시작 */
  onSyncAll?: () => void;
  /** 개별 항목 재시도 */
  onRetryItem?: (id: string) => void;
  /** 개별 항목 삭제 */
  onDeleteItem?: (id: string) => void;
  /** 전체 삭제 */
  onClearAll?: () => void;
  /** 동기화 중 여부 */
  isSyncing?: boolean;
  /** 커스텀 클래스 */
  className?: string;
}

export const OfflineQueuePanel: React.FC<OfflineQueuePanelProps> = ({
  items,
  onSyncAll,
  onRetryItem,
  onDeleteItem,
  onClearAll,
  isSyncing = false,
  className,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // 상태별 카운트
  const pendingCount = items.filter((i) => i.status === 'pending').length;
  const errorCount = items.filter((i) => i.status === 'error').length;
  const syncingCount = items.filter((i) => i.status === 'syncing' || i.status === 'retrying').length;

  // 타입 아이콘
  const getTypeIcon = (type: QueueItemType) => {
    switch (type) {
      case 'process_start':
        return <Zap className="w-4 h-4 text-primary-500" />;
      case 'process_complete':
        return <CheckCircle2 className="w-4 h-4 text-success-500" />;
      case 'measurement':
        return <Settings className="w-4 h-4 text-info-500" />;
      case 'defect':
        return <AlertTriangle className="w-4 h-4 text-danger-500" />;
      default:
        return <Package className="w-4 h-4 text-neutral-500" />;
    }
  };

  // 타입 라벨
  const getTypeLabel = (type: QueueItemType) => {
    switch (type) {
      case 'process_start':
        return '착공';
      case 'process_complete':
        return '완료';
      case 'measurement':
        return '측정';
      case 'defect':
        return '불량';
      default:
        return '기타';
    }
  };

  // 상태 스타일
  const getStatusStyle = (status: QueueItemStatus) => {
    switch (status) {
      case 'pending':
        return { color: 'text-warning-600', bg: 'bg-warning-100', label: '대기' };
      case 'syncing':
        return { color: 'text-primary-600', bg: 'bg-primary-100', label: '전송 중' };
      case 'success':
        return { color: 'text-success-600', bg: 'bg-success-100', label: '완료' };
      case 'error':
        return { color: 'text-danger-600', bg: 'bg-danger-100', label: '오류' };
      case 'retrying':
        return { color: 'text-warning-600', bg: 'bg-warning-100', label: '재시도' };
      default:
        return { color: 'text-neutral-600', bg: 'bg-neutral-100', label: '알 수 없음' };
    }
  };

  // 시간 포맷
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  };

  if (items.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <CheckCircle2 className="w-16 h-16 text-success-300 mb-4" />
        <p className="text-lg font-medium text-neutral-700">모든 데이터가 동기화되었습니다</p>
        <p className="text-sm text-neutral-500 mt-1">대기 중인 항목이 없습니다</p>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col', className)}>
      {/* 요약 헤더 */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-warning-500" />
            <span className="text-sm font-medium">{pendingCount} 대기</span>
          </div>
          {errorCount > 0 && (
            <div className="flex items-center gap-2">
              <XCircle className="w-4 h-4 text-danger-500" />
              <span className="text-sm font-medium text-danger-600">{errorCount} 오류</span>
            </div>
          )}
          {syncingCount > 0 && (
            <div className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-primary-500 animate-spin" />
              <span className="text-sm font-medium">{syncingCount} 전송 중</span>
            </div>
          )}
        </div>

        {/* 액션 버튼 */}
        <div className="flex items-center gap-2">
          {onClearAll && items.length > 0 && (
            <button
              onClick={onClearAll}
              className="p-2 text-danger-500 hover:bg-danger-50 rounded-lg transition-colors"
              title="전체 삭제"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          {onSyncAll && pendingCount > 0 && (
            <button
              onClick={onSyncAll}
              disabled={isSyncing}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg',
                'bg-primary-500 text-white',
                'hover:bg-primary-600',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-colors'
              )}
            >
              <RefreshCw className={cn('w-4 h-4', isSyncing && 'animate-spin')} />
              <span className="text-sm font-medium">
                {isSyncing ? '동기화 중...' : '지금 동기화'}
              </span>
            </button>
          )}
        </div>
      </div>

      {/* 큐 목록 */}
      <div className="space-y-2">
        {items.map((item) => {
          const statusStyle = getStatusStyle(item.status);
          const isExpanded = expandedId === item.id;

          return (
            <div
              key={item.id}
              className={cn(
                'bg-white rounded-xl border',
                'overflow-hidden',
                'transition-all duration-200',
                item.status === 'error' ? 'border-danger-200' : 'border-neutral-200'
              )}
            >
              {/* 메인 행 */}
              <button
                onClick={() => setExpandedId(isExpanded ? null : item.id)}
                className="w-full flex items-center gap-3 p-4 text-left"
              >
                {/* 타입 아이콘 */}
                <div className="w-10 h-10 flex items-center justify-center rounded-full bg-neutral-100">
                  {getTypeIcon(item.type)}
                </div>

                {/* 정보 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-neutral-800 truncate">
                      {item.data.wipNumber || '알 수 없음'}
                    </span>
                    <span
                      className={cn(
                        'px-2 py-0.5 rounded-full text-xs font-medium',
                        statusStyle.bg,
                        statusStyle.color
                      )}
                    >
                      {statusStyle.label}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-neutral-500">
                    <span>{getTypeLabel(item.type)}</span>
                    <span>·</span>
                    <span>{item.data.processName}</span>
                    <span>·</span>
                    <span>{formatTime(item.data.timestamp)}</span>
                  </div>
                </div>

                {/* 상태 아이콘 */}
                <div className="flex items-center gap-2">
                  {item.status === 'syncing' || item.status === 'retrying' ? (
                    <RefreshCw className="w-5 h-5 text-primary-500 animate-spin" />
                  ) : item.status === 'error' ? (
                    <XCircle className="w-5 h-5 text-danger-500" />
                  ) : item.status === 'success' ? (
                    <CheckCircle2 className="w-5 h-5 text-success-500" />
                  ) : (
                    <Clock className="w-5 h-5 text-warning-500" />
                  )}
                  <ChevronRight
                    className={cn(
                      'w-5 h-5 text-neutral-400 transition-transform',
                      isExpanded && 'rotate-90'
                    )}
                  />
                </div>
              </button>

              {/* 확장 영역 */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-0 border-t border-neutral-100 bg-neutral-50">
                  {/* 에러 메시지 */}
                  {item.errorMessage && (
                    <div className="flex items-start gap-2 p-3 mb-3 bg-danger-50 rounded-lg text-sm text-danger-700">
                      <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <span>{item.errorMessage}</span>
                    </div>
                  )}

                  {/* 재시도 정보 */}
                  {item.retryCount > 0 && (
                    <div className="text-xs text-neutral-500 mb-3">
                      재시도: {item.retryCount} / {item.maxRetries}
                    </div>
                  )}

                  {/* 액션 버튼 */}
                  <div className="flex items-center gap-2">
                    {onRetryItem && item.status === 'error' && (
                      <button
                        onClick={() => onRetryItem(item.id)}
                        className={cn(
                          'flex items-center gap-2 px-4 py-2 rounded-lg',
                          'bg-primary-500 text-white text-sm',
                          'hover:bg-primary-600 transition-colors'
                        )}
                      >
                        <RefreshCw className="w-4 h-4" />
                        재시도
                      </button>
                    )}
                    {onDeleteItem && (
                      <button
                        onClick={() => onDeleteItem(item.id)}
                        className={cn(
                          'flex items-center gap-2 px-4 py-2 rounded-lg',
                          'bg-neutral-200 text-neutral-700 text-sm',
                          'hover:bg-neutral-300 transition-colors'
                        )}
                      >
                        <Trash2 className="w-4 h-4" />
                        삭제
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default OfflineQueuePanel;
