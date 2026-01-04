/**
 * Export dropdown button component for reports.
 */

import { useState, useRef, useEffect } from 'react';
import { Download, ChevronDown, FileSpreadsheet, FileText, Loader2 } from 'lucide-react';
import { Button } from '../../atoms/Button';
import type { ExportFormat } from '../../../types';

interface ExportOption {
  format: ExportFormat;
  label: string;
  icon: React.ReactNode;
}

const exportOptions: ExportOption[] = [
  { format: 'xlsx', label: 'Excel (.xlsx)', icon: <FileSpreadsheet className="w-4 h-4" /> },
  { format: 'pdf', label: 'PDF (.pdf)', icon: <FileText className="w-4 h-4" /> },
  { format: 'csv', label: 'CSV (.csv)', icon: <FileSpreadsheet className="w-4 h-4" /> },
  { format: 'json', label: 'JSON (.json)', icon: <FileText className="w-4 h-4" /> },
];

interface ExportButtonProps {
  onExport: (format: ExportFormat) => void;
  isLoading?: boolean;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function ExportButton({ onExport, isLoading, disabled, size = 'sm' }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = (format: ExportFormat) => {
    onExport(format);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="secondary"
        size={size}
        disabled={disabled || isLoading}
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        Export
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg border z-50"
          style={{
            backgroundColor: 'var(--color-bg-elevated)',
            borderColor: 'var(--color-border-default)',
          }}
        >
          <div className="py-1">
            {exportOptions.map((option) => (
              <button
                key={option.format}
                onClick={() => handleExport(option.format)}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors"
                style={{ color: 'var(--color-text-primary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-bg-tertiary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                {option.icon}
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
