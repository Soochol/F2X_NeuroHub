/**
 * Recent History Component
 *
 * 최근 작업 WIP 빠른 접근
 * - 최근 WIP 목록
 * - 빠른 선택
 * - 상태 표시
 */
import { useState } from 'react';
import {
  Clock,
  ChevronRight,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Search,
  Star,
  StarOff,
} from 'lucide-react';
import { cn } from '@/lib/cn';

type WipStatus = 'completed' | 'failed' | 'in_progress' | 'pending';

interface RecentWipItem {
  id: string;
  wipNumber: string;
  processName: string;
  status: WipStatus;
  timestamp: Date;
  isFavorite?: boolean;
}

interface RecentHistoryProps {
  /** 최근 WIP 목록 */
  items: RecentWipItem[];
  /** WIP 선택 콜백 */
  onSelect: (wipNumber: string) => void;
  /** 즐겨찾기 토글 콜백 */
  onToggleFavorite?: (id: string) => void;
  /** 최대 표시 개수 */
  maxItems?: number;
  /** 커스텀 클래스 */
  className?: string;
}

export const RecentHistory: React.FC<RecentHistoryProps> = ({
  items,
  onSelect,
  onToggleFavorite,
  maxItems = 10,
  className,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<WipStatus | 'all' | 'favorite'>('all');

  // 필터링된 아이템
  const filteredItems = items
    .filter((item) => {
      // 검색 필터
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          item.wipNumber.toLowerCase().includes(query) ||
          item.processName.toLowerCase().includes(query)
        );
      }
      return true;
    })
    .filter((item) => {
      // 상태 필터
      if (filter === 'all') return true;
      if (filter === 'favorite') return item.isFavorite;
      return item.status === filter;
    })
    .slice(0, maxItems);

  // 상태 아이콘
  const StatusIcon: React.FC<{ status: WipStatus }> = ({ status }) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-success-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-danger-500" />;
      case 'in_progress':
        return <RefreshCw className="w-4 h-4 text-primary-500 animate-spin" />;
      case 'pending':
        return <AlertCircle className="w-4 h-4 text-warning-500" />;
    }
  };

  // 상태 라벨
  const getStatusLabel = (status: WipStatus) => {
    switch (status) {
      case 'completed':
        return '완료';
      case 'failed':
        return '실패';
      case 'in_progress':
        return '진행중';
      case 'pending':
        return '대기';
    }
  };

  // 시간 포맷
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  return (
    <div className={cn('flex flex-col', className)}>
      {/* 헤더 */}
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-neutral-500" />
        <h3 className="text-lg font-semibold text-neutral-800">최근 작업</h3>
        <span className="text-sm text-neutral-400 ml-auto">
          {filteredItems.length}개
        </span>
      </div>

      {/* 검색 */}
      <div className="relative mb-3">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="WIP 번호 검색..."
          className={cn(
            'w-full pl-9 pr-4 py-2.5 rounded-xl',
            'bg-neutral-100 border-0',
            'text-sm text-neutral-800',
            'placeholder:text-neutral-400',
            'focus:outline-none focus:ring-2 focus:ring-primary-500/30'
          )}
        />
      </div>

      {/* 필터 칩 */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
        {(['all', 'favorite', 'completed', 'failed', 'in_progress'] as const).map(
          (f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap',
                'transition-colors duration-200',
                filter === f
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
              )}
            >
              {f === 'all'
                ? '전체'
                : f === 'favorite'
                ? '⭐ 즐겨찾기'
                : getStatusLabel(f)}
            </button>
          )
        )}
      </div>

      {/* WIP 목록 */}
      <div className="space-y-2">
        {filteredItems.length === 0 ? (
          <div className="text-center py-8 text-neutral-400">
            <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>최근 작업 기록이 없습니다</p>
          </div>
        ) : (
          filteredItems.map((item) => (
            <RecentHistoryItem
              key={item.id}
              item={item}
              onSelect={onSelect}
              onToggleFavorite={onToggleFavorite}
              formatTime={formatTime}
              StatusIcon={StatusIcon}
            />
          ))
        )}
      </div>
    </div>
  );
};

/**
 * 개별 히스토리 아이템
 */
interface RecentHistoryItemProps {
  item: RecentWipItem;
  onSelect: (wipNumber: string) => void;
  onToggleFavorite?: (id: string) => void;
  formatTime: (date: Date) => string;
  StatusIcon: React.FC<{ status: WipStatus }>;
}

const RecentHistoryItem: React.FC<RecentHistoryItemProps> = ({
  item,
  onSelect,
  onToggleFavorite,
  formatTime,
  StatusIcon,
}) => {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3 rounded-xl',
        'bg-white border border-neutral-100',
        'hover:border-primary-200 hover:shadow-sm',
        'transition-all duration-200',
        'cursor-pointer group'
      )}
      onClick={() => onSelect(item.wipNumber)}
    >
      {/* 상태 아이콘 */}
      <div className="w-8 h-8 flex items-center justify-center rounded-full bg-neutral-50">
        <StatusIcon status={item.status} />
      </div>

      {/* 정보 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-neutral-800 truncate">
            {item.wipNumber}
          </span>
          {item.isFavorite && (
            <Star className="w-3.5 h-3.5 text-warning-500 fill-warning-500" />
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-neutral-500">
          <span className="truncate">{item.processName}</span>
          <span>·</span>
          <span className="whitespace-nowrap">{formatTime(item.timestamp)}</span>
        </div>
      </div>

      {/* 액션 */}
      <div className="flex items-center gap-1">
        {onToggleFavorite && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite(item.id);
            }}
            className={cn(
              'p-2 rounded-full',
              'opacity-0 group-hover:opacity-100',
              'hover:bg-neutral-100',
              'transition-all duration-200'
            )}
          >
            {item.isFavorite ? (
              <Star className="w-4 h-4 text-warning-500 fill-warning-500" />
            ) : (
              <StarOff className="w-4 h-4 text-neutral-400" />
            )}
          </button>
        )}
        <ChevronRight className="w-5 h-5 text-neutral-300 group-hover:text-primary-500 transition-colors" />
      </div>
    </div>
  );
};

/**
 * 컴팩트 최근 기록 (FAB 내부용)
 */
interface RecentHistoryCompactProps {
  items: RecentWipItem[];
  onSelect: (wipNumber: string) => void;
  maxItems?: number;
}

export const RecentHistoryCompact: React.FC<RecentHistoryCompactProps> = ({
  items,
  onSelect,
  maxItems = 5,
}) => {
  const recentItems = items.slice(0, maxItems);

  return (
    <div className="space-y-1">
      {recentItems.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect(item.wipNumber)}
          className={cn(
            'w-full flex items-center gap-3 p-2 rounded-lg',
            'text-left',
            'hover:bg-neutral-50',
            'transition-colors duration-150'
          )}
        >
          <span className="font-mono text-sm text-neutral-700">{item.wipNumber}</span>
          <span className="text-xs text-neutral-400 truncate">{item.processName}</span>
        </button>
      ))}
    </div>
  );
};

export default RecentHistory;
