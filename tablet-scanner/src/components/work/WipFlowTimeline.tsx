/**
 * WIP Flow Timeline Component
 *
 * 8공정 진행 상황을 시각화하는 타임라인
 * 터치 최적화 - 공정 터치로 선택 가능
 */
import { useMemo } from 'react';
import { Check, X, Circle } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { WIPTrace, Process } from '@/types';

// 공정 상태 타입
type ProcessStatus = 'pass' | 'fail' | 'in-progress' | 'pending';

interface WipFlowTimelineProps {
  trace: WIPTrace | null;
  processes: Process[];
  selectedProcessNumber?: number | null;
  onProcessSelect?: (processNumber: number, processId: number) => void;
  disabled?: boolean;
  className?: string;
}

// 공정 짧은 이름 매핑
const PROCESS_SHORT_NAMES: Record<number, string> = {
  1: '레이저',
  2: 'LMA',
  3: '센서',
  4: '펌웨어',
  5: '로봇',
  6: '성능',
  7: '라벨',
  8: '포장',
};

export const WipFlowTimeline: React.FC<WipFlowTimelineProps> = ({
  trace,
  processes,
  selectedProcessNumber,
  onProcessSelect,
  disabled = false,
  className,
}) => {
  // 공정별 상태 계산
  const processStatuses = useMemo(() => {
    const statuses = new Map<number, ProcessStatus>();

    // 기본값: 모두 pending
    for (let i = 1; i <= 8; i++) {
      statuses.set(i, 'pending');
    }

    if (!trace) return statuses;

    // 히스토리에서 상태 파싱
    trace.process_history.forEach((item) => {
      const processNum = item.process_number;

      if (item.complete_time && item.result) {
        // 완료된 공정
        statuses.set(processNum, item.result === 'PASS' ? 'pass' : 'fail');
      } else if (item.start_time && !item.complete_time) {
        // 진행 중인 공정
        statuses.set(processNum, 'in-progress');
      }
    });

    return statuses;
  }, [trace]);

  // 다음 진행할 공정 번호 계산
  const nextProcessNumber = useMemo(() => {
    // 진행 중인 공정이 있으면 해당 공정
    for (let i = 1; i <= 8; i++) {
      if (processStatuses.get(i) === 'in-progress') {
        return i;
      }
    }
    // 아니면 첫 번째 pending 공정
    for (let i = 1; i <= 8; i++) {
      if (processStatuses.get(i) === 'pending') {
        return i;
      }
    }
    return null;
  }, [processStatuses]);

  // 공정 클릭 핸들러
  const handleProcessClick = (processNum: number) => {
    if (disabled) return;

    const process = processes.find((p) => p.process_number === processNum);
    if (process && onProcessSelect) {
      onProcessSelect(processNum, process.id);
    }
  };

  // 현재 선택된 공정 (props 우선, 없으면 nextProcessNumber)
  const activeProcessNumber = selectedProcessNumber ?? nextProcessNumber;

  return (
    <div className={cn('w-full', className)}>
      {/* 타임라인 컨테이너 */}
      <div className="relative flex items-center justify-between px-1">
        {/* 연결선 (배경) */}
        <div className="absolute top-6 left-6 right-6 h-1 bg-neutral-200 rounded-full" />

        {/* 진행된 연결선 */}
        <div
          className="absolute top-6 left-6 h-1 bg-success-400 rounded-full transition-all duration-500"
          style={{
            width: `${Math.max(0, (Array.from(processStatuses.values()).filter((s) => s === 'pass').length - 1) / 7) * 100}%`,
          }}
        />

        {/* 공정 노드들 */}
        {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => {
          const status = processStatuses.get(num) || 'pending';
          const isSelected = activeProcessNumber === num;
          const process = processes.find((p) => p.process_number === num);
          const shortName = PROCESS_SHORT_NAMES[num] || `${num}`;

          return (
            <div key={num} className="relative z-10 flex flex-col items-center">
              {/* 공정 배지 */}
              <button
                type="button"
                onClick={() => handleProcessClick(num)}
                disabled={disabled}
                className={cn(
                  // 기본 스타일
                  'w-12 h-12 rounded-full flex items-center justify-center',
                  'transition-all duration-200',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2',
                  // 터치 피드백
                  !disabled && 'active:scale-95',
                  // 상태별 스타일
                  status === 'pass' && [
                    'bg-success-500 text-white',
                    'focus:ring-success-500',
                  ],
                  status === 'fail' && [
                    'bg-danger-500 text-white',
                    'focus:ring-danger-500',
                  ],
                  status === 'in-progress' && [
                    'bg-primary-500 text-white',
                    'animate-pulse',
                    'focus:ring-primary-500',
                  ],
                  status === 'pending' && [
                    'bg-neutral-100 text-neutral-400',
                    'border-2 border-neutral-300',
                    'focus:ring-neutral-400',
                  ],
                  // 선택됨 표시
                  isSelected && [
                    'ring-4 ring-offset-2',
                    status === 'pass' && 'ring-success-300',
                    status === 'fail' && 'ring-danger-300',
                    status === 'in-progress' && 'ring-primary-300',
                    status === 'pending' && 'ring-primary-400 border-primary-400 text-primary-500',
                  ],
                  // 비활성
                  disabled && 'cursor-not-allowed opacity-70'
                )}
                aria-label={`${process?.process_name_ko || `공정 ${num}`} - ${status}`}
              >
                {/* 아이콘 */}
                {status === 'pass' && <Check className="w-6 h-6" strokeWidth={3} />}
                {status === 'fail' && <X className="w-6 h-6" strokeWidth={3} />}
                {status === 'in-progress' && <Circle className="w-5 h-5" fill="currentColor" />}
                {status === 'pending' && (
                  <span className="text-sm font-bold">{num}</span>
                )}
              </button>

              {/* 공정 이름 */}
              <span
                className={cn(
                  'mt-2 text-xs font-medium text-center leading-tight',
                  'max-w-[48px] truncate',
                  status === 'pending' ? 'text-neutral-400' : 'text-neutral-700',
                  isSelected && 'text-primary-600 font-semibold'
                )}
              >
                {shortName}
              </span>
            </div>
          );
        })}
      </div>

      {/* 선택된 공정 표시 */}
      {activeProcessNumber && (
        <div
          className={cn(
            'mt-4 py-3 px-4 rounded-xl text-center',
            'transition-all duration-200',
            processStatuses.get(activeProcessNumber) === 'in-progress'
              ? 'bg-primary-50 border border-primary-200'
              : 'bg-neutral-50 border border-neutral-200'
          )}
        >
          <span className="text-sm text-neutral-500">선택된 공정</span>
          <p className="text-lg font-bold text-neutral-800 mt-0.5">
            {activeProcessNumber}.{' '}
            {processes.find((p) => p.process_number === activeProcessNumber)?.process_name_ko ||
              PROCESS_SHORT_NAMES[activeProcessNumber]}
          </p>
          {processStatuses.get(activeProcessNumber) === 'in-progress' && (
            <span className="inline-flex items-center gap-1.5 mt-1 text-xs text-primary-600">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse" />
              진행 중
            </span>
          )}
        </div>
      )}
    </div>
  );
};
