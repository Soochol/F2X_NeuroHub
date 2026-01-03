/**
 * Report type selector tabs.
 */

import type { ReportType } from '../../../types';
import { REPORT_TYPE_INFO } from '../../../types';

interface ReportTypeSelectorProps {
  selectedType: ReportType;
  onSelect: (type: ReportType) => void;
}

const reportTypes: ReportType[] = ['batch_summary', 'period_stats', 'step_analysis'];

export function ReportTypeSelector({ selectedType, onSelect }: ReportTypeSelectorProps) {
  return (
    <div
      className="flex rounded-lg p-1"
      style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
    >
      {reportTypes.map((type) => {
        const info = REPORT_TYPE_INFO[type];
        const isSelected = selectedType === type;

        return (
          <button
            key={type}
            onClick={() => onSelect(type)}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              isSelected ? 'shadow-sm' : ''
            }`}
            style={{
              backgroundColor: isSelected ? 'var(--color-bg-elevated)' : 'transparent',
              color: isSelected ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
            }}
            title={info.description}
          >
            {info.label}
          </button>
        );
      })}
    </div>
  );
}
