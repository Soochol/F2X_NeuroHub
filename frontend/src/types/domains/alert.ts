/**
 * Alert Types - System alerts and notifications
 */

import { AlertSeverity, AlertStatus, AlertType } from './enums';
import type { BaseQueryParams } from './common';

// ============================================================================
// Alert Model
// ============================================================================

export interface Alert {
  id: number;
  alert_type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  lot_id?: number;
  lot_number?: string;
  serial_id?: number;
  serial_number?: string;
  process_id?: number;
  process_name?: string;
  created_at: string;
  read_at?: string;
  read_by_id?: number;
  archived_at?: string;
}

// ============================================================================
// Alert CRUD
// ============================================================================

export interface AlertCreate {
  alert_type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  lot_id?: number;
  serial_id?: number;
  process_id?: number;
}

export interface AlertUpdate {
  status?: AlertStatus;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  unread_count: number;
}

// ============================================================================
// Query Parameters
// ============================================================================

export interface AlertQueryParams extends BaseQueryParams {
  severity?: AlertSeverity;
  status?: AlertStatus;
}
