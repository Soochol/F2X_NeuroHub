/**
 * WIP Timeline Component
 *
 * Responsive timeline showing process history
 * - Landscape: Horizontal timeline
 * - Portrait: Vertical timeline
 */
import { Check, Loader2, Circle } from 'lucide-react';
import { useIsLandscape } from '@/hooks/useMediaQuery';
import { Card } from '@/components/ui';
import { cn } from '@/lib/cn';
import type { Process, ProcessHistoryItem } from '@/types';

export interface WipTimelineProps {
  processes: Process[];
  processHistory: ProcessHistoryItem[];
  completedProcesses: number[];
  inProgressProcess: number | null;
  className?: string;
}

type StepStatus = 'completed' | 'in-progress' | 'pending';

export const WipTimeline: React.FC<WipTimelineProps> = ({
  processes,
  processHistory,
  completedProcesses,
  inProgressProcess,
  className,
}) => {
  const isLandscape = useIsLandscape();

  const sortedProcesses = [...processes].sort(
    (a, b) => a.process_number - b.process_number
  );

  const getStepStatus = (processNumber: number): StepStatus => {
    if (completedProcesses.includes(processNumber)) return 'completed';
    if (inProgressProcess === processNumber) return 'in-progress';
    return 'pending';
  };

  const getHistoryData = (processNumber: number): ProcessHistoryItem | undefined => {
    return processHistory.find((h) => h.process_number === processNumber);
  };

  const formatTime = (dateString: string | null): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  };

  if (isLandscape) {
    return (
      <HorizontalTimeline
        processes={sortedProcesses}
        getStepStatus={getStepStatus}
        getHistoryData={getHistoryData}
        formatTime={formatTime}
        className={className}
      />
    );
  }

  return (
    <VerticalTimeline
      processes={sortedProcesses}
      getStepStatus={getStepStatus}
      getHistoryData={getHistoryData}
      formatTime={formatTime}
      className={className}
    />
  );
};

// Step icon component
const StepIcon: React.FC<{ status: StepStatus }> = ({ status }) => {
  const baseClasses = cn(
    'w-8 h-8 rounded-full flex items-center justify-center',
    'border-2 transition-colors'
  );

  if (status === 'completed') {
    return (
      <div className={cn(baseClasses, 'bg-success-500 border-success-500')}>
        <Check className="w-4 h-4 text-white" />
      </div>
    );
  }

  if (status === 'in-progress') {
    return (
      <div className={cn(baseClasses, 'bg-primary-500 border-primary-500')}>
        <Loader2 className="w-4 h-4 text-white animate-spin" />
      </div>
    );
  }

  return (
    <div className={cn(baseClasses, 'bg-neutral-100 border-neutral-300')}>
      <Circle className="w-3 h-3 text-neutral-400" />
    </div>
  );
};

// Horizontal Timeline (Landscape)
interface TimelineInternalProps {
  processes: Process[];
  getStepStatus: (num: number) => StepStatus;
  getHistoryData: (num: number) => ProcessHistoryItem | undefined;
  formatTime: (date: string | null) => string;
  className?: string;
}

const HorizontalTimeline: React.FC<TimelineInternalProps> = ({
  processes,
  getStepStatus,
  getHistoryData,
  formatTime,
  className,
}) => {
  return (
    <Card className={cn('overflow-x-auto', className)}>
      <div className="min-w-[600px] px-2">
        {/* Timeline row */}
        <div className="flex items-center">
          {processes.map((process, index) => {
            const status = getStepStatus(process.process_number);
            const historyData = getHistoryData(process.process_number);
            const isLast = index === processes.length - 1;

            return (
              <div key={process.id} className="flex items-center flex-1">
                {/* Step */}
                <div className="flex flex-col items-center">
                  <StepIcon status={status} />

                  {/* Process info below */}
                  <div className="mt-2 text-center">
                    <div
                      className={cn(
                        'text-sm font-semibold',
                        status === 'completed' && 'text-success-600',
                        status === 'in-progress' && 'text-primary-600',
                        status === 'pending' && 'text-neutral-400'
                      )}
                    >
                      {process.process_number}
                    </div>
                    <div
                      className={cn(
                        'text-xs mt-0.5 max-w-[80px] truncate',
                        status === 'pending' ? 'text-neutral-400' : 'text-neutral-600'
                      )}
                      title={process.process_name_ko}
                    >
                      {process.process_name_ko}
                    </div>
                    {historyData && status === 'completed' && (
                      <div className="text-[10px] text-neutral-400 mt-0.5">
                        {formatTime(historyData.complete_time)}
                      </div>
                    )}
                    {status === 'in-progress' && (
                      <div className="text-[10px] text-primary-500 mt-0.5">
                        진행중
                      </div>
                    )}
                  </div>
                </div>

                {/* Connector line */}
                {!isLast && (
                  <div
                    className={cn(
                      'flex-1 h-0.5 mx-1',
                      status === 'completed' ? 'bg-success-500' : 'bg-neutral-200'
                    )}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

// Vertical Timeline (Portrait)
const VerticalTimeline: React.FC<TimelineInternalProps> = ({
  processes,
  getStepStatus,
  getHistoryData,
  formatTime,
  className,
}) => {
  return (
    <Card className={className}>
      <div className="relative">
        {/* Vertical line */}
        <div
          className="absolute left-4 top-4 bottom-4 w-0.5 bg-neutral-200"
          style={{ transform: 'translateX(-50%)' }}
        />

        {/* Steps */}
        <div className="space-y-4">
          {processes.map((process) => {
            const status = getStepStatus(process.process_number);
            const historyData = getHistoryData(process.process_number);

            return (
              <div
                key={process.id}
                className={cn(
                  'relative flex items-start gap-3 pl-0',
                  status === 'in-progress' && 'bg-primary-50 -mx-4 px-4 py-2 rounded-lg'
                )}
              >
                {/* Icon */}
                <div className="relative z-10 flex-shrink-0">
                  <StepIcon status={status} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pt-1">
                  <div className="flex items-baseline gap-2">
                    <span
                      className={cn(
                        'text-sm font-semibold',
                        status === 'completed' && 'text-success-600',
                        status === 'in-progress' && 'text-primary-600',
                        status === 'pending' && 'text-neutral-400'
                      )}
                    >
                      {process.process_number}.
                    </span>
                    <span
                      className={cn(
                        'text-sm font-medium truncate',
                        status === 'pending' ? 'text-neutral-400' : 'text-neutral-700'
                      )}
                    >
                      {process.process_name_ko}
                    </span>
                  </div>

                  {/* Status info */}
                  <div className="mt-0.5 text-xs text-neutral-500">
                    {status === 'completed' && historyData && (
                      <span>
                        완료 {formatTime(historyData.complete_time)}
                        {historyData.result && (
                          <span
                            className={cn(
                              'ml-2 font-medium',
                              historyData.result === 'PASS'
                                ? 'text-success-500'
                                : 'text-danger-500'
                            )}
                          >
                            {historyData.result}
                          </span>
                        )}
                      </span>
                    )}
                    {status === 'in-progress' && (
                      <span className="text-primary-500 font-medium">진행중...</span>
                    )}
                    {status === 'pending' && <span>대기</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};
