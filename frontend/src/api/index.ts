/**
 * API Exports - Central export point for all API endpoints
 */

export { default as apiClient } from './client';
export { authApi } from './endpoints/auth';
export { dashboardApi } from './endpoints/dashboard';
export { analyticsApi } from './endpoints/analytics';
export { alertsApi } from './endpoints/alerts';
export { serialsApi } from './endpoints/serials';
export { lotsApi } from './endpoints/lots';
export { wipItemsApi } from './endpoints/wipItems';
export { usersApi } from './endpoints/users';
export { processesApi } from './endpoints/processes';
export { processDataApi } from './endpoints/processData';
export { productModelsApi } from './endpoints/productModels';
export { productionLinesApi } from './endpoints/productionLines';
export { equipmentApi } from './endpoints/equipment';
export {
  errorLogsApi,
  type ErrorLog,
  type ErrorLogStats,
  type ErrorLogListResponse,
  type ErrorCodeCount,
  type HourlyErrorCount,
  type TopErrorPath,
  type ErrorLogFilters
} from './endpoints/errorLogs';
