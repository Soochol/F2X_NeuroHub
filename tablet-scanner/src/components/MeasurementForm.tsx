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

// Measurement configurations per process number
const processConfigs: Record<number, MeasurementField[]> = {
  // 1. 레이저 마킹
  1: [
    { key: 'marking_quality', label: '마킹 품질', type: 'select', options: [
      { value: 'good', label: '양호' },
      { value: 'acceptable', label: '허용' },
      { value: 'poor', label: '불량' },
    ], required: true },
    { key: 'laser_power', label: '레이저 출력', type: 'number', unit: 'W', min: 0, max: 100, step: 0.1 },
  ],
  // 2. LMA 조립
  2: [
    { key: 'assembly_torque', label: '조립 토크', type: 'number', unit: 'N·m', min: 0, max: 10, step: 0.01, required: true },
    { key: 'alignment_check', label: '정렬 상태', type: 'select', options: [
      { value: 'pass', label: '합격' },
      { value: 'adjusted', label: '조정 후 합격' },
      { value: 'fail', label: '불합격' },
    ] },
    { key: 'busbar_lot', label: 'Busbar LOT', type: 'text', placeholder: 'LOT 번호 입력' },
  ],
  // 3. 센서 검사
  3: [
    { key: 'sensitivity', label: '감도', type: 'number', unit: 'mV/Pa', min: 0, max: 1000, step: 0.1, required: true },
    { key: 'noise_level', label: '노이즈 레벨', type: 'number', unit: 'dB', min: -100, max: 0, step: 0.1, required: true },
    { key: 'frequency_response', label: '주파수 응답', type: 'number', unit: 'Hz', min: 0, max: 20000, step: 1 },
  ],
  // 4. 펌웨어 업로드
  4: [
    { key: 'firmware_version', label: '펌웨어 버전', type: 'text', required: true, placeholder: 'v1.0.0' },
    { key: 'upload_time', label: '업로드 시간', type: 'number', unit: '초', min: 0, max: 300, step: 1 },
    { key: 'verification', label: '검증 상태', type: 'select', options: [
      { value: 'verified', label: '검증 완료' },
      { value: 'warning', label: '경고 있음' },
      { value: 'failed', label: '검증 실패' },
    ], required: true },
  ],
  // 5. 로봇 조립
  5: [
    { key: 'robot_id', label: '로봇 ID', type: 'text', required: true },
    { key: 'positioning_error', label: '위치 오차', type: 'number', unit: 'mm', min: 0, max: 1, step: 0.001 },
    { key: 'cycle_time', label: '사이클 타임', type: 'number', unit: '초', min: 0, max: 60, step: 0.1 },
  ],
  // 6. 성능 검사
  6: [
    { key: 'output_power', label: '출력', type: 'number', unit: 'mW', min: 0, max: 1000, step: 0.1, required: true },
    { key: 'efficiency', label: '효율', type: 'number', unit: '%', min: 0, max: 100, step: 0.1, required: true },
    { key: 'temperature', label: '온도', type: 'number', unit: '°C', min: -20, max: 80, step: 0.1 },
    { key: 'humidity', label: '습도', type: 'number', unit: '%', min: 0, max: 100, step: 0.1 },
  ],
  // 7. 라벨 프린팅
  7: [
    { key: 'label_quality', label: '라벨 품질', type: 'select', options: [
      { value: 'excellent', label: '우수' },
      { value: 'good', label: '양호' },
      { value: 'acceptable', label: '허용' },
    ], required: true },
    { key: 'barcode_readable', label: '바코드 판독', type: 'select', options: [
      { value: 'yes', label: '판독 가능' },
      { value: 'no', label: '판독 불가' },
    ], required: true },
  ],
  // 8. 포장+외관검사
  8: [
    { key: 'visual_inspection', label: '외관 검사', type: 'select', options: [
      { value: 'pass', label: '합격' },
      { value: 'minor_defect', label: '경미한 결함' },
      { value: 'fail', label: '불합격' },
    ], required: true },
    { key: 'package_integrity', label: '포장 상태', type: 'select', options: [
      { value: 'intact', label: '완전' },
      { value: 'damaged', label: '손상' },
    ], required: true },
    { key: 'weight', label: '중량', type: 'number', unit: 'g', min: 0, max: 1000, step: 0.1 },
  ],
};

// Default fields for unknown processes
const defaultFields: MeasurementField[] = [
  { key: 'notes', label: '비고', type: 'text', placeholder: '측정 메모 입력' },
];

interface MeasurementFormProps {
  process: Process | null;
  onSubmit: (measurements: Record<string, unknown>) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export const MeasurementForm: React.FC<MeasurementFormProps> = ({
  process,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [values, setValues] = useState<Record<string, string | number>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Get fields for current process
  const fields = process
    ? processConfigs[process.process_number] || defaultFields
    : defaultFields;

  // Reset form when process changes
  useEffect(() => {
    setValues({});
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
        newErrors[field.key] = '필수 입력 항목입니다';
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

    onSubmit(measurements);
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
          <span className="text-xs text-neutral-400">({field.unit})</span>
        )}
      </span>
    );

    if (field.type === 'select') {
      const options = [
        { value: '', label: '선택하세요' },
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
        label={labelContent}
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
    <Card>
      {/* Header */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-1">
          <ClipboardList className="w-5 h-5 text-primary-500" />
          <h3 className="text-lg font-semibold text-neutral-800">
            측정값 입력
          </h3>
        </div>
        {process && (
          <p className="text-sm text-neutral-500">
            공정 {process.process_number}: {process.process_name_ko}
          </p>
        )}
      </div>

      {/* Form fields */}
      <div className="space-y-4 mb-6">
        {fields.map(renderField)}
      </div>

      {/* Buttons */}
      <div className="flex gap-3">
        <Button
          variant="ghost"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1"
        >
          취소
        </Button>
        <Button
          variant="primary"
          onClick={handleSubmit}
          disabled={isLoading}
          isLoading={isLoading}
          className="flex-[2]"
        >
          <Save className="w-4 h-4" />
          저장
        </Button>
      </div>
    </Card>
  );
};
