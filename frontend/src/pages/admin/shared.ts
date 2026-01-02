/**
 * Shared types, styles, and utilities for Admin components
 */

import type { UserRole } from '@/types/api';
import { UserRole as UserRoleEnum } from '@/types/api';

// ============================================================================
// Types
// ============================================================================

export type TabType = 'users' | 'processes' | 'products' | 'productionLines' | 'equipment' | 'sequences';

export interface UserFormData {
  username: string;
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
  is_active: boolean;
}

export interface ProcessFormData {
  process_number: number;
  process_code: string;
  process_name_ko: string;
  process_name_en: string;
  description: string;
  sort_order: number;
  is_active: boolean;
  estimated_duration_seconds: number | '';
  quality_criteria: string;
  defect_items: string[];
  auto_print_label: boolean;
  label_template_type: string | null;
  process_type: string;
}

export interface ProductFormData {
  model_code: string;
  model_name: string;
  category: string;
  status: 'ACTIVE' | 'INACTIVE' | 'DISCONTINUED';
}

export interface ProductionLineFormData {
  line_code: string;
  line_name: string;
  description: string;
  cycle_time_sec: number | '';
  location: string;
  is_active: boolean;
}

export interface EquipmentFormData {
  equipment_code: string;
  equipment_name: string;
  equipment_type: string;
  description: string;
  process_id: number | '';
  production_line_id: number | '';
  manufacturer: string;
  model_number: string;
  serial_number: string;
  status: string;
  is_active: boolean;
}

// ============================================================================
// Default Form Values
// ============================================================================

export const defaultUserFormData: UserFormData = {
  username: '',
  full_name: '',
  email: '',
  password: '',
  role: UserRoleEnum.OPERATOR,
  is_active: true,
};

export const defaultProcessFormData: ProcessFormData = {
  process_number: 1,
  process_code: '',
  process_name_ko: '',
  process_name_en: '',
  description: '',
  sort_order: 1,
  is_active: true,
  estimated_duration_seconds: '',
  quality_criteria: '{}',
  defect_items: [],
  auto_print_label: false,
  label_template_type: null,
  process_type: 'MANUFACTURING',
};

export const defaultProductFormData: ProductFormData = {
  model_code: '',
  model_name: '',
  category: '',
  status: 'ACTIVE',
};

export const defaultProductionLineFormData: ProductionLineFormData = {
  line_code: '',
  line_name: '',
  description: '',
  cycle_time_sec: '',
  location: '',
  is_active: true,
};

export const defaultEquipmentFormData: EquipmentFormData = {
  equipment_code: '',
  equipment_name: '',
  equipment_type: '',
  description: '',
  process_id: '',
  production_line_id: '',
  manufacturer: '',
  model_number: '',
  serial_number: '',
  status: 'AVAILABLE',
  is_active: true,
};

// ============================================================================
// Shared Styles
// ============================================================================

export const styles = {
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '20px' },
  title: { fontSize: '18px', fontWeight: '600', color: 'var(--color-text-primary)' },
  loading: { textAlign: 'center' as const, padding: '40px', color: 'var(--color-text-secondary)' },
  error: { textAlign: 'center' as const, padding: '40px', color: 'var(--color-error)' },
  th: { padding: '12px', fontWeight: '600', color: 'var(--color-text-primary)' },
  td: { padding: '12px', color: 'var(--color-text-primary)' },
  actions: { display: 'flex', gap: '8px', justifyContent: 'center' },
  checkbox: { marginBottom: '15px' },
  checkboxLabel: { display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' },
  checkboxInput: { width: '16px', height: '16px', accentColor: 'var(--color-brand)' },
  checkboxText: { fontSize: '14px', fontWeight: '500', color: 'var(--color-text-primary)' },
  modalFooter: { display: 'flex', gap: '10px', justifyContent: 'flex-end' },
};

export const getTabStyle = (isActive: boolean) => ({
  padding: '12px 24px',
  backgroundColor: isActive ? 'var(--color-brand)' : 'var(--color-bg-secondary)',
  color: isActive ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
  border: 'none',
  borderBottom: isActive ? '3px solid var(--color-brand-500)' : '3px solid transparent',
  borderRadius: '6px 6px 0 0',
  cursor: 'pointer',
  fontWeight: isActive ? 'bold' : '500',
  fontSize: '15px',
  transition: 'all 0.2s',
});

export const getRowStyle = (idx: number) => ({
  borderBottom: '1px solid var(--color-border)',
  backgroundColor: idx % 2 === 0 ? 'var(--color-bg-primary)' : 'var(--color-bg-secondary)',
});
