/**
 * Measurement Form Component
 *
 * Dynamic form for entering process-specific measurement data
 */
import { useState, useEffect } from 'react';
import { ClipboardList, Save } from 'lucide-react';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import type { Process } from '@/types';

// Process-specific measurement fields configuration
interface MeasurementField {
  key: string;
  label: string;
  type: 'number' | 'text' | 'select';
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
  options?: { value: string; label: string }[];
  required?: boolean;
  placeholder?: string;
}

// Measurement configurations are now handled via defect_items and specific process types
const processConfigs: Record<number, MeasurementField[]> = {};

// Default fields for unknown processes
const defaultFields: MeasurementField[] = [
  { key: 'notes', label: '비고', type: 'text', placeholder: '측정 메모 입력' },
];

interface MeasurementFormProps {
  process: Process | null;
  result: 'PASS' | 'FAIL' | 'REWORK';
  onSubmit: (data: { measurements: Record<string, unknown>, defects?: string[], notes?: string }) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const MeasurementForm: React.FC<MeasurementFormProps> = ({
  process,
  result,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [values, setValues] = useState<Record<string, string | number>>({});
  const [selectedDefects, setSelectedDefects] = useState<string[]>([]);
  const [notes, setNotes] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Get fields for current process
  const fields = process
    ? processConfigs[process.process_number] || defaultFields
    : defaultFields;

  // Reset form when process changes
  useEffect(() => {
    setValues({});
    setSelectedDefects([]);
    setNotes('');
    setErrors({});
  }, [process?.id]);

  // Update field value
  const handleChange = (key: string, value: string | number) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    // Clear error on change
    if (errors[key]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  };

  // Validate and submit
  const handleSubmit = () => {
    const newErrors: Record<string, string> = {};

    // Check required fields
    fields.forEach((field) => {
      if (field.required && !values[field.key] && values[field.key] !== 0) {
        newErrors[field.key] = 'This field is required';
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Convert to proper types and submit
    const measurements: Record<string, unknown> = {};
    fields.forEach((field) => {
      const value = values[field.key];
      if (value !== undefined && value !== '') {
        if (field.type === 'number') {
          measurements[field.key] = Number(value);
        } else {
          measurements[field.key] = value;
        }
      }
    });

    if (result === 'FAIL' && selectedDefects.length === 0 && (!notes || !notes.trim())) {
      setErrors({ ...newErrors, _defects: 'Please select at least one defect item or enter a notes.' });
      return;
    }

    onSubmit({
      measurements,
      defects: result === 'FAIL' ? selectedDefects : undefined,
      notes: notes.trim() || undefined
    });
  };

  const toggleDefect = (defect: string) => {
    setSelectedDefects(prev =>
      prev.includes(defect)
        ? prev.filter(d => d !== defect)
        : [...prev, defect]
    );
    if (errors._defects) {
      setErrors(prev => {
        const next = { ...prev };
        delete next._defects;
        return next;
      });
    }
  };

  // Render field input
  const renderField = (field: MeasurementField) => {
    const value = values[field.key] ?? '';
    const error = errors[field.key];

    // Create label with unit info
    const labelContent = (
      <span className="flex items-baseline gap-1">
        <span>{field.label}</span>
        {field.required && <span className="text-danger-500">*</span>}
        {field.unit && (
          <span className="text-xs text-muted">({field.unit})</span>
        )}
      </span>
    );

    if (field.type === 'select') {
      const options = [
        { value: '', label: 'Select an option' },
        ...(field.options || []),
      ];
      return (
        <Select
          key={field.key}
          label={labelContent}
          value={String(value)}
          onChange={(e) => handleChange(field.key, e.target.value)}
          options={options}
          error={error}
          disabled={isLoading}
        />
      );
    }

    return (
      <Input
        key={field.key}
        type={field.type}
        label={<span className="text-[11px] font-black text-muted uppercase tracking-widest">{labelContent}</span>}
        value={value}
        onChange={(e) => handleChange(field.key, e.target.value)}
        placeholder={field.placeholder}
        min={field.min}
        max={field.max}
        step={field.step}
        error={error}
        disabled={isLoading}
      />
    );
  };

  return (
    <Card variant="glass" className="border-main shadow-none bg-surface">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center border border-primary-500/30">
            <ClipboardList className="w-5 h-5 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-black text-dynamic tracking-tight">
              {result === 'FAIL' ? 'Defect Report' : 'Measurement Data'}
            </h3>
            {process && (
              <p className="text-[10px] font-bold text-primary-400 uppercase tracking-widest mt-0.5">
                Process {process.process_number}: {process.process_name_en}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Form fields - Only show for PASS/REWORK */}
      {result !== 'FAIL' && (
        <div className="space-y-6 mb-8">
          {fields.map(renderField)}
        </div>
      )}

      {/* Defect Selection UI (Only for FAIL) */}
      {result === 'FAIL' && (
        <div className="mb-8 p-6 bg-danger-500/5 rounded-3xl border border-danger-500/20">
          <h4 className="text-sm font-black text-danger-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-danger-500" />
            Defect Selection
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
            {process?.defect_items && process.defect_items.length > 0 ? (
              process.defect_items.map((defect) => (
                <label
                  key={defect}
                  className={`flex items-center gap-3 p-4 rounded-2xl cursor-pointer border-2 transition-all ${selectedDefects.includes(defect)
                    ? 'bg-danger-500/10 border-danger-500/40 text-dynamic'
                    : 'bg-sub border-main text-muted hover:bg-sub/80'
                    }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedDefects.includes(defect)}
                    onChange={() => toggleDefect(defect)}
                    className="hidden"
                  />
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center border-2 transition-all ${selectedDefects.includes(defect) ? 'bg-danger-500 border-danger-500' : 'border-neutral-700'
                    }`}>
                    {selectedDefects.includes(defect) && <Save className="w-3.5 h-3.5 text-white" />}
                  </div>
                  <span className="font-bold text-base">{defect}</span>
                </label>
              ))
            ) : (
              <p className="text-xs text-muted italic col-span-2 py-2">No pre-defined defect items found. Please enter a reason below.</p>
            )}
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-black text-muted uppercase tracking-widest block ml-1">Defect Reason & Notes (Optional)</span>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Enter detailed reason for failure..."
              className="w-full min-h-[100px] bg-sub border border-main rounded-2xl p-4 text-dynamic placeholder:text-dim focus:outline-none focus:border-primary-500/50 transition-all font-medium"
            />
          </div>

          {errors._defects && (
            <p className="mt-3 text-xs font-bold text-danger-400 animate-pulse">{errors._defects}</p>
          )}
        </div>
      )}

      {/* Buttons */}
      <div className="flex gap-4">
        <Button
          variant="ghost"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 py-6 rounded-2xl border border-dynamic opacity-70 hover:opacity-100 transition-all font-bold"
        >
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isLoading}
          isLoading={isLoading}
          className="flex-[2] py-6 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-400 shadow-[0_8px_20px_rgba(30,58,95,0.3)] font-black"
        >
          <Save className="w-5 h-5 mr-1" />
          {result === 'FAIL' ? 'Report Failure' : 'Save & Finish'}
        </Button>
      </div>
    </Card>
  );
};
