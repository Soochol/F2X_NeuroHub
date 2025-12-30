/**
 * Application Constants
 *
 * Centralized constants for the tablet-scanner app
 */

// ============================================================
// WIP Validation
// ============================================================

/** WIP ID format pattern: WIP-{10-20 alphanumeric}-{3 digits} */
export const WIP_ID_PATTERN = /^WIP-[A-Z0-9-]{10,20}-\d{3}$/;

// ============================================================
// Scanner Configuration
// ============================================================

/** Debounce time between duplicate scans (ms) */
export const SCAN_DEBOUNCE_MS = 2000;

/** Default scanner FPS */
export const SCANNER_FPS = 10;

/** Default QR box size (pixels) */
export const SCANNER_QRBOX_SIZE = 220;

/** Pause duration after successful scan (ms) */
export const SCAN_SUCCESS_PAUSE_MS = 1500;

/** Scanner initialization delay (ms) */
export const SCANNER_INIT_DELAY_MS = 100;

// ============================================================
// API Configuration
// ============================================================

/** API request timeout (ms) */
export const API_TIMEOUT_MS = 10000;

/** Default API base URL */
export const API_BASE_URL = '/api/v1';

// ============================================================
// Offline Queue
// ============================================================

/** Maximum retry attempts for queued items */
export const QUEUE_MAX_RETRIES = 5;

/** Queue status check interval (ms) */
export const QUEUE_CHECK_INTERVAL_MS = 5000;

// ============================================================
// Process Configuration
// ============================================================

/** Maximum number of manufacturing processes */
export const MAX_PROCESS_COUNT = 8;

/** Auto-start delay after WIP scan (ms) */
export const AUTO_START_DELAY_MS = 300;

// ============================================================
// UI Timing
// ============================================================

/** Toast notification default duration (ms) */
export const TOAST_DURATION_MS = 3000;

/** Visual feedback duration (ms) */
export const VISUAL_FEEDBACK_DURATION_MS = 300;

/** Success navigation delay (ms) */
export const SUCCESS_NAVIGATION_DELAY_MS = 800;

/** Error shake animation reset delay (ms) */
export const ERROR_SHAKE_RESET_MS = 600;

// ============================================================
// Storage Keys
// ============================================================

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  FEEDBACK_CONFIG: 'feedbackConfig',
  APP_STORE: 'tablet-scanner-storage',
  UI_STORE: 'ui-storage',
  OFFLINE_QUEUE_PREFIX: 'offline-queue-',
} as const;
