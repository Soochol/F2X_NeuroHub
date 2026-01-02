/**
 * ParameterForm - Dynamic form for sequence parameters.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Settings, AlertCircle, Info } from 'lucide-react';
import { Input } from '../../atoms/Input';
import { Select } from '../../atoms/Select';
import { Button } from '../../atoms/Button';
import type { ParameterSchema } from '../../../types';

interface ParameterFormProps {
  /** Parameter schema definitions */
  parameters: ParameterSchema[];
  /** Initial values */
  initialValues?: Record<string, unknown>;
  /** Called when values change */
  onChange?: (values: Record<string, unknown>) => void;
  /** Called on form submit */
  onSubmit?: (values: Record<string, unknown>) => void;
  /** Validation errors */
  errors?: Record<string, string>;
  /** Whether form is read-only */
  readOnly?: boolean;
  /** Show submit button */
  showSubmit?: boolean;
  /** Submit button text */
  submitText?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Convert value to appropriate type based on parameter schema.
 */
function convertValue(value: unknown, type: ParameterSchema['type']): unknown {
  if (value === '' || value === null || value === undefined) {
    return undefined;
  }

  switch (type) {
    case 'float':
      return parseFloat(String(value));
    case 'integer':
      return parseInt(String(value), 10);
    case 'boolean':
      return value === true || value === 'true';
    case 'string':
    default:
      return String(value);
  }
}

/**
 * Validate a parameter value against its schema.
 */
function validateParameter(
  value: unknown,
  schema: ParameterSchema
): string | undefined {
  if (value === undefined || value === null || value === '') {
    return undefined; // Allow empty values (use default)
  }

  if (schema.type === 'float' || schema.type === 'integer') {
    const numValue = Number(value);
    if (isNaN(numValue)) {
      return `Invalid ${schema.type} value`;
    }
    if (schema.min !== undefined && numValue < schema.min) {
      return `Value must be at least ${schema.min}`;
    }
    if (schema.max !== undefined && numValue > schema.max) {
      return `Value must be at most ${schema.max}`;
    }
  }

  if (schema.options && schema.options.length > 0) {
    if (!schema.options.includes(String(value))) {
      return `Value must be one of: ${schema.options.join(', ')}`;
    }
  }

  return undefined;
}

export function ParameterForm({
  parameters,
  initialValues = {},
  onChange,
  onSubmit,
  errors: externalErrors = {},
  readOnly = false,
  showSubmit = true,
  submitText = 'Apply',
  className = '',
}: ParameterFormProps) {
  // Build default values from schema (memoized)
  const defaultValues = useMemo(
    () =>
      parameters.reduce(
        (acc, param) => {
          acc[param.name] = param.default;
          return acc;
        },
        {} as Record<string, unknown>
      ),
    [parameters]
  );

  const [values, setValues] = useState<Record<string, unknown>>({
    ...defaultValues,
    ...initialValues,
  });
  const [internalErrors, setInternalErrors] = useState<Record<string, string>>({});

  // Merge external and internal errors
  const allErrors = { ...internalErrors, ...externalErrors };

  // Update values when initialValues or parameters change
  useEffect(() => {
    setValues({ ...defaultValues, ...initialValues });
  }, [initialValues, defaultValues]);

  const handleChange = useCallback(
    (name: string, value: unknown, type: ParameterSchema['type']) => {
      const convertedValue = convertValue(value, type);
      const schema = parameters.find((p) => p.name === name);

      // Validate
      if (schema) {
        const error = validateParameter(convertedValue, schema);
        setInternalErrors((prev) => {
          if (error) {
            return { ...prev, [name]: error };
          }
          const { [name]: _removed, ...rest } = prev;
          void _removed; // Intentionally unused - destructuring to remove key
          return rest;
        });
      }

      setValues((prev) => {
        const newValues = { ...prev, [name]: convertedValue };
        onChange?.(newValues);
        return newValues;
      });
    },
    [parameters, onChange]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all parameters
    const validationErrors: Record<string, string> = {};
    parameters.forEach((param) => {
      const error = validateParameter(values[param.name], param);
      if (error) {
        validationErrors[param.name] = error;
      }
    });

    if (Object.keys(validationErrors).length > 0) {
      setInternalErrors(validationErrors);
      return;
    }

    onSubmit?.(values);
  };

  const handleReset = () => {
    setValues({ ...defaultValues, ...initialValues });
    setInternalErrors({});
    onChange?.({ ...defaultValues, ...initialValues });
  };

  if (parameters.length === 0) {
    return (
      <div className={`text-center py-4 text-zinc-500 ${className}`}>
        <Info className="w-5 h-5 mx-auto mb-2" />
        <p className="text-sm">No parameters defined</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={className}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-brand-400" />
          <h3 className="text-sm font-medium text-zinc-100">Parameters</h3>
        </div>

        {/* Parameter Fields */}
        <div className="space-y-3">
          {parameters.map((param) => (
            <div key={param.name} className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-zinc-300">
                  {param.displayName}
                  {param.unit && (
                    <span className="ml-1 text-zinc-500">({param.unit})</span>
                  )}
                </label>
                {param.description && (
                  <span
                    className="text-xs text-zinc-500 cursor-help"
                    title={param.description}
                  >
                    <Info className="w-3.5 h-3.5" />
                  </span>
                )}
              </div>

              {/* Render appropriate input based on type */}
              {param.type === 'boolean' ? (
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={Boolean(values[param.name])}
                    onChange={(e) =>
                      handleChange(param.name, e.target.checked, param.type)
                    }
                    disabled={readOnly}
                    className="w-4 h-4 rounded border-zinc-700 bg-zinc-800 text-brand-500 focus:ring-brand-500 focus:ring-offset-zinc-900"
                  />
                  <span className="ml-2 text-sm text-zinc-400">
                    {values[param.name] ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              ) : param.options && param.options.length > 0 ? (
                <Select
                  value={String(values[param.name] ?? '')}
                  onChange={(e) =>
                    handleChange(param.name, e.target.value, param.type)
                  }
                  disabled={readOnly}
                  className={allErrors[param.name] ? 'border-red-500' : ''}
                  placeholder="Select..."
                  options={param.options.map((option) => ({
                    value: option,
                    label: option,
                  }))}
                />
              ) : (
                <Input
                  type={param.type === 'float' || param.type === 'integer' ? 'number' : 'text'}
                  value={String(values[param.name] ?? '')}
                  onChange={(e) =>
                    handleChange(param.name, e.target.value, param.type)
                  }
                  disabled={readOnly}
                  placeholder={`Default: ${String(param.default)}`}
                  step={param.type === 'float' ? '0.01' : '1'}
                  min={param.min}
                  max={param.max}
                  className={allErrors[param.name] ? 'border-red-500' : ''}
                />
              )}

              {/* Error message */}
              {allErrors[param.name] && (
                <div className="flex items-center gap-1 text-xs text-red-400">
                  <AlertCircle className="w-3 h-3" />
                  {allErrors[param.name]}
                </div>
              )}

              {/* Range hint */}
              {(param.min !== undefined || param.max !== undefined) && !allErrors[param.name] && (
                <p className="text-xs text-zinc-500">
                  Range: {param.min ?? '-∞'} ~ {param.max ?? '∞'}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Actions */}
        {showSubmit && !readOnly && (
          <div className="flex items-center justify-end gap-2 pt-4 border-t border-zinc-800">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleReset}
            >
              Reset
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={Object.keys(allErrors).length > 0}
            >
              {submitText}
            </Button>
          </div>
        )}
      </div>
    </form>
  );
}
