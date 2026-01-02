/**
 * Enums - All enumeration types
 */

export enum UserRole {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  OPERATOR = 'OPERATOR',
}

export enum LotStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CLOSED = 'CLOSED',
}

export enum SerialStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  PASS = 'PASSED',
  FAIL = 'FAILED',
}

export enum ProcessResult {
  PASS = 'PASS',
  FAIL = 'FAIL',
  REWORK = 'REWORK',
}

export enum DataLevel {
  NORMAL = 'NORMAL',
  DETAILED = 'DETAILED',
}

export enum WIPStatus {
  CREATED = 'CREATED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CONVERTED = 'CONVERTED',
}

export enum AuditAction {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
}

export enum AlertType {
  DEFECT_DETECTED = 'DEFECT_DETECTED',
  REWORK_REQUEST = 'REWORK_REQUEST',
  PROCESS_DELAY = 'PROCESS_DELAY',
  LOT_COMPLETED = 'LOT_COMPLETED',
  LOT_CLOSED = 'LOT_CLOSED',
  EQUIPMENT_FAILURE = 'EQUIPMENT_FAILURE',
  QUALITY_THRESHOLD = 'QUALITY_THRESHOLD',
  SYSTEM_ERROR = 'SYSTEM_ERROR',
  MANUAL = 'MANUAL',
}

export enum AlertSeverity {
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export enum AlertStatus {
  UNREAD = 'UNREAD',
  READ = 'READ',
  ARCHIVED = 'ARCHIVED',
}

export enum HeaderStatus {
  OPEN = 'OPEN',
  CLOSED = 'CLOSED',
  CANCELLED = 'CANCELLED',
}
