/**
 * Audit Types - Audit logging
 */

import { AuditAction } from './enums';
import type { User } from './user';

// ============================================================================
// Audit Log Model
// ============================================================================

export interface AuditLog {
  id: number;
  entity_type: string;
  entity_id: number;
  action: AuditAction;
  user_id?: number;
  user?: User;
  changes?: Record<string, any>;
  timestamp: string;
}
