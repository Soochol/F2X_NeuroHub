/**
 * Swipe Gesture Hook
 *
 * 터치 제스처 감지 훅
 * - 스와이프 방향 감지
 * - 임계값 설정
 * - 시각적 피드백 지원
 */
import { useEffect, useRef, useState, useCallback } from 'react';

type SwipeDirection = 'left' | 'right' | 'up' | 'down';

interface SwipeGestureOptions {
  /** 스와이프 감지 임계값 (px) */
  threshold?: number;
  /** 스와이프 속도 임계값 (px/ms) */
  velocityThreshold?: number;
  /** 스와이프 방향 콜백 */
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  /** 드래그 중 콜백 (시각적 피드백용) */
  onDrag?: (deltaX: number, deltaY: number) => void;
  /** 드래그 종료 콜백 */
  onDragEnd?: () => void;
  /** 비활성화 여부 */
  disabled?: boolean;
}

interface SwipeState {
  /** 현재 스와이프 중인지 */
  isSwiping: boolean;
  /** 현재 드래그 방향 */
  direction: SwipeDirection | null;
  /** X축 이동 거리 */
  deltaX: number;
  /** Y축 이동 거리 */
  deltaY: number;
  /** 스와이프 진행률 (0-1) */
  progress: number;
}

export function useSwipeGesture<T extends HTMLElement>(
  options: SwipeGestureOptions = {}
) {
  const {
    threshold = 50,
    velocityThreshold = 0.3,
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    onDrag,
    onDragEnd,
    disabled = false,
  } = options;

  const ref = useRef<T>(null);
  const startX = useRef(0);
  const startY = useRef(0);
  const startTime = useRef(0);

  const [state, setState] = useState<SwipeState>({
    isSwiping: false,
    direction: null,
    deltaX: 0,
    deltaY: 0,
    progress: 0,
  });

  const getDirection = useCallback(
    (deltaX: number, deltaY: number): SwipeDirection | null => {
      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);

      if (absX < threshold && absY < threshold) return null;

      if (absX > absY) {
        return deltaX > 0 ? 'right' : 'left';
      } else {
        return deltaY > 0 ? 'down' : 'up';
      }
    },
    [threshold]
  );

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      if (disabled) return;

      const touch = e.touches[0];
      startX.current = touch.clientX;
      startY.current = touch.clientY;
      startTime.current = Date.now();

      setState({
        isSwiping: true,
        direction: null,
        deltaX: 0,
        deltaY: 0,
        progress: 0,
      });
    },
    [disabled]
  );

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (disabled || !state.isSwiping) return;

      const touch = e.touches[0];
      const deltaX = touch.clientX - startX.current;
      const deltaY = touch.clientY - startY.current;
      const direction = getDirection(deltaX, deltaY);

      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);
      const maxDelta = Math.max(absX, absY);
      const progress = Math.min(maxDelta / threshold, 1);

      setState({
        isSwiping: true,
        direction,
        deltaX,
        deltaY,
        progress,
      });

      onDrag?.(deltaX, deltaY);

      // Prevent scroll if horizontal swipe
      if (direction === 'left' || direction === 'right') {
        e.preventDefault();
      }
    },
    [disabled, state.isSwiping, getDirection, threshold, onDrag]
  );

  const handleTouchEnd = useCallback(
    (e: TouchEvent) => {
      if (disabled) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - startX.current;
      const deltaY = touch.clientY - startY.current;
      const duration = Date.now() - startTime.current;

      const velocity = Math.max(Math.abs(deltaX), Math.abs(deltaY)) / duration;
      const isValidSwipe =
        Math.abs(deltaX) > threshold ||
        Math.abs(deltaY) > threshold ||
        velocity > velocityThreshold;

      if (isValidSwipe) {
        const direction = getDirection(deltaX, deltaY);

        switch (direction) {
          case 'left':
            onSwipeLeft?.();
            break;
          case 'right':
            onSwipeRight?.();
            break;
          case 'up':
            onSwipeUp?.();
            break;
          case 'down':
            onSwipeDown?.();
            break;
        }
      }

      setState({
        isSwiping: false,
        direction: null,
        deltaX: 0,
        deltaY: 0,
        progress: 0,
      });

      onDragEnd?.();
    },
    [
      disabled,
      threshold,
      velocityThreshold,
      getDirection,
      onSwipeLeft,
      onSwipeRight,
      onSwipeUp,
      onSwipeDown,
      onDragEnd,
    ]
  );

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: false });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return {
    ref,
    ...state,
  };
}

/**
 * 수평 스와이프 전용 훅
 */
export function useHorizontalSwipe<T extends HTMLElement>(options: {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  threshold?: number;
  disabled?: boolean;
}) {
  return useSwipeGesture<T>({
    ...options,
    onSwipeUp: undefined,
    onSwipeDown: undefined,
  });
}

/**
 * 수직 스와이프 전용 훅
 */
export function useVerticalSwipe<T extends HTMLElement>(options: {
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
  disabled?: boolean;
}) {
  return useSwipeGesture<T>({
    ...options,
    onSwipeLeft: undefined,
    onSwipeRight: undefined,
  });
}

export default useSwipeGesture;
