/**
 * StepDataViewer - Display step measurement data and results.
 */

import { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Database,
  Copy,
  Check,
} from 'lucide-react';
import { useDebugPanelStore } from '../../../stores/debugPanelStore';
import { StatusBadge } from '../../atoms/StatusBadge';
import type { StepResult } from '../../../types';

interface StepDataViewerProps {
  /** Step results to display */
  steps: StepResult[];
}

interface StepRowProps {
  step: StepResult;
  isSelected: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  onClick: () => void;
}

function StepRow({ step, isSelected, isExpanded, onToggle, onClick }: StepRowProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (step.result) {
      await navigator.clipboard.writeText(JSON.stringify(step.result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const hasData = step.result && Object.keys(step.result).length > 0;
  const hasError = !!step.error;

  return (
    <div
      className={`border-b transition-colors ${isSelected ? 'bg-brand-500/10' : ''}`}
      style={{ borderColor: 'var(--color-border-subtle)' }}
    >
      {/* Step header */}
      <div
        onClick={() => {
          onClick();
          if (hasData || hasError) onToggle();
        }}
        className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800/50 ${
          hasData || hasError ? '' : 'opacity-60'
        }`}
      >
        {/* Expand/collapse icon */}
        <div className="w-4 h-4 flex items-center justify-center">
          {(hasData || hasError) &&
            (isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5" style={{ color: 'var(--color-text-tertiary)' }} />
            ) : (
              <ChevronRight className="w-3.5 h-3.5" style={{ color: 'var(--color-text-tertiary)' }} />
            ))}
        </div>

        {/* Step order */}
        <span
          className="w-5 text-center text-xs font-mono"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          {step.order}
        </span>

        {/* Step name */}
        <span className="flex-1 text-xs font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
          {step.name}
        </span>

        {/* Status and result */}
        <div className="flex items-center gap-2">
          {step.duration != null && (
            <span
              className="flex items-center gap-0.5 text-[10px] font-mono"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              <Clock className="w-3 h-3" />
              {step.duration.toFixed(2)}s
            </span>
          )}

          {step.status === 'completed' && (
            <span className={step.pass ? 'text-green-500' : 'text-red-500'}>
              {step.pass ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
            </span>
          )}

          {step.status === 'running' && <StatusBadge status="running" size="sm" />}

          {step.status === 'failed' && <XCircle className="w-3.5 h-3.5 text-red-500" />}

          {hasData && (
            <span title="Has data">
              <Database className="w-3 h-3" style={{ color: 'var(--color-text-tertiary)' }} />
            </span>
          )}

          {/* Copy button - always visible when has data */}
          {hasData && (
            <button
              onClick={handleCopy}
              className="p-1 rounded hover:bg-zinc-700 transition-colors"
              title="Copy step data to clipboard"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5" style={{ color: 'var(--color-text-tertiary)' }} />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (hasData || hasError) && (
        <div className="px-2 py-2 ml-6" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          {/* Error message */}
          {hasError && (
            <div className="mb-2 p-2 rounded bg-red-500/10 border border-red-500/30">
              <div className="flex items-center gap-1 text-xs text-red-400 mb-1">
                <AlertCircle className="w-3 h-3" />
                <span className="font-medium">Error</span>
              </div>
              <p className="text-xs text-red-300 font-mono break-all">{step.error}</p>
            </div>
          )}

          {/* Result data */}
          {hasData && (
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-medium" style={{ color: 'var(--color-text-tertiary)' }}>
                  Measurements
                </span>
                <button
                  onClick={handleCopy}
                  className="p-1 rounded hover:bg-zinc-700 transition-colors"
                  title="Copy JSON"
                >
                  {copied ? (
                    <Check className="w-3 h-3 text-green-500" />
                  ) : (
                    <Copy className="w-3 h-3" style={{ color: 'var(--color-text-tertiary)' }} />
                  )}
                </button>
              </div>
              <div className="space-y-0.5">
                {Object.entries(step.result || {}).map(([key, value]) => (
                  <div key={key} className="flex items-start gap-2 text-[11px] font-mono">
                    <span className="text-brand-400 flex-shrink-0">{key}:</span>
                    <span className="text-zinc-300 break-all">{formatValue(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  if (typeof value === 'number') {
    // Format numbers with appropriate precision
    if (Number.isInteger(value)) return value.toString();
    return value.toFixed(4);
  }
  return String(value);
}

export function StepDataViewer({ steps }: StepDataViewerProps) {
  const { selectedStep, setSelectedStep } = useDebugPanelStore();
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleExpanded = (stepName: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepName)) {
        next.delete(stepName);
      } else {
        next.add(stepName);
      }
      return next;
    });
  };

  if (steps.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center py-8"
        style={{ color: 'var(--color-text-tertiary)' }}
      >
        <Database className="w-6 h-6 mb-2 opacity-50" />
        <p className="text-xs">No step data available</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {steps.map((step) => (
        <StepRow
          key={`${step.order}-${step.name}`}
          step={step}
          isSelected={selectedStep === step.name}
          isExpanded={expandedSteps.has(step.name)}
          onToggle={() => toggleExpanded(step.name)}
          onClick={() => setSelectedStep(selectedStep === step.name ? null : step.name)}
        />
      ))}
    </div>
  );
}
