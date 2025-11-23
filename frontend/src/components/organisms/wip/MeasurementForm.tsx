/**
 * Measurement Form Component
 *
 * Dynamic form for recording process-specific measurements and defects:
 * - Input fields for measurements
 * - Pass/Fail/Rework result selection
 * - Defect code selection (if failed)
 * - Notes/comments
 * - Form validation
 */

import { useState, type FormEvent } from 'react';
import { Input, Select, Button, Card } from '@/components/common';
import { ProcessResult, DataLevel, type Process } from '@/types/api';

interface MeasurementData {
  result: ProcessResult;
  data_level: DataLevel;
  measurements: Record<string, any>;
  defect_codes: string[];
  notes: string;
}

interface MeasurementFormProps {
  process: Process;
  onSubmit: (data: MeasurementData) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
  measurementFields?: Array<{
    key: string;
    label: string;
    type: 'number' | 'text' | 'select';
    options?: string[];
    required?: boolean;
    unit?: string;
  }>;
}

const COMMON_DEFECT_CODES = [
  { value: 'DEF001', label: 'Scratch' },
  { value: 'DEF002', label: 'Dent' },
  { value: 'DEF003', label: 'Crack' },
  { value: 'DEF004', label: 'Missing Part' },
  { value: 'DEF005', label: 'Wrong Part' },
  { value: 'DEF006', label: 'Misalignment' },
  { value: 'DEF007', label: 'Contamination' },
  { value: 'DEF008', label: 'Dimensional Error' },
  { value: 'DEF009', label: 'Surface Defect' },
  { value: 'DEF010', label: 'Other' },
];

export const MeasurementForm: React.FC<MeasurementFormProps> = ({
  process,
  onSubmit,
  onCancel,
  isSubmitting = false,
  measurementFields = [],
}) => {
  const [result, setResult] = useState<ProcessResult>(ProcessResult.PASS);
  const [dataLevel, setDataLevel] = useState<DataLevel>(DataLevel.NORMAL);
  const [measurements, setMeasurements] = useState<Record<string, any>>({});
  const [defectCodes, setDefectCodes] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleMeasurementChange = (key: string, value: any) => {
    setMeasurements((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const handleDefectCodeToggle = (code: string) => {
    setDefectCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate required measurement fields
    measurementFields.forEach((field) => {
      if (field.required && !measurements[field.key]) {
        newErrors[field.key] = `${field.label} is required`;
      }
    });

    // Validate defect codes for FAIL result
    if (result === ProcessResult.FAIL && defectCodes.length === 0) {
      newErrors.defectCodes = 'At least one defect code must be selected for FAIL result';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    onSubmit({
      result,
      data_level: dataLevel,
      measurements,
      defect_codes: defectCodes,
      notes,
    });
  };

  return (
    <Card>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-4)' }}>
          {/* Header */}
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: 'var(--spacing-1)' }}>
              Process: {process.process_name_ko}
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
              {process.process_name_en} (Process #{process.process_number})
            </p>
          </div>

          {/* Result Selection */}
          <Select
            label="Result"
            value={result}
            onChange={(e) => setResult(e.target.value as ProcessResult)}
            options={[
              { value: ProcessResult.PASS, label: 'PASS' },
              { value: ProcessResult.FAIL, label: 'FAIL' },
              { value: ProcessResult.REWORK, label: 'REWORK' },
            ]}
            required
          />

          {/* Data Level */}
          <Select
            label="Data Level"
            value={dataLevel}
            onChange={(e) => setDataLevel(e.target.value as DataLevel)}
            options={[
              { value: DataLevel.NORMAL, label: 'Normal' },
              { value: DataLevel.DETAILED, label: 'Detailed' },
            ]}
          />

          {/* Dynamic Measurement Fields */}
          {measurementFields.length > 0 && (
            <div
              style={{
                padding: 'var(--spacing-3)',
                backgroundColor: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-base)',
                border: '1px solid var(--color-border-subtle)',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: 'var(--spacing-3)' }}>
                Measurements
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
                {measurementFields.map((field) => {
                  if (field.type === 'select' && field.options) {
                    return (
                      <Select
                        key={field.key}
                        label={field.label}
                        value={measurements[field.key] || ''}
                        onChange={(e) => handleMeasurementChange(field.key, e.target.value)}
                        options={field.options.map((opt) => ({ value: opt, label: opt }))}
                        required={field.required}
                        error={errors[field.key]}
                      />
                    );
                  }

                  return (
                    <Input
                      key={field.key}
                      label={`${field.label}${field.unit ? ` (${field.unit})` : ''}`}
                      type={field.type}
                      value={measurements[field.key] || ''}
                      onChange={(e) =>
                        handleMeasurementChange(
                          field.key,
                          field.type === 'number' ? parseFloat(e.target.value) : e.target.value
                        )
                      }
                      required={field.required}
                      error={errors[field.key]}
                      placeholder={`Enter ${field.label.toLowerCase()}`}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {/* Defect Codes (only for FAIL result) */}
          {result === ProcessResult.FAIL && (
            <div
              style={{
                padding: 'var(--spacing-3)',
                backgroundColor: 'var(--color-error-bg, rgba(245, 101, 101, 0.1))',
                borderRadius: 'var(--radius-base)',
                border: '1px solid var(--color-error)',
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: 'var(--spacing-2)' }}>
                Defect Codes *
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
                  gap: 'var(--spacing-2)',
                }}
              >
                {COMMON_DEFECT_CODES.map((defect) => (
                  <label
                    key={defect.value}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-2)',
                      padding: 'var(--spacing-2)',
                      backgroundColor: defectCodes.includes(defect.value)
                        ? 'var(--color-error)'
                        : 'var(--color-bg-primary)',
                      borderRadius: 'var(--radius-base)',
                      border: '1px solid var(--color-border-default)',
                      cursor: 'pointer',
                      fontSize: '13px',
                      transition: 'all var(--transition-fast)',
                      color: defectCodes.includes(defect.value)
                        ? 'white'
                        : 'var(--color-text-primary)',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={defectCodes.includes(defect.value)}
                      onChange={() => handleDefectCodeToggle(defect.value)}
                      style={{ cursor: 'pointer' }}
                    />
                    <span>{defect.label}</span>
                  </label>
                ))}
              </div>
              {errors.defectCodes && (
                <div
                  style={{
                    color: 'var(--color-error)',
                    fontSize: '12px',
                    marginTop: 'var(--spacing-2)',
                  }}
                >
                  {errors.defectCodes}
                </div>
              )}
            </div>
          )}

          {/* Notes */}
          <div>
            <label
              style={{
                display: 'block',
                marginBottom: 'var(--spacing-1)',
                fontWeight: '500',
                fontSize: '14px',
              }}
            >
              Notes / Comments
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any additional notes or observations..."
              rows={4}
              style={{
                width: '100%',
                padding: 'var(--spacing-2)',
                backgroundColor: 'var(--color-input-bg)',
                border: '1px solid var(--color-input-border)',
                borderRadius: 'var(--radius-base)',
                fontSize: '14px',
                color: 'var(--color-text-primary)',
                resize: 'vertical',
                fontFamily: 'inherit',
              }}
            />
          </div>

          {/* Actions */}
          <div
            style={{
              display: 'flex',
              gap: 'var(--spacing-2)',
              justifyContent: 'flex-end',
              paddingTop: 'var(--spacing-3)',
              borderTop: '1px solid var(--color-border-default)',
            }}
          >
            {onCancel && (
              <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              isLoading={isSubmitting}
              disabled={isSubmitting}
              variant={result === ProcessResult.FAIL ? 'danger' : 'primary'}
            >
              {result === ProcessResult.PASS ? 'Submit PASS' : result === ProcessResult.FAIL ? 'Submit FAIL' : 'Submit REWORK'}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
};
