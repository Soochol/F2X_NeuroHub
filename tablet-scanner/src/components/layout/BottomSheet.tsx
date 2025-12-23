/**
 * Bottom Sheet Component
 *
 * 스와이프로 열고 닫을 수 있는 바텀 시트
 * - 드래그 핸들
 * - 스냅 포인트
 * - 백드롭 클릭으로 닫기
 * - 키보드 접근성
 */
import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';
import { useSwipeGesture } from '@/hooks/useSwipeGesture';

interface BottomSheetProps {
  /** 시트 열림 상태 */
  isOpen: boolean;
  /** 닫기 콜백 */
  onClose: () => void;
  /** 시트 제목 */
  title?: string;
  /** 시트 내용 */
  children: React.ReactNode;
  /** 시트 높이 (기본값: auto) */
  height?: 'auto' | 'half' | 'full';
  /** 백드롭 클릭으로 닫기 허용 */
  closeOnBackdrop?: boolean;
  /** 스와이프 다운으로 닫기 허용 */
  closeOnSwipeDown?: boolean;
  /** 드래그 핸들 표시 */
  showHandle?: boolean;
  /** 닫기 버튼 표시 */
  showCloseButton?: boolean;
  /** 커스텀 클래스 */
  className?: string;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
  isOpen,
  onClose,
  title,
  children,
  height = 'auto',
  closeOnBackdrop = true,
  closeOnSwipeDown = true,
  showHandle = true,
  showCloseButton = true,
  className,
}) => {
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const sheetRef = useRef<HTMLDivElement>(null);

  // 스와이프 제스처
  const { ref: swipeRef } = useSwipeGesture<HTMLDivElement>({
    threshold: 50,
    onSwipeDown: closeOnSwipeDown ? onClose : undefined,
    onDrag: (_, deltaY) => {
      if (deltaY > 0) {
        setDragOffset(deltaY);
        setIsDragging(true);
      }
    },
    onDragEnd: () => {
      if (dragOffset > 100) {
        onClose();
      }
      setDragOffset(0);
      setIsDragging(false);
    },
  });

  // ESC 키로 닫기
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // 열릴 때 스크롤 방지
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // 높이 클래스
  const heightClasses = {
    auto: 'max-h-[80vh]',
    half: 'h-[50vh]',
    full: 'h-[90vh]',
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* 백드롭 */}
      <div
        className={cn(
          'absolute inset-0 bg-black/50 backdrop-blur-sm',
          'animate-fade-in'
        )}
        onClick={closeOnBackdrop ? onClose : undefined}
      />

      {/* 시트 */}
      <div
        ref={sheetRef}
        className={cn(
          'absolute bottom-0 left-0 right-0',
          'bg-white rounded-t-3xl',
          'shadow-2xl',
          'animate-slide-up',
          heightClasses[height],
          className
        )}
        style={{
          transform: isDragging ? `translateY(${dragOffset}px)` : undefined,
          transition: isDragging ? 'none' : 'transform 0.3s ease-out',
        }}
      >
        {/* 드래그 핸들 영역 */}
        <div ref={swipeRef} className="touch-none">
          {/* 핸들 바 */}
          {showHandle && (
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-12 h-1.5 bg-neutral-300 rounded-full" />
            </div>
          )}

          {/* 헤더 */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between px-5 py-3 border-b border-neutral-100">
              {title && (
                <h3 className="text-lg font-semibold text-neutral-800">
                  {title}
                </h3>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className={cn(
                    'p-2 -mr-2 rounded-full',
                    'text-neutral-500 hover:text-neutral-700',
                    'hover:bg-neutral-100',
                    'transition-colors'
                  )}
                  aria-label="닫기"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* 콘텐츠 */}
        <div className="overflow-y-auto px-5 py-4" style={{ maxHeight: 'calc(100% - 60px)' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

/**
 * 바텀 시트 트리거 버튼
 */
interface BottomSheetTriggerProps {
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
}

export const BottomSheetTrigger: React.FC<BottomSheetTriggerProps> = ({
  onClick,
  children,
  className,
}) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center justify-center',
        'transition-all duration-200',
        'active:scale-95',
        className
      )}
    >
      {children}
    </button>
  );
};

/**
 * 바텀 시트 액션 버튼
 */
interface BottomSheetActionProps {
  onClick: () => void;
  icon?: React.ReactNode;
  label: string;
  description?: string;
  variant?: 'default' | 'primary' | 'danger';
  disabled?: boolean;
}

export const BottomSheetAction: React.FC<BottomSheetActionProps> = ({
  onClick,
  icon,
  label,
  description,
  variant = 'default',
  disabled = false,
}) => {
  const variantClasses = {
    default: 'text-neutral-700 hover:bg-neutral-100',
    primary: 'text-primary-600 hover:bg-primary-50',
    danger: 'text-danger-600 hover:bg-danger-50',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'w-full flex items-center gap-4 p-4 rounded-xl',
        'transition-colors duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variantClasses[variant]
      )}
    >
      {icon && (
        <div className="w-10 h-10 flex items-center justify-center rounded-full bg-neutral-100">
          {icon}
        </div>
      )}
      <div className="flex-1 text-left">
        <div className="font-medium">{label}</div>
        {description && (
          <div className="text-sm text-neutral-500">{description}</div>
        )}
      </div>
    </button>
  );
};

export default BottomSheet;
