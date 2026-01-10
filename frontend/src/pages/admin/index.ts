/**
 * Admin Module - Barrel Export
 *
 * Re-exports all admin management components for clean imports:
 * - AdminPage: Main admin page with tab navigation
 * - Individual management components for standalone use
 * - Shared types and utilities
 */

// Main admin page
export { AdminPage } from './AdminPage';

// Individual management components
export { EquipmentManagement } from './EquipmentManagement';
export { ProcessManagement } from './ProcessManagement';
export { ProductionLineManagement } from './ProductionLineManagement';
export { ProductModelManagement } from './ProductModelManagement';
export { SequenceManagement } from './SequenceManagement';
export { UserManagement } from './UserManagement';

// Other admin pages
export { SerialInspectorPage } from './SerialInspectorPage';

// Shared types and utilities
export type {
  EquipmentFormData,
  ProcessFormData,
  ProductFormData,
  ProductionLineFormData,
  TabType,
  UserFormData,
} from './shared';
