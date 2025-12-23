/**
 * Sound Feedback Service
 *
 * Provides audio feedback for scan results using Web Audio API
 */

// Sound types
type SoundType = 'success' | 'error' | 'warning' | 'scan';

// Audio context (created lazily)
let audioContext: AudioContext | null = null;

// Get or create audio context
const getAudioContext = (): AudioContext => {
  if (!audioContext) {
    audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  }
  return audioContext;
};

// Sound configurations
const soundConfigs: Record<SoundType, { frequencies: number[]; durations: number[]; type: OscillatorType }> = {
  success: {
    frequencies: [523.25, 659.25, 783.99], // C5, E5, G5 (major chord arpeggio)
    durations: [100, 100, 200],
    type: 'sine',
  },
  error: {
    frequencies: [200, 150], // Low descending
    durations: [200, 300],
    type: 'square',
  },
  warning: {
    frequencies: [440, 440], // A4 beep
    durations: [100, 100],
    type: 'triangle',
  },
  scan: {
    frequencies: [880], // A5 short beep
    durations: [50],
    type: 'sine',
  },
};

/**
 * Play a tone with specified frequency and duration
 */
const playTone = (
  context: AudioContext,
  frequency: number,
  duration: number,
  type: OscillatorType,
  startTime: number,
  volume: number = 0.3
): void => {
  const oscillator = context.createOscillator();
  const gainNode = context.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(context.destination);

  oscillator.frequency.value = frequency;
  oscillator.type = type;

  // Envelope for smooth sound
  gainNode.gain.setValueAtTime(0, startTime);
  gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.01);
  gainNode.gain.linearRampToValueAtTime(0, startTime + duration / 1000);

  oscillator.start(startTime);
  oscillator.stop(startTime + duration / 1000 + 0.01);
};

/**
 * Play a sound effect
 */
export const playSound = async (type: SoundType): Promise<void> => {
  try {
    const context = getAudioContext();

    // Resume context if suspended (browser autoplay policy)
    if (context.state === 'suspended') {
      await context.resume();
    }

    const config = soundConfigs[type];
    let currentTime = context.currentTime;

    config.frequencies.forEach((freq, index) => {
      playTone(context, freq, config.durations[index], config.type, currentTime);
      currentTime += config.durations[index] / 1000;
    });
  } catch (error) {
    console.warn('[SoundService] Failed to play sound:', error);
  }
};

/**
 * Play success sound (scan successful, operation complete)
 */
export const playSuccessSound = (): Promise<void> => playSound('success');

/**
 * Play error sound (scan failed, operation failed)
 */
export const playErrorSound = (): Promise<void> => playSound('error');

/**
 * Play warning sound (attention needed)
 */
export const playWarningSound = (): Promise<void> => playSound('warning');

/**
 * Play scan sound (QR code detected)
 */
export const playScanSound = (): Promise<void> => playSound('scan');

/**
 * Vibrate device (if supported)
 */
export const vibrate = (pattern: number | number[]): boolean => {
  if (navigator.vibrate) {
    return navigator.vibrate(pattern);
  }
  return false;
};

/**
 * Combined feedback for different events
 */
export const feedback = {
  scanDetected: async (): Promise<void> => {
    await playScanSound();
    vibrate(50);
  },

  success: async (): Promise<void> => {
    await playSuccessSound();
    vibrate([100, 50, 100]);
  },

  error: async (): Promise<void> => {
    await playErrorSound();
    vibrate([200, 100, 200]);
  },

  warning: async (): Promise<void> => {
    await playWarningSound();
    vibrate(150);
  },
};

/**
 * Initialize audio context on user interaction
 * Call this on first user tap/click to enable audio
 */
export const initializeAudio = async (): Promise<void> => {
  try {
    const context = getAudioContext();
    if (context.state === 'suspended') {
      await context.resume();
    }
    // Play silent sound to initialize
    playTone(context, 0, 1, 'sine', context.currentTime, 0);
  } catch (error) {
    console.warn('[SoundService] Failed to initialize audio:', error);
  }
};

/**
 * Sound settings
 */
let soundEnabled = true;

export const setSoundEnabled = (enabled: boolean): void => {
  soundEnabled = enabled;
  localStorage.setItem('sound-enabled', String(enabled));
};

export const isSoundEnabled = (): boolean => {
  const stored = localStorage.getItem('sound-enabled');
  if (stored !== null) {
    return stored === 'true';
  }
  return soundEnabled;
};

// Export wrapped feedback functions that respect sound settings
export const safeFeedback = {
  scanDetected: async (): Promise<void> => {
    if (isSoundEnabled()) await feedback.scanDetected();
    else vibrate(50);
  },

  success: async (): Promise<void> => {
    if (isSoundEnabled()) await feedback.success();
    else vibrate([100, 50, 100]);
  },

  error: async (): Promise<void> => {
    if (isSoundEnabled()) await feedback.error();
    else vibrate([200, 100, 200]);
  },

  warning: async (): Promise<void> => {
    if (isSoundEnabled()) await feedback.warning();
    else vibrate(150);
  },
};
