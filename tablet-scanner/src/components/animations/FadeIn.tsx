/**
 * FadeIn Animation Wrapper
 *
 * 자식 요소에 페이드 인 애니메이션 적용
 */
import { useEffect, useState, useRef } from 'react';
import { cn } from '@/lib/cn';

interface FadeInProps {
  children: React.ReactNode;
  /** 애니메이션 지연 시간 (ms) */
  delay?: number;
  /** 애니메이션 지속 시간 (ms) */
  duration?: number;
  /** 뷰포트 진입 시 애니메이션 시작 */
  whenVisible?: boolean;
  /** 초기 상태 (마운트 즉시 애니메이션 시작 여부) */
  show?: boolean;
  /** 추가 클래스 */
  className?: string;
  /** 애니메이션 완료 콜백 */
  onComplete?: () => void;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  duration = 300,
  whenVisible = false,
  show = true,
  className,
  onComplete,
}) => {
  const [isVisible, setIsVisible] = useState(!whenVisible && show);
  const [hasAnimated, setHasAnimated] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Intersection Observer for whenVisible
  useEffect(() => {
    if (!whenVisible || hasAnimated) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            setIsVisible(true);
            setHasAnimated(true);
          }, delay);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [whenVisible, delay, hasAnimated]);

  // show prop 변경 시 애니메이션
  useEffect(() => {
    if (!whenVisible) {
      if (show) {
        setTimeout(() => setIsVisible(true), delay);
      } else {
        setIsVisible(false);
      }
    }
  }, [show, delay, whenVisible]);

  // 애니메이션 완료 핸들러
  const handleAnimationEnd = () => {
    if (isVisible) {
      onComplete?.();
    }
  };

  return (
    <div
      ref={ref}
      className={cn(
        'transition-opacity',
        isVisible ? 'opacity-100' : 'opacity-0',
        className
      )}
      style={{
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: 'ease-out',
      }}
      onTransitionEnd={handleAnimationEnd}
    >
      {children}
    </div>
  );
};

/**
 * FadeInScale - 페이드 + 스케일 애니메이션
 */
interface FadeInScaleProps extends FadeInProps {
  /** 시작 스케일 (0-1) */
  initialScale?: number;
}

export const FadeInScale: React.FC<FadeInScaleProps> = ({
  children,
  delay = 0,
  duration = 300,
  initialScale = 0.95,
  whenVisible = false,
  show = true,
  className,
  onComplete,
}) => {
  const [isVisible, setIsVisible] = useState(!whenVisible && show);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (whenVisible) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setTimeout(() => setIsVisible(true), delay);
          }
        },
        { threshold: 0.1 }
      );

      if (ref.current) {
        observer.observe(ref.current);
      }

      return () => observer.disconnect();
    } else {
      if (show) {
        setTimeout(() => setIsVisible(true), delay);
      } else {
        setIsVisible(false);
      }
    }
  }, [show, delay, whenVisible]);

  return (
    <div
      ref={ref}
      className={cn(
        'transition-all',
        className
      )}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'scale(1)' : `scale(${initialScale})`,
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: 'ease-out',
      }}
      onTransitionEnd={() => isVisible && onComplete?.()}
    >
      {children}
    </div>
  );
};

/**
 * Stagger Container - 자식 요소들에 순차적 페이드 인
 */
interface StaggerContainerProps {
  children: React.ReactNode;
  /** 각 자식 간 지연 시간 (ms) */
  staggerDelay?: number;
  /** 시작 지연 시간 (ms) */
  initialDelay?: number;
  className?: string;
}

export const StaggerContainer: React.FC<StaggerContainerProps> = ({
  children,
  staggerDelay = 50,
  initialDelay = 0,
  className,
}) => {
  return (
    <div className={className}>
      {Array.isArray(children)
        ? children.map((child, index) => (
            <FadeIn
              key={index}
              delay={initialDelay + index * staggerDelay}
              duration={200}
            >
              {child}
            </FadeIn>
          ))
        : children}
    </div>
  );
};

export default FadeIn;
