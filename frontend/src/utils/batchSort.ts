/**
 * Batch Sorting Utilities
 *
 * Provides consistent sorting for batches across the application
 */

import type { BatchSummary } from '@/types/station';

/**
 * Parses slot ID for numeric comparison
 * Handles: "1", "2", "10", "1A", "A1", 1, 2, 10, null, undefined
 *
 * Strategy:
 * - Convert to string if number
 * - Extract leading numeric portion for comparison
 * - Fall back to string comparison if no number found
 * - Place nulls/undefined at the end
 */
const parseSlotId = (slotId: string | number | undefined): { num: number; full: string } | null => {
  if (slotId === null || slotId === undefined) return null;

  // Convert to string if number
  const slotStr = String(slotId);
  if (!slotStr) return null;

  // Extract leading digits
  const match = slotStr.match(/^(\d+)/);
  const num = match ? parseInt(match[1], 10) : -1;

  return { num, full: slotStr };
};

/**
 * Compare function for sorting batches by slot_id in ascending order
 *
 * Rules:
 * 1. Batches with slot_id come before batches without
 * 2. Numeric portion sorted numerically (2 < 10)
 * 3. If numeric parts equal, sort by full string (10A < 10B)
 * 4. Nulls/undefined at the end
 *
 * @example
 * ["10", "2", "1A", "1", undefined, "3"] → ["1", "1A", "2", "3", "10", undefined]
 */
export const compareBySlotId = (a: BatchSummary, b: BatchSummary): number => {
  const slotA = parseSlotId(a.slotId);
  const slotB = parseSlotId(b.slotId);

  // Both null - maintain order
  if (!slotA && !slotB) return 0;

  // A is null - B comes first
  if (!slotA) return 1;

  // B is null - A comes first
  if (!slotB) return -1;

  // Both have numeric parts - compare numerically
  if (slotA.num !== slotB.num) {
    // Handle cases where one has no numeric part (-1)
    if (slotA.num === -1) return 1;
    if (slotB.num === -1) return -1;
    return slotA.num - slotB.num;
  }

  // Numeric parts equal - compare full string
  return slotA.full.localeCompare(slotB.full, undefined, {
    numeric: true,
    sensitivity: 'base',
  });
};

/**
 * Sort batches by slot_id (ascending, nulls last)
 * Returns a new sorted array without mutating the original
 *
 * @param batches - Array of batches to sort
 * @returns New sorted array
 */
export const sortBatchesBySlotId = (batches: BatchSummary[]): BatchSummary[] => {
  return [...batches].sort(compareBySlotId);
};
