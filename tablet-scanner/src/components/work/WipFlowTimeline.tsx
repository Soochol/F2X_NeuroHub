/**
 * WIP Flow Timeline Component
 *
 * 동적 공정 진행 상황을 시각화하는 타임라인
 * API에서 가져온 공정 목록 사용
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

// 공정 코드에서 짧은 이름 추출 (예: SENSOR_TEST -> Sensor, FIRMWARE_UPLOAD -> Firmware)
const getShortName = (process: Process): string => {
  const code = process.process_code || process.process_name_en || '';
  // 첫 번째 단어만 추출하고 첫 글자 대문자로
  const firstWord = code.split('_')[0];
  return firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
};

export const WipFlowTimeline: React.FC<WipFlowTimelineProps> = ({
  trace,
  processes,
  selectedProcessNumber,
  onProcessSelect,
  disabled = false,
  className,
}) => {
  // 공정 목록을 process_number로 정렬
  const sortedProcesses = useMemo(() => {
    return [...processes].sort((a, b) => a.process_number - b.process_number);
  }, [processes]);

  // 공정별 상태 계산
  const processStatuses = useMemo(() => {
    const statuses = new Map<number, ProcessStatus>();

    // 기본값: 모든 공정을 pending으로 설정
    sortedProcesses.forEach((p) => {
      statuses.set(p.process_number, 'pending');
    });

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
  }, [trace, sortedProcesses]);

  // 다음 진행할 공정 번호 계산
  const nextProcessNumber = useMemo(() => {
    // 진행 중인 공정이 있으면 해당 공정
    for (const process of sortedProcesses) {
      if (processStatuses.get(process.process_number) === 'in-progress') {
        return process.process_number;
      }
    }
    // 아니면 첫 번째 pending 공정
    for (const process of sortedProcesses) {
      if (processStatuses.get(process.process_number) === 'pending') {
        return process.process_number;
      }
    }
    return null;
  }, [processStatuses, sortedProcesses]);

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
      {/* 타임라인 컨테이너 - 모바일에서 가로 스크롤 */}
      <div className="relative flex items-center justify-between px-2 pt-6 pb-2 overflow-x-auto scrollbar-hide min-w-0 gap-1 sm:gap-0">
        {/* 연결선 (배경) */}
        <div className="absolute top-12 left-6 right-6 h-1.5 bg-sub rounded-full" />

        {/* 진행된 연결선 */}
        <div
          className="absolute top-12 left-6 h-1.5 bg-success-500 rounded-full transition-all duration-700 ease-in-out shadow-[0_0_15px_rgba(16,185,129,0.4)]"
          style={{
            width: sortedProcesses.length > 1
              ? `${Math.max(0, (Array.from(processStatuses.values()).filter((s) => s === 'pass').length - 1) / (sortedProcesses.length - 1)) * 100}%`
              : '0%',
          }}
        />

        {/* 공정 노드들 - API에서 가져온 공정 목록 사용 */}
        {sortedProcesses.map((process) => {
          const num = process.process_number;
          const status = processStatuses.get(num) || 'pending';
          const isSelected = activeProcessNumber === num;
          const shortName = getShortName(process);

          return (
            <div key={num} className="relative z-10 flex flex-col items-center shrink-0">
              {/* 공정 배지 */}
              <button
                type="button"
                onClick={() => handleProcessClick(num)}
                disabled={disabled}
                className={cn(
                  // 기본 스타일 - 모바일에서 더 작게
                  'w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center',
                  'transition-all duration-300 border-2',
                  // 터치 피드백
                  !disabled && 'active:scale-90',
                  // 상태별 스타일
                  status === 'pass' && [
                    'bg-success-500 border-success-400 text-dynamic shadow-[0_0_20px_rgba(16,185,129,0.3)]',
                  ],
                  status === 'fail' && [
                    'bg-danger-500 border-danger-400 text-dynamic shadow-[0_0_20px_rgba(239,68,68,0.3)]',
                  ],
                  status === 'in-progress' && [
                    'bg-primary-500 border-primary-400 text-dynamic animate-pulse shadow-[0_0_30px_rgba(30,58,95,0.5)]',
                  ],
                  status === 'pending' && [
                    isSelected ? 'bg-primary-500/10 border-primary-500 text-dynamic' : 'bg-sub border-main text-muted',
                  ],
                  // 선택됨 표시
                  isSelected && [
                    'ring-offset-transparent ring-4 ring-primary-500/30 scale-110',
                  ],
                  // 비활성
                  disabled && 'cursor-not-allowed'
                )}
                aria-label={`${process?.process_name_en || `Process ${num}`} - ${status}`}
              >
                {/* 아이콘 */}
                {status === 'pass' && <Check className="w-6 h-6 lg:w-7 lg:h-7" strokeWidth={4} />}
                {status === 'fail' && <X className="w-6 h-6 lg:w-7 lg:h-7" strokeWidth={4} />}
                {status === 'in-progress' && <Circle className="w-6 h-6 lg:w-7 lg:h-7" fill="currentColor" />}
                {status === 'pending' && (
                  <span className={cn('text-lg font-black', isSelected ? 'text-dynamic' : 'text-muted')}>
                    {num}
                  </span>
                )}
              </button>

              {/* 공정 이름 */}
              <span
                className={cn(
                  'mt-3 text-[10px] sm:text-xs lg:text-sm font-black text-center leading-tight uppercase tracking-tighter',
                  'max-w-[60px] sm:max-w-[80px] lg:max-w-[100px] transition-all duration-300',
                  isSelected || status === 'in-progress'
                    ? 'text-primary-400 opacity-100 scale-110 font-black'
                    : status === 'pending'
                      ? 'text-muted opacity-80'
                      : 'text-dim opacity-90'
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
            'mt-8 py-4 px-6 rounded-2xl text-center',
            'bg-sub border border-main shadow-inner'
          )}
        >
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted">Selected Process</span>
          <p className="text-xl font-black text-primary-400 mt-1 tracking-tight">
            <span className="opacity-70 mr-3">{activeProcessNumber}</span>
            {(() => {
              const activeProcess = sortedProcesses.find((p) => p.process_number === activeProcessNumber);
              return activeProcess?.process_name_en || activeProcess?.process_code || `Process ${activeProcessNumber}`;
            })()}
          </p>
          {processStatuses.get(activeProcessNumber) === 'in-progress' && (
            <div className="inline-flex items-center gap-2 mt-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-ping" />
              <span className="text-[10px] font-bold text-primary-400 uppercase tracking-wider">In Progress</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
