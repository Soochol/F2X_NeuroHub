/**
 * Theme exports and utilities for Supabase-style theming
 */
import theme from './theme.json';

export { theme };

// Type definitions
export type Theme = typeof theme;
export type ThemeColors = typeof theme.colors;
export type ThemeTypography = typeof theme.typography;
export type ThemeComponents = typeof theme.components;
export type ThemeCharts = typeof theme.charts;

// Component styles
export {
  tableStyles,
  badgeStyles,
  layoutStyles,
  typographyStyles,
  containerStyles,
  formStyles,
  spacingStyles,
} from './componentStyles';

// Export default theme
export default theme;
