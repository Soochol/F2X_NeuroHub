/**
 * Progress Ring Component
 *
 * 원형 프로그레스 인디케이터
 * 완료율, 동기화 상태 등을 시각화
 */
import { useEffect, useState, useMemo } from 'react';
import { cn } from '@/lib/cn';

interface ProgressRingProps {
  /** 진행률 (0-100) */
  value: number;
  /** 링 크기 (px) */
  size?: number;
  /** 선 두께 (px) */
  strokeWidth?: number;
  /** 링 색상 */
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral';
  /** 배경 링 표시 */
  showBackground?: boolean;
  /** 중앙 텍스트 표시 */
  showValue?: boolean;
  /** 중앙 커스텀 콘텐츠 */
  children?: React.ReactNode;
  /** 애니메이션 활성화 */
  animated?: boolean;
  /** 추가 클래스 */
  className?: string;
}

const colorClasses = {
  primary: {
    stroke: 'stroke-primary-500',
    text: 'text-primary-600',
  },
  success: {
    stroke: 'stroke-success-500',
    text: 'text-success-600',
  },
  warning: {
    stroke: 'stroke-warning-500',
    text: 'text-warning-600',
  },
  danger: {
    stroke: 'stroke-danger-500',
    text: 'text-danger-600',
  },
  neutral: {
    stroke: 'stroke-neutral-400',
    text: 'text-neutral-600',
  },
};

export const ProgressRing: React.FC<ProgressRingProps> = ({
  value,
  size = 80,
  strokeWidth = 8,
  color = 'primary',
  showBackground = true,
  showValue = true,
  children,
  animated = true,
  className,
}) => {
  const [displayValue, setDisplayValue] = useState(animated ? 0 : value);

  // 반지름 및 둘레 계산
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayValue / 100) * circumference;

  // 애니메이션 효과
  useEffect(() => {
    if (!animated) {
      setDisplayValue(value);
      return;
    }

    const duration = 500; // ms
    const startValue = displayValue;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const newValue = startValue + (value - startValue) * eased;

      setDisplayValue(newValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value, animated]);

  const colorClass = colorClasses[color];

  return (
    <div
      className={cn('relative inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
    >
      <svg
        className="transform -rotate-90"
        width={size}
        height={size}
      >
        {/* Background circle */}
        {showBackground && (
          <circle
            className="stroke-neutral-200"
            fill="none"
            strokeWidth={strokeWidth}
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
        )}

        {/* Progress circle */}
        <circle
          className={cn(
            colorClass.stroke,
            'transition-all duration-300 ease-out'
          )}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex items-center justify-center">
        {children ?? (
          showValue && (
            <span className={cn('font-semibold', colorClass.text)}>
              {Math.round(displayValue)}%
            </span>
          )
        )}
      </div>
    </div>
  );
};

/**
 * 작은 인라인 프로그레스 링
 */
interface MiniProgressRingProps {
  value: number;
  size?: number;
  color?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export const MiniProgressRing: React.FC<MiniProgressRingProps> = ({
  value,
  size = 24,
  color = 'primary',
  className,
}) => {
  return (
    <ProgressRing
      value={value}
      size={size}
      strokeWidth={3}
      color={color}
      showBackground
      showValue={false}
      animated={false}
      className={className}
    />
  );
};

/**
 * 스피너 (로딩 인디케이터)
 */
interface SpinnerRingProps {
  size?: number;
  strokeWidth?: number;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral' | 'white';
  className?: string;
}

const spinnerColorClasses = {
  primary: 'stroke-primary-500',
  success: 'stroke-success-500',
  warning: 'stroke-warning-500',
  danger: 'stroke-danger-500',
  neutral: 'stroke-neutral-400',
  white: 'stroke-white',
};

export const SpinnerRing: React.FC<SpinnerRingProps> = ({
  size = 32,
  strokeWidth = 4,
  color = 'primary',
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  return (
    <div
      className={cn('animate-spin', className)}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size}>
        {/* Background */}
        <circle
          className="stroke-neutral-200"
          fill="none"
          strokeWidth={strokeWidth}
          r={radius}
          cx={size / 2}
          cy={size / 2}
          opacity={0.25}
        />
        {/* Spinner */}
        <circle
          className={spinnerColorClasses[color]}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * 0.75}
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
    </div>
  );
};

/**
 * 완료 체크 링 (성공 애니메이션)
 */
interface CheckRingProps {
  size?: number;
  strokeWidth?: number;
  color?: 'success' | 'primary';
  animated?: boolean;
  className?: string;
}

export const CheckRing: React.FC<CheckRingProps> = ({
  size = 64,
  strokeWidth = 4,
  color = 'success',
  animated = true,
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const checkPath = `M ${size * 0.3} ${size * 0.5} L ${size * 0.45} ${size * 0.65} L ${size * 0.7} ${size * 0.35}`;

  const colorClass = color === 'success' ? 'stroke-success-500' : 'stroke-primary-500';

  return (
    <div
      className={cn('relative', className)}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size}>
        {/* Circle */}
        <circle
          className={cn(
            colorClass,
            animated && 'animate-[progress-fill_0.5s_ease-out_forwards]'
          )}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={animated ? circumference : 0}
          r={radius}
          cx={size / 2}
          cy={size / 2}
          style={
            animated
              ? {
                  '--progress-circumference': circumference,
                  '--progress-offset': 0,
                } as React.CSSProperties
              : undefined
          }
        />
        {/* Checkmark */}
        <path
          className={cn(
            colorClass,
            animated && 'animate-[checkmark-draw_0.3s_ease-out_0.4s_forwards]'
          )}
          fill="none"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={50}
          strokeDashoffset={animated ? 50 : 0}
          d={checkPath}
        />
      </svg>
    </div>
  );
};

/**
 * 프로세스 진행률 링 (Tablet Scanner 전용)
 * 8개 공정 중 완료된 공정 수를 시각화
 */
interface ProcessProgressRingProps {
  completedSteps: number;
  totalSteps?: number;
  size?: number;
  className?: string;
}

export const ProcessProgressRing: React.FC<ProcessProgressRingProps> = ({
  completedSteps,
  totalSteps = 8,
  size = 60,
  className,
}) => {
  const percentage = (completedSteps / totalSteps) * 100;

  // 진행 상태에 따른 색상
  const getColor = useMemo(() => {
    if (percentage === 100) return 'success';
    if (percentage >= 75) return 'primary';
    if (percentage >= 50) return 'warning';
    return 'neutral';
  }, [percentage]);

  return (
    <ProgressRing
      value={percentage}
      size={size}
      strokeWidth={6}
      color={getColor}
      showValue={false}
      className={className}
    >
      <div className="text-center">
        <div className="text-lg font-bold text-neutral-800">
          {completedSteps}
        </div>
        <div className="text-xs text-neutral-500">/{totalSteps}</div>
      </div>
    </ProgressRing>
  );
};

export default ProgressRing;
