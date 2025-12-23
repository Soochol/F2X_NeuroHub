/**
 * Feedback Hook
 *
 * 피드백 서비스를 React 컴포넌트에서 쉽게 사용하기 위한 훅
 */
import { useEffect, useState, useCallback } from 'react';
import {
  feedbackService,
  loadFeedbackConfig,
  type FeedbackConfig,
} from '@/services/feedbackService';

type FeedbackType = 'success' | 'error' | 'warning' | 'scan' | 'info';

interface UseFeedbackReturn {
  /** 피드백 설정 */
  config: FeedbackConfig;
  /** 사운드 활성화 여부 */
  soundEnabled: boolean;
  /** 진동 활성화 여부 */
  vibrationEnabled: boolean;
  /** 시각적 피드백 활성화 여부 */
  visualEnabled: boolean;
  /** 현재 시각적 피드백 타입 */
  visualFeedback: FeedbackType | null;
  /** 사운드 토글 */
  toggleSound: () => void;
  /** 진동 토글 */
  toggleVibration: () => void;
  /** 시각적 피드백 토글 */
  toggleVisual: () => void;
  /** 성공 피드백 */
  success: () => Promise<void>;
  /** 에러 피드백 */
  error: () => Promise<void>;
  /** 경고 피드백 */
  warning: () => Promise<void>;
  /** 스캔 피드백 */
  scan: () => Promise<void>;
  /** 정보 피드백 */
  info: () => Promise<void>;
}

export function useFeedback(): UseFeedbackReturn {
  const [config, setConfig] = useState<FeedbackConfig>(() => loadFeedbackConfig());
  const [visualFeedback, setVisualFeedback] = useState<FeedbackType | null>(null);

  // 초기화 및 시각적 피드백 리스너 등록
  useEffect(() => {
    // 오디오 컨텍스트 초기화를 위한 첫 인터랙션 감지
    const handleFirstInteraction = () => {
      feedbackService.init();
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('touchstart', handleFirstInteraction);
    };

    document.addEventListener('click', handleFirstInteraction);
    document.addEventListener('touchstart', handleFirstInteraction);

    // 시각적 피드백 리스너
    const unsubscribe = feedbackService.onVisual((type) => {
      setVisualFeedback(type);
      // 자동으로 300ms 후 초기화
      setTimeout(() => setVisualFeedback(null), 300);
    });

    return () => {
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('touchstart', handleFirstInteraction);
      unsubscribe();
    };
  }, []);

  // 설정 토글 함수들
  const toggleSound = useCallback(() => {
    const newValue = !config.soundEnabled;
    feedbackService.updateConfig({ soundEnabled: newValue });
    setConfig((prev: FeedbackConfig) => ({ ...prev, soundEnabled: newValue }));
  }, [config.soundEnabled]);

  const toggleVibration = useCallback(() => {
    const newValue = !config.vibrationEnabled;
    feedbackService.updateConfig({ vibrationEnabled: newValue });
    setConfig((prev: FeedbackConfig) => ({ ...prev, vibrationEnabled: newValue }));
  }, [config.vibrationEnabled]);

  const toggleVisual = useCallback(() => {
    const newValue = !config.visualEnabled;
    feedbackService.updateConfig({ visualEnabled: newValue });
    setConfig((prev: FeedbackConfig) => ({ ...prev, visualEnabled: newValue }));
  }, [config.visualEnabled]);

  return {
    config,
    soundEnabled: config.soundEnabled,
    vibrationEnabled: config.vibrationEnabled,
    visualEnabled: config.visualEnabled,
    visualFeedback,
    toggleSound,
    toggleVibration,
    toggleVisual,
    success: feedbackService.success,
    error: feedbackService.error,
    warning: feedbackService.warning,
    scan: feedbackService.scan,
    info: feedbackService.info,
  };
}

/**
 * 시각적 피드백 래퍼 컴포넌트용 훅
 */
export function useVisualFeedbackClass(
  baseClass: string = ''
): {
  className: string;
  feedbackType: FeedbackType | null;
} {
  const { visualFeedback } = useFeedback();

  const getFeedbackClass = (): string => {
    switch (visualFeedback) {
      case 'success':
        return 'animate-success-pulse';
      case 'error':
        return 'animate-error-shake';
      case 'warning':
        return 'animate-pulse';
      case 'scan':
        return 'animate-scan-line';
      default:
        return '';
    }
  };

  return {
    className: `${baseClass} ${getFeedbackClass()}`.trim(),
    feedbackType: visualFeedback,
  };
}

export default useFeedback;
