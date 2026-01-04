/**
 * Route constants for centralized path management.
 */

export const ROUTES = {
  DASHBOARD: '/',
  BATCHES: '/batches',
  BATCH_DETAIL: '/batches/:batchId',
  SEQUENCES: '/sequences',
  SEQUENCE_DETAIL: '/sequences/:sequenceName',
  MANUAL: '/manual',
  RESULTS: '/results',
  LOGS: '/logs',
  MONITOR: '/monitor',
  SETTINGS: '/settings',
} as const;

/**
 * Helper function to generate batch detail route.
 */
export function getBatchDetailRoute(batchId: string): string {
  return `/batches/${batchId}`;
}

/**
 * Helper function to generate sequence detail route.
 */
export function getSequenceDetailRoute(sequenceName: string): string {
  return `/sequences/${sequenceName}`;
}

/**
 * Navigation items configuration.
 */
export const NAV_ITEMS = [
  { path: ROUTES.DASHBOARD, label: 'Dashboard', iconName: 'LayoutDashboard' },
  { path: ROUTES.BATCHES, label: 'Batches', iconName: 'Layers' },
  { path: ROUTES.SEQUENCES, label: 'Sequences', iconName: 'GitBranch' },
  { path: ROUTES.MANUAL, label: 'Manual', iconName: 'Wrench' },
  { path: ROUTES.RESULTS, label: 'Results', iconName: 'ClipboardList' },
  { path: ROUTES.LOGS, label: 'Logs', iconName: 'FileText' },
  { path: ROUTES.MONITOR, label: 'Monitor', iconName: 'Activity' },
  { path: ROUTES.SETTINGS, label: 'Settings', iconName: 'Settings' },
] as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = (typeof ROUTES)[RouteKey];
