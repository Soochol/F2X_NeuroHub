/**
 * Design Tokens - 디자인 시스템 상수
 *
 * 태블릿 터치 최적화 + 산업용 프로페셔널 UI
 */

// 터치 타겟 최소 크기 (44px 이상 권장)
export const TOUCH_TARGETS = {
  minimum: 44,      // 최소 터치 영역
  comfortable: 48,  // 편안한 터치 영역
  large: 56,        // 큰 버튼
  xlarge: 64,       // 메인 액션 버튼
} as const;

// 간격 시스템 (8px 기반)
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  '2xl': 32,
  '3xl': 48,
} as const;

// 폰트 크기 (태블릿 최적화)
export const FONT_SIZES = {
  xs: '0.75rem',    // 12px - 보조 텍스트
  sm: '0.875rem',   // 14px - 일반 텍스트
  base: '1rem',     // 16px - 기본
  lg: '1.125rem',   // 18px - 강조
  xl: '1.25rem',    // 20px - 제목
  '2xl': '1.5rem',  // 24px - 큰 제목
  '3xl': '1.875rem',// 30px - 메인 액션
} as const;

// 색상 팔레트 (산업용)
export const COLORS = {
  // Primary - 착공/메인 액션
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  // Success - 합격/완료
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
  },
  // Danger - 불량/에러
  danger: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
  },
  // Warning - 경고/오프라인
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    500: '#f59e0b',
    600: '#d97706',
  },
  // Neutral - 배경/텍스트
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#e5e5e5',
    300: '#d4d4d4',
    400: '#a3a3a3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
  },
} as const;

// 그림자 (깊이 표현)
export const SHADOWS = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
} as const;

// 테두리 반경
export const RADIUS = {
  sm: '0.375rem',   // 6px
  md: '0.5rem',     // 8px
  lg: '0.75rem',    // 12px
  xl: '1rem',       // 16px
  '2xl': '1.5rem',  // 24px
  full: '9999px',
} as const;

// 애니메이션 시간
export const TRANSITIONS = {
  fast: '150ms',
  normal: '200ms',
  slow: '300ms',
} as const;

// 레이아웃 상수
export const LAYOUT = {
  maxWidth: '640px',        // 모바일/태블릿 최대 너비
  headerHeight: '64px',     // 헤더 높이
  footerHeight: '80px',     // FAB 영역 높이
  cardPadding: '16px',      // 카드 내부 패딩
  pagePadding: '16px',      // 페이지 좌우 패딩
} as const;
