/**
 * Quick Actions Component
 *
 * 스와이프로 빠른 PASS/FAIL 처리
 * - 좌/우 스와이프 액션
 * - 시각적 피드백
 * - 햅틱 피드백
 */
import { useState, useCallback } from 'react';
import { Check, X, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/cn';
import { useSwipeGesture } from '@/hooks/useSwipeGesture';

type ActionType = 'pass' | 'fail' | null;

interface QuickActionsProps {
  /** WIP 번호 */
  wipNumber: string;
  /** 공정명 */
  processName: string;
  /** PASS 콜백 */
  onPass: () => void;
  /** FAIL 콜백 */
  onFail: () => void;
  /** 비활성화 여부 */
  disabled?: boolean;
  /** 로딩 상태 */
  isLoading?: boolean;
  /** 커스텀 클래스 */
  className?: string;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  wipNumber,
  processName,
  onPass,
  onFail,
  disabled = false,
  isLoading = false,
  className,
}) => {
  const [swipeProgress, setSwipeProgress] = useState(0);
  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null);
  const [pendingAction, setPendingAction] = useState<ActionType>(null);

  // 스와이프 완료 처리
  const handleSwipeComplete = useCallback(
    (action: ActionType) => {
      if (disabled || isLoading || !action) return;

      setPendingAction(action);

      // 햅틱 피드백
      if (navigator.vibrate) {
        navigator.vibrate(action === 'pass' ? [30, 20, 30] : [50, 30, 50, 30, 50]);
      }

      // 0.3초 후 액션 실행
      setTimeout(() => {
        if (action === 'pass') {
          onPass();
        } else {
          onFail();
        }
        setPendingAction(null);
      }, 300);
    },
    [disabled, isLoading, onPass, onFail]
  );

  // 스와이프 제스처
  const { ref } = useSwipeGesture<HTMLDivElement>({
    threshold: 120,
    disabled: disabled || isLoading,
    onSwipeRight: () => handleSwipeComplete('pass'),
    onSwipeLeft: () => handleSwipeComplete('fail'),
    onDrag: (deltaX) => {
      const maxDrag = 150;
      const progress = Math.min(Math.abs(deltaX) / maxDrag, 1);
      setSwipeProgress(progress);
      setSwipeDirection(deltaX > 0 ? 'right' : deltaX < 0 ? 'left' : null);
    },
    onDragEnd: () => {
      setSwipeProgress(0);
      setSwipeDirection(null);
    },
  });

  // 배경 색상 계산
  const getBackgroundStyle = () => {
    if (pendingAction === 'pass') {
      return 'bg-success-500';
    }
    if (pendingAction === 'fail') {
      return 'bg-danger-500';
    }

    if (swipeDirection === 'right') {
      return `rgba(34, 197, 94, ${swipeProgress * 0.3})`;
    }
    if (swipeDirection === 'left') {
      return `rgba(239, 68, 68, ${swipeProgress * 0.3})`;
    }

    return 'transparent';
  };

  return (
    <div className={cn('relative overflow-hidden rounded-2xl', className)}>
      {/* 배경 레이어 */}
      <div
        className="absolute inset-0 transition-colors duration-200"
        style={{ backgroundColor: getBackgroundStyle() }}
      />

      {/* 좌측 힌트 (FAIL) */}
      <div
        className={cn(
          'absolute left-0 top-0 bottom-0 flex items-center justify-center',
          'w-20 text-danger-500',
          'transition-opacity duration-200'
        )}
        style={{ opacity: swipeDirection === 'left' ? swipeProgress : 0.3 }}
      >
        <div className="flex flex-col items-center gap-1">
          <X className="w-6 h-6" />
          <span className="text-xs font-medium">FAIL</span>
        </div>
      </div>

      {/* 우측 힌트 (PASS) */}
      <div
        className={cn(
          'absolute right-0 top-0 bottom-0 flex items-center justify-center',
          'w-20 text-success-500',
          'transition-opacity duration-200'
        )}
        style={{ opacity: swipeDirection === 'right' ? swipeProgress : 0.3 }}
      >
        <div className="flex flex-col items-center gap-1">
          <Check className="w-6 h-6" />
          <span className="text-xs font-medium">PASS</span>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div
        ref={ref}
        className={cn(
          'relative z-10',
          'bg-white border border-neutral-200 rounded-2xl',
          'p-5',
          'touch-pan-y',
          'transition-transform duration-200',
          disabled && 'opacity-50',
          pendingAction && 'scale-95'
        )}
        style={{
          transform: `translateX(${swipeDirection === 'right' ? swipeProgress * 40 : swipeDirection === 'left' ? -swipeProgress * 40 : 0}px)`,
        }}
      >
        {/* 스와이프 가이드 */}
        <div className="flex items-center justify-between mb-3 text-neutral-400">
          <div className="flex items-center gap-1 text-xs">
            <ChevronLeft className="w-4 h-4" />
            <span>FAIL</span>
          </div>
          <div className="flex items-center gap-1 text-xs">
            <span>PASS</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        </div>

        {/* WIP 정보 */}
        <div className="text-center">
          <div className="text-sm text-neutral-500 mb-1">{processName}</div>
          <div className="text-xl font-bold text-neutral-800">{wipNumber}</div>
        </div>

        {/* 로딩 오버레이 */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-2xl">
            <div className="w-8 h-8 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* 성공/실패 오버레이 */}
        {pendingAction && (
          <div
            className={cn(
              'absolute inset-0 flex items-center justify-center rounded-2xl',
              pendingAction === 'pass' ? 'bg-success-500' : 'bg-danger-500'
            )}
          >
            {pendingAction === 'pass' ? (
              <Check className="w-12 h-12 text-white animate-success-check" />
            ) : (
              <X className="w-12 h-12 text-white animate-error-shake" />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * 퀵 액션 버튼 그룹 (스와이프 대신 버튼 사용)
 */
interface QuickActionButtonsProps {
  onPass: () => void;
  onFail: () => void;
  disabled?: boolean;
  isLoading?: boolean;
  className?: string;
}

export const QuickActionButtons: React.FC<QuickActionButtonsProps> = ({
  onPass,
  onFail,
  disabled = false,
  isLoading = false,
  className,
}) => {
  return (
    <div className={cn('flex gap-3', className)}>
      <button
        onClick={onFail}
        disabled={disabled || isLoading}
        className={cn(
          'flex-1 flex items-center justify-center gap-2',
          'py-4 px-6 rounded-xl',
          'bg-danger-50 text-danger-600',
          'border-2 border-danger-200',
          'font-semibold',
          'transition-all duration-200',
          'hover:bg-danger-100 hover:border-danger-300',
          'active:scale-95',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        <X className="w-5 h-5" />
        <span>FAIL</span>
      </button>

      <button
        onClick={onPass}
        disabled={disabled || isLoading}
        className={cn(
          'flex-1 flex items-center justify-center gap-2',
          'py-4 px-6 rounded-xl',
          'bg-success-500 text-white',
          'font-semibold',
          'transition-all duration-200',
          'hover:bg-success-600',
          'active:scale-95',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        <Check className="w-5 h-5" />
        <span>PASS</span>
      </button>
    </div>
  );
};

/**
 * 확인 필요 퀵 액션 (측정값 입력 필요시)
 */
interface QuickActionWithConfirmProps {
  onAction: () => void;
  actionType: 'pass' | 'fail';
  requiresConfirmation?: boolean;
  confirmMessage?: string;
  disabled?: boolean;
  className?: string;
}

export const QuickActionWithConfirm: React.FC<QuickActionWithConfirmProps> = ({
  onAction,
  actionType,
  requiresConfirmation = false,
  confirmMessage = '정말 진행하시겠습니까?',
  disabled = false,
  className,
}) => {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleClick = () => {
    if (requiresConfirmation) {
      setShowConfirm(true);
    } else {
      onAction();
    }
  };

  const handleConfirm = () => {
    setShowConfirm(false);
    onAction();
  };

  const isPass = actionType === 'pass';

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={handleClick}
        disabled={disabled}
        className={cn(
          'w-full flex items-center justify-center gap-2',
          'py-4 px-6 rounded-xl',
          'font-semibold',
          'transition-all duration-200',
          'active:scale-95',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          isPass
            ? 'bg-success-500 text-white hover:bg-success-600'
            : 'bg-danger-500 text-white hover:bg-danger-600'
        )}
      >
        {isPass ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
        <span>{isPass ? 'PASS' : 'FAIL'}</span>
      </button>

      {/* 확인 오버레이 */}
      {showConfirm && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-white rounded-xl shadow-lg border-2 border-neutral-200 p-4">
          <AlertCircle className="w-6 h-6 text-warning-500 mb-2" />
          <p className="text-sm text-neutral-600 text-center mb-3">{confirmMessage}</p>
          <div className="flex gap-2">
            <button
              onClick={() => setShowConfirm(false)}
              className="px-4 py-2 text-sm text-neutral-600 bg-neutral-100 rounded-lg"
            >
              취소
            </button>
            <button
              onClick={handleConfirm}
              className={cn(
                'px-4 py-2 text-sm text-white rounded-lg',
                isPass ? 'bg-success-500' : 'bg-danger-500'
              )}
            >
              확인
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickActions;
