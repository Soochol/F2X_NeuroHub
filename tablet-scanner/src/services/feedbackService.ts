/**
 * Feedback Service
 *
 * 복합 피드백 시스템 (사운드 + 진동 + 시각)
 * - 성공: 녹색 pulse + 사운드 + 진동
 * - 에러: 빨간 shake + 사운드 + 진동
 * - 스캔: 경쾌한 비프 + 짧은 진동
 */

type FeedbackType = 'success' | 'error' | 'warning' | 'scan' | 'info';

interface FeedbackOptions {
  sound?: boolean;
  vibration?: boolean;
  visual?: boolean;
}

export interface FeedbackConfig {
  soundEnabled: boolean;
  vibrationEnabled: boolean;
  visualEnabled: boolean;
}

// 기본 설정
let config: FeedbackConfig = {
  soundEnabled: true,
  vibrationEnabled: true,
  visualEnabled: true,
};

// 오디오 컨텍스트 (lazy initialization)
let audioContext: AudioContext | null = null;

/**
 * 오디오 컨텍스트 초기화
 */
export function initAudioContext(): void {
  if (!audioContext) {
    audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  }
}

/**
 * 설정 업데이트
 */
export function updateFeedbackConfig(newConfig: Partial<FeedbackConfig>): void {
  config = { ...config, ...newConfig };
  // localStorage에 저장
  localStorage.setItem('feedbackConfig', JSON.stringify(config));
}

/**
 * 설정 로드
 */
export function loadFeedbackConfig(): FeedbackConfig {
  try {
    const saved = localStorage.getItem('feedbackConfig');
    if (saved) {
      config = { ...config, ...JSON.parse(saved) };
    }
  } catch {
    // 기본값 유지
  }
  return config;
}

/**
 * 현재 설정 반환
 */
export function getFeedbackConfig(): FeedbackConfig {
  return { ...config };
}

// ============================================================
// 진동 패턴
// ============================================================

const vibrationPatterns: Record<FeedbackType, number[]> = {
  success: [30, 20, 30],        // 짧은 더블 진동
  error: [50, 30, 50, 30, 50],  // 긴 트리플 진동
  warning: [100, 50, 100],      // 중간 더블 진동
  scan: [20],                   // 아주 짧은 진동
  info: [15],                   // 미세한 진동
};

/**
 * 진동 발생
 */
function vibrate(type: FeedbackType): void {
  if (!config.vibrationEnabled) return;
  if (!navigator.vibrate) return;

  try {
    navigator.vibrate(vibrationPatterns[type]);
  } catch {
    // 진동 실패 무시
  }
}

// ============================================================
// 사운드 생성
// ============================================================

interface SoundConfig {
  frequency: number;
  duration: number;
  type: OscillatorType;
  volume: number;
}

const soundConfigs: Record<FeedbackType, SoundConfig[]> = {
  success: [
    { frequency: 523.25, duration: 100, type: 'sine', volume: 0.3 }, // C5
    { frequency: 659.25, duration: 100, type: 'sine', volume: 0.3 }, // E5
    { frequency: 783.99, duration: 150, type: 'sine', volume: 0.3 }, // G5
  ],
  error: [
    { frequency: 200, duration: 150, type: 'square', volume: 0.2 },
    { frequency: 150, duration: 200, type: 'square', volume: 0.2 },
  ],
  warning: [
    { frequency: 440, duration: 100, type: 'triangle', volume: 0.25 },
    { frequency: 440, duration: 100, type: 'triangle', volume: 0.25 },
  ],
  scan: [
    { frequency: 880, duration: 50, type: 'sine', volume: 0.2 },
  ],
  info: [
    { frequency: 600, duration: 80, type: 'sine', volume: 0.15 },
  ],
};

/**
 * 소리 재생
 */
async function playSound(type: FeedbackType): Promise<void> {
  if (!config.soundEnabled) return;

  try {
    initAudioContext();
    if (!audioContext) return;

    // Resume if suspended
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    const sounds = soundConfigs[type];
    let offset = 0;

    for (const sound of sounds) {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.type = sound.type;
      oscillator.frequency.value = sound.frequency;

      gainNode.gain.value = sound.volume;
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + offset + sound.duration / 1000
      );

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.start(audioContext.currentTime + offset);
      oscillator.stop(audioContext.currentTime + offset + sound.duration / 1000);

      offset += sound.duration / 1000 + 0.02; // 20ms gap
    }
  } catch {
    // 소리 재생 실패 무시
  }
}

// ============================================================
// 시각적 피드백 (이벤트 발행)
// ============================================================

type VisualFeedbackCallback = (type: FeedbackType) => void;
const visualCallbacks: Set<VisualFeedbackCallback> = new Set();

/**
 * 시각적 피드백 리스너 등록
 */
export function onVisualFeedback(callback: VisualFeedbackCallback): () => void {
  visualCallbacks.add(callback);
  return () => visualCallbacks.delete(callback);
}

/**
 * 시각적 피드백 발행
 */
function emitVisualFeedback(type: FeedbackType): void {
  if (!config.visualEnabled) return;
  visualCallbacks.forEach((cb) => cb(type));
}

// ============================================================
// 메인 피드백 함수
// ============================================================

/**
 * 복합 피드백 발생
 */
export async function feedback(
  type: FeedbackType,
  options: FeedbackOptions = {}
): Promise<void> {
  const {
    sound = true,
    vibration = true,
    visual = true,
  } = options;

  const promises: Promise<void>[] = [];

  if (sound) {
    promises.push(playSound(type));
  }

  if (vibration) {
    vibrate(type);
  }

  if (visual) {
    emitVisualFeedback(type);
  }

  await Promise.all(promises);
}

/**
 * 성공 피드백
 */
export async function successFeedback(options?: FeedbackOptions): Promise<void> {
  return feedback('success', options);
}

/**
 * 에러 피드백
 */
export async function errorFeedback(options?: FeedbackOptions): Promise<void> {
  return feedback('error', options);
}

/**
 * 경고 피드백
 */
export async function warningFeedback(options?: FeedbackOptions): Promise<void> {
  return feedback('warning', options);
}

/**
 * 스캔 감지 피드백
 */
export async function scanFeedback(options?: FeedbackOptions): Promise<void> {
  return feedback('scan', options);
}

/**
 * 정보 피드백
 */
export async function infoFeedback(options?: FeedbackOptions): Promise<void> {
  return feedback('info', options);
}

// ============================================================
// React Hook 용 헬퍼
// ============================================================

/**
 * 피드백 서비스 객체
 */
export const feedbackService = {
  success: successFeedback,
  error: errorFeedback,
  warning: warningFeedback,
  scan: scanFeedback,
  info: infoFeedback,
  init: initAudioContext,
  updateConfig: updateFeedbackConfig,
  loadConfig: loadFeedbackConfig,
  getConfig: getFeedbackConfig,
  onVisual: onVisualFeedback,
};

export default feedbackService;
