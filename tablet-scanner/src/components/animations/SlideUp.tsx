/**
 * SlideUp Animation Wrapper
 *
 * 아래에서 위로 슬라이드하며 등장하는 애니메이션
 */
import { useEffect, useState, useRef } from 'react';
import { cn } from '@/lib/cn';

type SlideDirection = 'up' | 'down' | 'left' | 'right';

interface SlideProps {
  children: React.ReactNode;
  /** 슬라이드 방향 */
  direction?: SlideDirection;
  /** 애니메이션 지연 시간 (ms) */
  delay?: number;
  /** 애니메이션 지속 시간 (ms) */
  duration?: number;
  /** 이동 거리 (px) */
  distance?: number;
  /** 뷰포트 진입 시 애니메이션 시작 */
  whenVisible?: boolean;
  /** 초기 상태 */
  show?: boolean;
  /** 추가 클래스 */
  className?: string;
  /** 애니메이션 완료 콜백 */
  onComplete?: () => void;
}

const getTranslate = (direction: SlideDirection, distance: number, isVisible: boolean) => {
  if (isVisible) return 'translate(0, 0)';

  switch (direction) {
    case 'up':
      return `translate(0, ${distance}px)`;
    case 'down':
      return `translate(0, -${distance}px)`;
    case 'left':
      return `translate(${distance}px, 0)`;
    case 'right':
      return `translate(-${distance}px, 0)`;
    default:
      return `translate(0, ${distance}px)`;
  }
};

export const Slide: React.FC<SlideProps> = ({
  children,
  direction = 'up',
  delay = 0,
  duration = 300,
  distance = 20,
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

  return (
    <div
      ref={ref}
      className={cn('transition-all', className)}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: getTranslate(direction, distance, isVisible),
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: 'cubic-bezier(0.4, 0, 0.2, 1)',
      }}
      onTransitionEnd={() => isVisible && onComplete?.()}
    >
      {children}
    </div>
  );
};

// Convenience exports
export const SlideUp: React.FC<Omit<SlideProps, 'direction'>> = (props) => (
  <Slide {...props} direction="up" />
);

export const SlideDown: React.FC<Omit<SlideProps, 'direction'>> = (props) => (
  <Slide {...props} direction="down" />
);

export const SlideLeft: React.FC<Omit<SlideProps, 'direction'>> = (props) => (
  <Slide {...props} direction="left" />
);

export const SlideRight: React.FC<Omit<SlideProps, 'direction'>> = (props) => (
  <Slide {...props} direction="right" />
);

/**
 * SlideUpStagger - 자식 요소들에 순차적 슬라이드 업
 */
interface SlideUpStaggerProps {
  children: React.ReactNode;
  /** 각 자식 간 지연 시간 (ms) */
  staggerDelay?: number;
  /** 시작 지연 시간 (ms) */
  initialDelay?: number;
  /** 애니메이션 지속 시간 (ms) */
  duration?: number;
  className?: string;
}

export const SlideUpStagger: React.FC<SlideUpStaggerProps> = ({
  children,
  staggerDelay = 50,
  initialDelay = 0,
  duration = 300,
  className,
}) => {
  return (
    <div className={className}>
      {Array.isArray(children)
        ? children.map((child, index) => (
            <SlideUp
              key={index}
              delay={initialDelay + index * staggerDelay}
              duration={duration}
            >
              {child}
            </SlideUp>
          ))
        : <SlideUp delay={initialDelay} duration={duration}>{children}</SlideUp>}
    </div>
  );
};

/**
 * AnimatedList - 리스트 아이템 애니메이션
 */
interface AnimatedListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string | number;
  staggerDelay?: number;
  className?: string;
  itemClassName?: string;
}

export function AnimatedList<T>({
  items,
  renderItem,
  keyExtractor,
  staggerDelay = 50,
  className,
  itemClassName,
}: AnimatedListProps<T>) {
  return (
    <div className={className}>
      {items.map((item, index) => (
        <SlideUp
          key={keyExtractor(item, index)}
          delay={index * staggerDelay}
          duration={200}
          className={itemClassName}
        >
          {renderItem(item, index)}
        </SlideUp>
      ))}
    </div>
  );
}

/**
 * BounceIn - 바운스 효과와 함께 등장
 */
interface BounceInProps {
  children: React.ReactNode;
  delay?: number;
  show?: boolean;
  className?: string;
}

export const BounceIn: React.FC<BounceInProps> = ({
  children,
  delay = 0,
  show = true,
  className,
}) => {
  const [shouldAnimate, setShouldAnimate] = useState(false);

  useEffect(() => {
    if (show) {
      setTimeout(() => setShouldAnimate(true), delay);
    } else {
      setShouldAnimate(false);
    }
  }, [show, delay]);

  return (
    <div
      className={cn(
        shouldAnimate ? 'animate-bounce-in' : 'opacity-0 scale-50',
        className
      )}
    >
      {children}
    </div>
  );
};

export default SlideUp;
