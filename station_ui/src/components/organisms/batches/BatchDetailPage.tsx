/**
 * Enhanced Batch Detail Page component.
 * Shows complete batch information with sequence metadata, steps, parameters,
 * and execution statistics in a full-page layout.
 */

import { useState } from 'react';
import {
  X,
  Play,
  Square,
  Settings,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Edit3,
  Save,
} from 'lucide-react';
import { Button } from '../../atoms/Button';
import { StatusBadge } from '../../atoms/StatusBadge';
import { ProgressBar } from '../../atoms/ProgressBar';
import { LoadingSpinner } from '../../atoms/LoadingSpinner';
import { Input } from '../../atoms/Input';
import type {
  Batch,
  BatchDetail as BatchDetailType,
  HardwareStatus,
  StepResult,
  BatchStatistics,
  StepStatistics,
} from '../../../types';

// Type guard to check if batch is a BatchDetail
function isBatchDetail(batch: Batch | BatchDetailType): batch is BatchDetailType {
  return 'parameters' in batch && 'hardwareStatus' in batch;
}

export interface BatchDetailPageProps {
  batch: Batch | BatchDetailType | null;
  isLoading?: boolean;
  onClose: () => void;
  onStartSequence: (batchId: string, params?: Record<string, unknown>) => void;
  onStopSequence: (batchId: string) => void;
  onUpdateParameters?: (batchId: string, params: Record<string, unknown>) => void;
  isStarting?: boolean;
  isStopping?: boolean;
  statistics?: BatchStatistics;
  stepStatistics?: StepStatistics[];
}

export function BatchDetailPage({
  batch,
  isLoading,
  onClose,
  onStartSequence,
  onStopSequence,
  onUpdateParameters,
  isStarting,
  isStopping,
  statistics,
  stepStatistics,
}: BatchDetailPageProps) {
  const [isEditingParams, setIsEditingParams] = useState(false);
  const [editedParams, setEditedParams] = useState<Record<string, unknown>>({});
  const [expandedSections, setExpandedSections] = useState({
    sequence: true,
    execution: true,
    steps: true,
    parameters: true,
    hardware: false,
  });

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-zinc-900">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!batch) {
    return (
      <div className="h-full flex items-center justify-center bg-zinc-900">
        <p className="text-zinc-500">Select a batch to view details</p>
      </div>
    );
  }

  const isRunning = batch.status === 'running' || batch.status === 'starting';
  const canStart = batch.status === 'idle' || batch.status === 'completed' || batch.status === 'error';

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleEditParams = () => {
    if (isBatchDetail(batch)) {
      setEditedParams({ ...batch.parameters });
      setIsEditingParams(true);
    }
  };

  const handleSaveParams = () => {
    if (onUpdateParameters) {
      onUpdateParameters(batch.id, editedParams);
    }
    setIsEditingParams(false);
  };

  const handleParamChange = (key: string, value: unknown) => {
    setEditedParams((prev) => ({ ...prev, [key]: value }));
  };

  // Calculate overall statistics
  const totalStats = statistics || { total: 0, pass: 0, fail: 0, passRate: 0 };

  return (
    <div className="h-full flex flex-col bg-zinc-900 rounded-lg border border-zinc-700 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-zinc-700 bg-zinc-800">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-bold text-white">{batch.name}</h2>
          <StatusBadge status={batch.status} />
        </div>
        <div className="flex items-center gap-2">
          {canStart && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => onStartSequence(batch.id)}
              isLoading={isStarting}
            >
              <Play className="w-4 h-4 mr-1" />
              Start
            </Button>
          )}
          {isRunning && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => onStopSequence(batch.id)}
              isLoading={isStopping}
            >
              <Square className="w-4 h-4 mr-1" />
              Stop
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Statistics Summary Bar */}
      <div className="flex items-center gap-6 px-4 py-3 bg-zinc-800/50 border-b border-zinc-700">
        <StatItem
          icon={<CheckCircle className="w-4 h-4 text-green-500" />}
          label="Total"
          value={totalStats.total}
        />
        <StatItem
          icon={<CheckCircle className="w-4 h-4 text-green-500" />}
          label="Pass"
          value={totalStats.pass}
          color="text-green-500"
        />
        <StatItem
          icon={<XCircle className="w-4 h-4 text-red-500" />}
          label="Fail"
          value={totalStats.fail}
          color="text-red-500"
        />
        <StatItem
          icon={<AlertCircle className="w-4 h-4 text-brand-500" />}
          label="Pass Rate"
          value={`${(totalStats.passRate * 100).toFixed(1)}%`}
          color="text-brand-500"
        />
        {isBatchDetail(batch) && batch.execution && (
          <StatItem
            icon={<Clock className="w-4 h-4 text-zinc-400" />}
            label="Elapsed"
            value={`${batch.execution.elapsed.toFixed(1)}s`}
          />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Sequence Info Section */}
        <CollapsibleSection
          title="Sequence Information"
          icon={<Settings className="w-4 h-4" />}
          isExpanded={expandedSections.sequence}
          onToggle={() => toggleSection('sequence')}
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <InfoCard label="Name" value={batch.sequenceName || 'Not assigned'} />
            <InfoCard label="Version" value={batch.sequenceVersion || '-'} />
            <InfoCard label="Package" value={batch.sequencePackage || '-'} />
            <InfoCard label="Total Steps" value={batch.totalSteps.toString()} />
          </div>
        </CollapsibleSection>

        {/* Execution Status Section - only for BatchDetail */}
        {isBatchDetail(batch) && batch.execution && (
          <CollapsibleSection
            title="Current Execution"
            icon={<Play className="w-4 h-4" />}
            isExpanded={expandedSections.execution}
            onToggle={() => toggleSection('execution')}
          >
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <ProgressBar
                  value={batch.execution.progress * 100}
                  variant={batch.status === 'error' ? 'error' : 'default'}
                  className="flex-1"
                />
                <span className="text-sm font-medium text-white w-16 text-right">
                  {Math.round(batch.execution.progress * 100)}%
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <InfoCard label="Current Step" value={batch.execution.currentStep || 'Waiting'} />
                <InfoCard
                  label="Progress"
                  value={`${batch.execution.stepIndex + 1} / ${batch.execution.totalSteps}`}
                />
                <InfoCard label="Elapsed" value={`${batch.execution.elapsed.toFixed(1)}s`} />
                <InfoCard
                  label="Status"
                  value={batch.execution.status}
                  valueColor={
                    batch.execution.status === 'completed'
                      ? 'text-green-500'
                      : batch.execution.status === 'failed'
                        ? 'text-red-500'
                        : 'text-brand-500'
                  }
                />
              </div>
            </div>
          </CollapsibleSection>
        )}

        {/* Steps Table Section - only for BatchDetail */}
        {isBatchDetail(batch) && (
          <CollapsibleSection
            title="Step Results"
            icon={<CheckCircle className="w-4 h-4" />}
            isExpanded={expandedSections.steps}
            onToggle={() => toggleSection('steps')}
          >
            <StepsTable
              steps={batch.execution?.steps || []}
              stepStatistics={stepStatistics}
            />
          </CollapsibleSection>
        )}

        {/* Parameters Section - only show for BatchDetail */}
        {isBatchDetail(batch) && (
          <CollapsibleSection
            title="Parameters"
            icon={<Settings className="w-4 h-4" />}
            isExpanded={expandedSections.parameters}
            onToggle={() => toggleSection('parameters')}
            action={
              !isEditingParams && onUpdateParameters ? (
                <Button variant="ghost" size="sm" onClick={handleEditParams}>
                  <Edit3 className="w-3 h-3 mr-1" />
                  Edit
                </Button>
              ) : isEditingParams ? (
                <Button variant="primary" size="sm" onClick={handleSaveParams}>
                  <Save className="w-3 h-3 mr-1" />
                  Save
                </Button>
              ) : null
            }
          >
            {isEditingParams ? (
              <ParameterEditor
                parameters={editedParams}
                onChange={handleParamChange}
                onCancel={() => setIsEditingParams(false)}
              />
            ) : (
              <ParameterDisplay parameters={batch.parameters} />
            )}
          </CollapsibleSection>
        )}

        {/* Hardware Section - only show for BatchDetail */}
        {isBatchDetail(batch) && batch.hardwareStatus && Object.keys(batch.hardwareStatus).length > 0 && (
          <CollapsibleSection
            title="Hardware Status"
            icon={<Settings className="w-4 h-4" />}
            isExpanded={expandedSections.hardware}
            onToggle={() => toggleSection('hardware')}
          >
            <div className="space-y-2">
              {Object.entries(batch.hardwareStatus).map(([id, status]) => (
                <HardwareRow key={id} id={id} status={status as HardwareStatus} />
              ))}
            </div>
          </CollapsibleSection>
        )}
      </div>
    </div>
  );
}

// Sub-components

function StatItem({
  icon,
  label,
  value,
  color = 'text-white',
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-xs text-zinc-500">{label}:</span>
      <span className={`text-sm font-medium ${color}`}>{value}</span>
    </div>
  );
}

function InfoCard({
  label,
  value,
  valueColor = 'text-white',
}: {
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="p-3 bg-zinc-800 rounded-lg">
      <p className="text-xs text-zinc-500 mb-1">{label}</p>
      <p className={`text-sm font-medium ${valueColor} truncate`}>{value}</p>
    </div>
  );
}

function CollapsibleSection({
  title,
  icon,
  isExpanded,
  onToggle,
  children,
  action,
}: {
  title: string;
  icon: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="bg-zinc-800 rounded-lg border border-zinc-700">
      <button
        className="w-full flex items-center justify-between p-3 text-left hover:bg-zinc-700/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-medium text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {action && <div onClick={(e) => e.stopPropagation()}>{action}</div>}
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          )}
        </div>
      </button>
      {isExpanded && <div className="p-4 pt-0">{children}</div>}
    </div>
  );
}

function StepsTable({
  steps,
  stepStatistics,
}: {
  steps: StepResult[];
  stepStatistics?: StepStatistics[];
}) {
  if (steps.length === 0 && (!stepStatistics || stepStatistics.length === 0)) {
    return <p className="text-zinc-500 text-sm">No steps executed yet</p>;
  }

  // Merge steps with statistics
  const mergedSteps = steps.length > 0 ? steps : [];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-zinc-500 border-b border-zinc-700">
            <th className="pb-2 pr-4">#</th>
            <th className="pb-2 pr-4">Step Name</th>
            <th className="pb-2 pr-4">Status</th>
            <th className="pb-2 pr-4">Pass/Fail</th>
            <th className="pb-2 pr-4">Duration</th>
            <th className="pb-2 pr-4">Result Data</th>
            {stepStatistics && <th className="pb-2 pr-4">Stats (P/F)</th>}
          </tr>
        </thead>
        <tbody>
          {mergedSteps.map((step) => {
            const stats = stepStatistics?.find((s) => s.name === step.name);
            return (
              <tr
                key={`step-${step.order}-${step.name}`}
                className={`border-b border-zinc-700/50 ${
                  step.status === 'running'
                    ? 'bg-brand-500/10'
                    : step.status === 'failed'
                      ? 'bg-red-500/10'
                      : ''
                }`}
              >
                <td className="py-2 pr-4 text-zinc-400">{step.order}</td>
                <td className="py-2 pr-4 text-white">{step.name}</td>
                <td className="py-2 pr-4">
                  <StatusBadge
                    status={
                      step.status === 'completed'
                        ? 'completed'
                        : step.status === 'running'
                          ? 'running'
                          : step.status === 'failed'
                            ? 'error'
                            : 'idle'
                    }
                    size="sm"
                  />
                </td>
                <td className="py-2 pr-4">
                  {step.status !== 'pending' && (
                    <span
                      className={`font-medium ${step.pass ? 'text-green-500' : 'text-red-500'}`}
                    >
                      {step.pass ? 'PASS' : 'FAIL'}
                    </span>
                  )}
                </td>
                <td className="py-2 pr-4 text-zinc-400">
                  {step.duration !== undefined ? `${step.duration.toFixed(2)}s` : '-'}
                </td>
                <td className="py-2 pr-4 text-zinc-400 max-w-xs truncate">
                  {step.result ? JSON.stringify(step.result) : '-'}
                </td>
                {stepStatistics && (
                  <td className="py-2 pr-4">
                    {stats && (
                      <span className="text-xs">
                        <span className="text-green-500">{stats.pass}</span>
                        <span className="text-zinc-500">/</span>
                        <span className="text-red-500">{stats.fail}</span>
                      </span>
                    )}
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function ParameterDisplay({ parameters }: { parameters: Record<string, unknown> }) {
  if (Object.keys(parameters).length === 0) {
    return <p className="text-zinc-500 text-sm">No parameters configured</p>;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {Object.entries(parameters).map(([key, value]) => (
        <div key={key} className="p-2 bg-zinc-900 rounded">
          <p className="text-xs text-zinc-500">{key}</p>
          <p className="text-sm text-white font-mono">{String(value)}</p>
        </div>
      ))}
    </div>
  );
}

function ParameterEditor({
  parameters,
  onChange,
  onCancel,
}: {
  parameters: Record<string, unknown>;
  onChange: (key: string, value: unknown) => void;
  onCancel: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(parameters).map(([key, value]) => (
          <div key={key}>
            <label className="text-xs text-zinc-500 block mb-1">{key}</label>
            <Input
              value={String(value)}
              onChange={(e) => {
                const newValue = e.target.value;
                // Try to parse as number if original was number
                if (typeof value === 'number') {
                  const num = parseFloat(newValue);
                  onChange(key, isNaN(num) ? newValue : num);
                } else if (typeof value === 'boolean') {
                  onChange(key, newValue === 'true');
                } else {
                  onChange(key, newValue);
                }
              }}
              className="font-mono text-sm"
            />
          </div>
        ))}
      </div>
      <div className="flex justify-end">
        <Button variant="ghost" size="sm" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  );
}

function HardwareRow({ id, status }: { id: string; status: HardwareStatus }) {
  return (
    <div className="flex items-center justify-between p-3 bg-zinc-900 rounded-lg">
      <div>
        <span className="text-white font-medium">{id}</span>
        <span className="ml-2 text-xs text-zinc-500">{status.driver}</span>
      </div>
      <StatusBadge
        status={status.status === 'connected' ? 'connected' : 'disconnected'}
        size="sm"
      />
    </div>
  );
}
