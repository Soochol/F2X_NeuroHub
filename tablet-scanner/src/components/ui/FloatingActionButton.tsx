/**
 * Floating Action Button (FAB) Component
 *
 * 플로팅 액션 버튼
 * - 메인 버튼 + 확장 메뉴
 * - 애니메이션 효과
 * - 위치 커스터마이징
 */
import { useState, useCallback } from 'react';
import { Plus, X } from 'lucide-react';
import { cn } from '@/lib/cn';

type FABPosition = 'bottom-right' | 'bottom-left' | 'bottom-center';
type FABSize = 'sm' | 'md' | 'lg';

interface FABAction {
  id: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  color?: 'primary' | 'success' | 'danger' | 'warning' | 'neutral';
}

interface FloatingActionButtonProps {
  /** 확장 액션들 */
  actions?: FABAction[];
  /** 단일 클릭 핸들러 (actions 없을 때) */
  onClick?: () => void;
  /** 메인 아이콘 (기본: Plus) */
  icon?: React.ReactNode;
  /** 열린 상태 아이콘 (기본: X) */
  openIcon?: React.ReactNode;
  /** 위치 */
  position?: FABPosition;
  /** 크기 */
  size?: FABSize;
  /** 색상 */
  color?: 'primary' | 'success' | 'danger' | 'warning';
  /** 라벨 (접힌 상태에서 표시) */
  label?: string;
  /** 비활성화 */
  disabled?: boolean;
  /** 커스텀 클래스 */
  className?: string;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  actions = [],
  onClick,
  icon,
  openIcon,
  position = 'bottom-right',
  size = 'md',
  color = 'primary',
  label,
  disabled = false,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = useCallback(() => {
    if (actions.length > 0) {
      setIsOpen((prev) => !prev);
    } else if (onClick) {
      onClick();
    }
  }, [actions.length, onClick]);

  const handleActionClick = useCallback((action: FABAction) => {
    action.onClick();
    setIsOpen(false);
  }, []);

  // 위치 클래스
  const positionClasses: Record<FABPosition, string> = {
    'bottom-right': 'right-4 bottom-4',
    'bottom-left': 'left-4 bottom-4',
    'bottom-center': 'left-1/2 -translate-x-1/2 bottom-4',
  };

  // 크기 클래스
  const sizeClasses: Record<FABSize, string> = {
    sm: 'w-12 h-12',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  };

  const iconSizeClasses: Record<FABSize, string> = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-7 h-7',
  };

  // 색상 클래스
  const colorClasses: Record<string, string> = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white shadow-primary-500/30',
    success: 'bg-success-500 hover:bg-success-600 text-white shadow-success-500/30',
    danger: 'bg-danger-500 hover:bg-danger-600 text-white shadow-danger-500/30',
    warning: 'bg-warning-500 hover:bg-warning-600 text-white shadow-warning-500/30',
    neutral: 'bg-neutral-700 hover:bg-neutral-800 text-white shadow-neutral-500/30',
  };

  return (
    <div className={cn('fixed z-50', positionClasses[position], className)}>
      {/* 백드롭 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm -z-10 animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* 확장 액션들 */}
      {actions.length > 0 && isOpen && (
        <div className="absolute bottom-full mb-3 right-0 flex flex-col-reverse gap-2">
          {actions.map((action, index) => (
            <div
              key={action.id}
              className="flex items-center gap-3 justify-end animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* 라벨 */}
              <span
                className={cn(
                  'px-3 py-1.5 rounded-lg',
                  'bg-neutral-800 text-white text-sm font-medium',
                  'shadow-lg',
                  'whitespace-nowrap'
                )}
              >
                {action.label}
              </span>

              {/* 미니 FAB */}
              <button
                onClick={() => handleActionClick(action)}
                className={cn(
                  'w-12 h-12 rounded-full',
                  'flex items-center justify-center',
                  'shadow-lg',
                  'transition-all duration-200',
                  'hover:scale-110',
                  'active:scale-95',
                  colorClasses[action.color || 'neutral']
                )}
              >
                {action.icon}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 메인 FAB */}
      <button
        onClick={toggleOpen}
        disabled={disabled}
        className={cn(
          'rounded-full',
          'flex items-center justify-center gap-2',
          'shadow-xl',
          'transition-all duration-300',
          'hover:scale-105',
          'active:scale-95',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          sizeClasses[size],
          colorClasses[color],
          isOpen && 'rotate-45',
          label && 'px-5 w-auto'
        )}
      >
        {isOpen
          ? openIcon || <X className={iconSizeClasses[size]} />
          : icon || <Plus className={iconSizeClasses[size]} />}
        {label && !isOpen && (
          <span className="font-semibold">{label}</span>
        )}
      </button>
    </div>
  );
};

/**
 * 단순 FAB (확장 메뉴 없음)
 */
interface SimpleFABProps {
  onClick: () => void;
  icon: React.ReactNode;
  label?: string;
  position?: FABPosition;
  color?: 'primary' | 'success' | 'danger' | 'warning';
  disabled?: boolean;
  className?: string;
}

export const SimpleFAB: React.FC<SimpleFABProps> = ({
  onClick,
  icon,
  label,
  position = 'bottom-right',
  color = 'primary',
  disabled = false,
  className,
}) => {
  const positionClasses: Record<FABPosition, string> = {
    'bottom-right': 'right-4 bottom-4',
    'bottom-left': 'left-4 bottom-4',
    'bottom-center': 'left-1/2 -translate-x-1/2 bottom-4',
  };

  const colorClasses: Record<string, string> = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white',
    success: 'bg-success-500 hover:bg-success-600 text-white',
    danger: 'bg-danger-500 hover:bg-danger-600 text-white',
    warning: 'bg-warning-500 hover:bg-warning-600 text-white',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'fixed z-50',
        'flex items-center justify-center gap-2',
        'rounded-full shadow-xl',
        'transition-all duration-200',
        'hover:scale-105 active:scale-95',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        label ? 'h-14 px-6' : 'w-14 h-14',
        positionClasses[position],
        colorClasses[color],
        className
      )}
    >
      {icon}
      {label && <span className="font-semibold">{label}</span>}
    </button>
  );
};

/**
 * 스피드 다이얼 FAB (원형 배열)
 */
interface SpeedDialFABProps {
  actions: FABAction[];
  icon?: React.ReactNode;
  position?: FABPosition;
  color?: 'primary' | 'success' | 'danger' | 'warning';
  disabled?: boolean;
}

export const SpeedDialFAB: React.FC<SpeedDialFABProps> = ({
  actions,
  icon,
  position = 'bottom-right',
  color = 'primary',
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const positionClasses: Record<FABPosition, string> = {
    'bottom-right': 'right-4 bottom-4',
    'bottom-left': 'left-4 bottom-4',
    'bottom-center': 'left-1/2 -translate-x-1/2 bottom-4',
  };

  const colorClasses: Record<string, string> = {
    primary: 'bg-primary-500 hover:bg-primary-600 text-white',
    success: 'bg-success-500 hover:bg-success-600 text-white',
    danger: 'bg-danger-500 hover:bg-danger-600 text-white',
    warning: 'bg-warning-500 hover:bg-warning-600 text-white',
    neutral: 'bg-neutral-600 hover:bg-neutral-700 text-white',
  };

  // 각 액션 버튼의 위치 계산 (반원 형태)
  const getActionPosition = (index: number, total: number) => {
    const angleStep = 180 / (total + 1);
    const angle = (angleStep * (index + 1) - 90) * (Math.PI / 180);
    const radius = 80;

    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
    };
  };

  return (
    <div className={cn('fixed z-50', positionClasses[position])}>
      {/* 백드롭 */}
      {isOpen && (
        <div
          className="fixed inset-0 -z-10"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* 스피드 다이얼 액션들 */}
      {isOpen &&
        actions.map((action, index) => {
          const pos = getActionPosition(index, actions.length);
          return (
            <button
              key={action.id}
              onClick={() => {
                action.onClick();
                setIsOpen(false);
              }}
              className={cn(
                'absolute w-12 h-12 rounded-full',
                'flex items-center justify-center',
                'shadow-lg',
                'transition-all duration-300',
                'hover:scale-110',
                colorClasses[action.color || 'neutral']
              )}
              style={{
                transform: `translate(${-pos.x}px, ${-pos.y}px)`,
                opacity: isOpen ? 1 : 0,
                transitionDelay: `${index * 30}ms`,
              }}
              title={action.label}
            >
              {action.icon}
            </button>
          );
        })}

      {/* 메인 버튼 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'w-14 h-14 rounded-full',
          'flex items-center justify-center',
          'shadow-xl',
          'transition-all duration-300',
          'hover:scale-105 active:scale-95',
          'disabled:opacity-50',
          colorClasses[color],
          isOpen && 'rotate-45'
        )}
      >
        {icon || <Plus className="w-6 h-6" />}
      </button>
    </div>
  );
};

export default FloatingActionButton;
