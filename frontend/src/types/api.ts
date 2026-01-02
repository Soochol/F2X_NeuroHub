/**
 * F2X NeuroHub MES - API Type Definitions
 *
 * TypeScript types matching backend Pydantic schemas.
 *
 * This file re-exports all types from domain modules for backwards compatibility.
 * The actual type definitions are now organized in src/types/domains/ directory:
 *
 * - domains/enums.ts: All enumeration types
 * - domains/common.ts: Shared types and utilities
 * - domains/user.ts: User and authentication
 * - domains/equipment.ts: ProductModel, ProductionLine, Equipment
 * - domains/process.ts: Process, ProcessData, ProcessHeaders
 * - domains/lot.ts: Lot management
 * - domains/serial.ts: Serial and SerialTrace
 * - domains/wip.ts: WIP tracking
 * - domains/alert.ts: System alerts
 * - domains/audit.ts: Audit logging
 * - domains/analytics.ts: Dashboard and analytics
 * - domains/measurement.ts: Measurement history
 * - domains/printer.ts: Printer monitoring
 *
 * Original file: 814 lines → Split into 13 domain modules
 */

// Re-export everything from domains
export * from './domains';
