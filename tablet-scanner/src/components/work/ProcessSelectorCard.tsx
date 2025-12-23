/**
 * Process Selector Card
 *
 * 공정 선택 카드 - 8개 공정을 그리드로 표시
 * 태블릿 터치 최적화
 */
import { Factory } from 'lucide-react';
import { Card } from '@/components/ui';
import { cn } from '@/lib/cn';
import type { Process } from '@/types';

interface ProcessSelectorCardProps {
  processes: Process[];
  selectedProcessId: number | null;
  onSelect: (processId: number) => void;
  disabled?: boolean;
  className?: string;
}

export const ProcessSelectorCard: React.FC<ProcessSelectorCardProps> = ({
  processes,
  selectedProcessId,
  onSelect,
  disabled = false,
  className,
}) => {
  // Sort by process_number
  const sortedProcesses = [...processes].sort(
    (a, b) => a.process_number - b.process_number
  );

  return (
    <Card className={cn('p-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
          <Factory className="w-4 h-4 text-primary-600" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-neutral-800">공정 선택</h3>
          <p className="text-xs text-neutral-500">현재 작업 공정을 선택하세요</p>
        </div>
      </div>

      {/* Process Grid - 4x2 */}
      <div className="grid grid-cols-4 gap-2">
        {sortedProcesses.map((process) => {
          const isSelected = selectedProcessId === process.id;

          return (
            <button
              key={process.id}
              onClick={() => !disabled && onSelect(process.id)}
              disabled={disabled}
              className={cn(
                // Base styles
                'relative flex flex-col items-center justify-center',
                'min-h-[72px] p-2 rounded-xl',
                'border-2 transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                // Disabled state
                disabled && 'opacity-50 cursor-not-allowed',
                // Selected state
                isSelected
                  ? 'border-primary-500 bg-primary-50 shadow-md'
                  : 'border-neutral-200 bg-white hover:border-primary-300 hover:bg-primary-50/50',
                // Active state
                !disabled && 'active:scale-95'
              )}
            >
              {/* Process Number Badge */}
              <div
                className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center',
                  'text-sm font-bold mb-1',
                  isSelected
                    ? 'bg-primary-500 text-white'
                    : 'bg-neutral-100 text-neutral-600'
                )}
              >
                {process.process_number}
              </div>

              {/* Process Name */}
              <span
                className={cn(
                  'text-[11px] text-center leading-tight line-clamp-2',
                  isSelected ? 'text-primary-700 font-medium' : 'text-neutral-600'
                )}
              >
                {process.process_name_ko}
              </span>

              {/* Selected Indicator */}
              {isSelected && (
                <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-primary-500 flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Selected Process Info */}
      {selectedProcessId && (
        <div className="mt-3 pt-3 border-t border-neutral-100">
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-500">선택된 공정</span>
            <span className="text-sm font-semibold text-primary-600">
              {sortedProcesses.find(p => p.id === selectedProcessId)?.process_name_ko}
            </span>
          </div>
        </div>
      )}
    </Card>
  );
};
