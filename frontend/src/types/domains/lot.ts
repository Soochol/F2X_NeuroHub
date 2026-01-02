/**
 * Lot Types - Production lot management
 */

import { LotStatus } from './enums';
import type { BaseQueryParams } from './common';
import type { ProductModel } from './equipment';

// ============================================================================
// Lot Model
// ============================================================================

export interface Lot {
  id: number;
  lot_number: string;
  product_model_id: number;
  product_model?: ProductModel;
  target_quantity: number;
  production_date: string;
  status: LotStatus;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  closed_at?: string;
  parent_spring_lot?: string;
  sma_spring_lot?: string;
  shift?: string;
  serial_count?: number;
  wip_count?: number;
  actual_quantity?: number;
  passed_quantity?: number;
  failed_quantity?: number;
}

// ============================================================================
// Lot CRUD
// ============================================================================

export interface LotCreate {
  product_model_id: number;
  production_line_id: number;
  target_quantity: number;
  production_date: string;
  parent_spring_lot?: string;
  sma_spring_lot?: string;
}

export interface LotUpdate {
  status?: LotStatus;
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface LotQueryParams extends BaseQueryParams {
  status?: LotStatus;
  product_model_id?: number;
}
