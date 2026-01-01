/**
 * Key transformation utilities for API responses.
 *
 * Converts between snake_case (Python/API) and camelCase (TypeScript/JS).
 * See docs/api-conventions.md for usage guidelines.
 */

/**
 * Convert snake_case string to camelCase.
 *
 * @example
 * snakeToCamel('batch_id') // 'batchId'
 * snakeToCamel('step_index') // 'stepIndex'
 */
export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * Convert camelCase string to snake_case.
 *
 * Useful for restoring ID-keyed dictionary keys that were
 * incorrectly transformed by the global response interceptor.
 *
 * @example
 * camelToSnake('batchId') // 'batch_id'
 * camelToSnake('sensorInspection') // 'sensor_inspection'
 * camelToSnake('powerSupply') // 'power_supply'
 */
export function camelToSnake(str: string): string {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase();
}

/**
 * Options for transformKeys function.
 */
export interface TransformKeysOptions {
  /**
   * If true, top-level keys are not transformed.
   * Useful for ID-keyed dictionaries like `{ "sensor_inspection": {...} }`
   * where the key is a batch_id that should remain unchanged.
   */
  preserveTopLevelKeys?: boolean;
}

/**
 * Transform object keys from snake_case to camelCase recursively.
 *
 * @param obj - Object to transform
 * @param options - Transformation options
 * @returns Transformed object with camelCase keys
 *
 * @example
 * // Basic transformation
 * transformKeys({ batch_id: '123', step_index: 1 })
 * // Returns: { batchId: '123', stepIndex: 1 }
 *
 * @example
 * // Preserve top-level keys (for ID-keyed dictionaries)
 * transformKeys(
 *   { sensor_inspection: { total_count: 10 } },
 *   { preserveTopLevelKeys: true }
 * )
 * // Returns: { sensor_inspection: { totalCount: 10 } }
 */
export function transformKeys<T>(
  obj: unknown,
  options?: TransformKeysOptions
): T {
  if (obj === null || obj === undefined) {
    return obj as T;
  }

  // Skip transformation for Blob, ArrayBuffer, and other binary types
  if (obj instanceof Blob || obj instanceof ArrayBuffer || obj instanceof FormData) {
    return obj as T;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => transformKeys(item)) as T;
  }

  // Only transform plain objects (not class instances)
  if (typeof obj === 'object' && obj.constructor === Object) {
    const transformed: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      const newKey = options?.preserveTopLevelKeys ? key : snakeToCamel(key);
      // Child objects always get full transformation (no preserveTopLevelKeys)
      transformed[newKey] = transformKeys(value);
    }
    return transformed as T;
  }

  return obj as T;
}
