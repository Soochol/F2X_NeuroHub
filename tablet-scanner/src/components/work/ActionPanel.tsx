/**
 * Action Panel
 *
 * 착공/완공 메인 액션 버튼 패널
 * 태블릿 터치 최적화 - 큰 터치 타겟
 */
import { Play, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

interface ActionPanelProps {
  onStart: () => void;
  onCompletePass: () => void;
  onCompleteFail: () => void;
  disabled?: boolean;
  isLoading?: boolean;
  selectedProcessName?: string;
  currentWipId?: string | null;
  className?: string;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({
  onStart,
  onCompletePass,
  onCompleteFail,
  disabled = false,
  isLoading = false,
  selectedProcessName,
  currentWipId,
  className,
}) => {
  const isDisabled = disabled || isLoading;
  const canComplete = !!currentWipId;

  return (
    <div className={cn('space-y-3', className)}>
      {/* Current WIP Indicator */}
      {currentWipId && (
        <div className="p-3 bg-success-50 rounded-xl border border-success-200">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-success-500 animate-pulse" />
            <span className="text-xs text-success-600 font-medium">작업 중</span>
          </div>
          <p className="text-base font-mono font-semibold text-success-700 mt-1 truncate">
            {currentWipId}
          </p>
        </div>
      )}

      {/* Selected Process Indicator */}
      {selectedProcessName && !currentWipId && (
        <div className="text-center py-2 px-4 bg-primary-50 rounded-lg border border-primary-200">
          <span className="text-sm text-primary-700">
            <span className="font-medium">{selectedProcessName}</span> 공정 선택됨
          </span>
        </div>
      )}

      {/* Start Button - Large */}
      <button
        onClick={onStart}
        disabled={isDisabled}
        className={cn(
          // Base
          'w-full flex items-center justify-center gap-4',
          'py-5 px-6 rounded-2xl',
          'font-bold text-xl',
          'transition-all duration-200',
          'shadow-lg',
          // States
          isDisabled
            ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
            : [
                'bg-gradient-to-r from-primary-500 to-primary-600',
                'text-white',
                'hover:from-primary-600 hover:to-primary-700',
                'active:scale-[0.98] active:shadow-md',
              ]
        )}
      >
        {isLoading ? (
          <Loader2 className="w-7 h-7 animate-spin" />
        ) : (
          <Play className="w-7 h-7" fill="currentColor" />
        )}
        <span>착공</span>
      </button>

      {/* Complete Buttons Row */}
      <div className="grid grid-cols-2 gap-3">
        {/* Pass Button */}
        <button
          onClick={onCompletePass}
          disabled={isDisabled || !canComplete}
          className={cn(
            // Base
            'flex items-center justify-center gap-2',
            'py-4 px-4 rounded-xl',
            'font-bold text-lg',
            'transition-all duration-200',
            'shadow-lg',
            // States
            isDisabled || !canComplete
              ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
              : [
                  'bg-gradient-to-r from-success-500 to-success-600',
                  'text-white',
                  'hover:from-success-600 hover:to-success-700',
                  'active:scale-[0.98] active:shadow-md',
                ]
          )}
        >
          <CheckCircle className="w-6 h-6" />
          <span>완공</span>
          <span className={cn(
            'text-sm font-normal',
            isDisabled || !canComplete ? 'text-neutral-300' : 'text-success-200'
          )}>(합격)</span>
        </button>

        {/* Fail Button */}
        <button
          onClick={onCompleteFail}
          disabled={isDisabled || !canComplete}
          className={cn(
            // Base
            'flex items-center justify-center gap-2',
            'py-4 px-4 rounded-xl',
            'font-bold text-lg',
            'transition-all duration-200',
            'shadow-lg',
            // States
            isDisabled || !canComplete
              ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed shadow-none'
              : [
                  'bg-gradient-to-r from-danger-500 to-danger-600',
                  'text-white',
                  'hover:from-danger-600 hover:to-danger-700',
                  'active:scale-[0.98] active:shadow-md',
                ]
          )}
        >
          <XCircle className="w-6 h-6" />
          <span>완공</span>
          <span className={cn(
            'text-sm font-normal',
            isDisabled || !canComplete ? 'text-neutral-300' : 'text-danger-200'
          )}>(불량)</span>
        </button>
      </div>

      {/* Helper Text */}
      {!selectedProcessName && (
        <p className="text-center text-sm text-neutral-500">
          먼저 위에서 공정을 선택해주세요
        </p>
      )}
      {selectedProcessName && !canComplete && (
        <p className="text-center text-sm text-neutral-500">
          착공 후 완공 버튼이 활성화됩니다
        </p>
      )}
    </div>
  );
};
