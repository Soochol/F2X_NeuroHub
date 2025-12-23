/**
 * Process Selector Component
 *
 * Allows selecting manufacturing process with visual feedback
 * Modern styling with Tailwind CSS
 */
import { Check, Loader2, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { Process, NextProcessRecommendation } from '@/types';

interface ProcessSelectorProps {
  processes: Process[];
  selectedProcessId: number | null;
  recommendation?: NextProcessRecommendation | null;
  completedProcesses?: number[];
  inProgressProcess?: number | null;
  onSelect: (processId: number | null) => void;
  disabled?: boolean;
}

type ProcessStatus = 'completed' | 'in-progress' | 'recommended' | 'pending';

export const ProcessSelector: React.FC<ProcessSelectorProps> = ({
  processes,
  selectedProcessId,
  recommendation = null,
  completedProcesses = [],
  inProgressProcess = null,
  onSelect,
  disabled = false,
}) => {
  // Sort processes by process_number
  const sortedProcesses = [...processes].sort(
    (a, b) => a.process_number - b.process_number
  );

  const getProcessStatus = (processNumber: number): ProcessStatus => {
    if (inProgressProcess === processNumber) return 'in-progress';
    if (completedProcesses.includes(processNumber)) return 'completed';
    if (recommendation?.processNumber === processNumber) return 'recommended';
    return 'pending';
  };

  const getStatusStyles = (status: ProcessStatus, isSelected: boolean) => {
    if (isSelected) {
      return 'border-primary-500 bg-primary-50 text-primary-600';
    }

    switch (status) {
      case 'completed':
        return 'border-success-300 bg-success-50 text-success-600';
      case 'in-progress':
        return 'border-warning-300 bg-warning-50 text-warning-600';
      case 'recommended':
        return 'border-primary-200 bg-primary-50/50 text-primary-500';
      default:
        return 'border-neutral-200 bg-neutral-50 text-neutral-400';
    }
  };

  return (
    <div className="w-full">
      {/* Recommendation banner */}
      {recommendation && (
        <div className="mb-3 p-3 bg-primary-50 rounded-lg border border-primary-200">
          <div className="flex items-center gap-2 text-xs text-neutral-500 mb-1">
            <Lightbulb className="w-3.5 h-3.5" />
            추천 공정
          </div>
          <div className="text-base font-semibold text-primary-600">
            {recommendation.processNumber}. {recommendation.processName}
          </div>
          <div className="text-xs text-neutral-600 mt-1">
            {recommendation.reason}
          </div>
        </div>
      )}

      {/* Process grid */}
      <div className="grid grid-cols-4 gap-2">
        {sortedProcesses.map((process) => {
          const status = getProcessStatus(process.process_number);
          const isSelected = selectedProcessId === process.id;

          return (
            <button
              key={process.id}
              onClick={() => !disabled && onSelect(process.id)}
              disabled={disabled}
              className={cn(
                'flex flex-col items-center gap-1',
                'p-3 rounded-lg border-2',
                'transition-all duration-150',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1',
                disabled && 'opacity-50 cursor-not-allowed',
                !disabled && 'cursor-pointer hover:shadow-sm',
                getStatusStyles(status, isSelected)
              )}
            >
              {/* Process number with status icon */}
              <div className="relative">
                <span className="text-lg font-bold">
                  {process.process_number}
                </span>
                {status === 'completed' && (
                  <Check className="absolute -top-1 -right-3 w-3.5 h-3.5 text-success-500" />
                )}
                {status === 'in-progress' && (
                  <Loader2 className="absolute -top-1 -right-3 w-3.5 h-3.5 text-warning-500 animate-spin" />
                )}
              </div>

              {/* Process name */}
              <span
                className="text-[10px] text-center leading-tight line-clamp-2"
                title={process.process_name_ko}
              >
                {process.process_name_ko}
              </span>

              {/* Status label */}
              {status === 'completed' && (
                <span className="text-[9px] font-medium text-success-500">완료</span>
              )}
              {status === 'in-progress' && (
                <span className="text-[9px] font-medium text-warning-500">진행중</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-3 text-[11px] text-neutral-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-sm bg-success-500" />
          완료
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-sm bg-warning-500" />
          진행중
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-sm bg-primary-500" />
          추천/선택
        </span>
      </div>
    </div>
  );
};
