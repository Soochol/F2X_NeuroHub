/**
 * Admin Page - Re-export from admin module
 *
 * This file exists for backwards compatibility.
 * The actual implementation has been refactored into separate files
 * under the /pages/admin/ directory for better maintainability.
 *
 * Original file: 1,003 lines → Split into 7 files (~150-470 lines each)
 *
 * New structure:
 * - admin/shared.ts: Types, styles, and utilities
 * - admin/UserManagement.tsx: User CRUD operations
 * - admin/ProcessManagement.tsx: Process configuration
 * - admin/ProductModelManagement.tsx: Product model management
 * - admin/ProductionLineManagement.tsx: Production line setup
 * - admin/EquipmentManagement.tsx: Equipment tracking
 * - admin/AdminPage.tsx: Tab navigation container
 */

export {
  AdminPage,
  EquipmentManagement,
  ProcessManagement,
  ProductionLineManagement,
  ProductModelManagement,
  UserManagement,
} from './admin';
