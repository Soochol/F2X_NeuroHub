/**
 * Enhanced Manual Control Page
 *
 * Features:
 * - Smart command discovery with category tabs
 * - Type-aware parameter inputs
 * - Result visualization with history
 * - Manual sequence step-by-step execution
 */

import { useState, useMemo } from 'react';
import {
  Wrench,
  AlertTriangle,
  Send,
  History,
  Cpu,
  Play,
  SkipForward,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Gauge,
  Settings,
  Zap,
  Search,
  ListOrdered,
  CheckCircle,
  XCircle,
  Clock,
  FastForward,
} from 'lucide-react';
import {
  useBatchList,
  useBatch,
  useHardwareCommands,
  useExecuteCommand,
  useManualSteps,
  useRunManualStep,
  useSkipManualStep,
  useResetManualSequence,
} from '../hooks';
import { useManualControlStore, selectGroupedCommands } from '../stores/manualControlStore';
import { Button } from '../components/atoms/Button';
import { Input } from '../components/atoms/Input';
import { Select } from '../components/atoms/Select';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { cn } from '../utils';
import type {
  CommandInfo,
  CommandParameter,
  ManualStepInfo,
  HardwareStatus,
  BatchDetail,
} from '../types';

// Type guard to check if data is a BatchDetail
function isBatchDetail(data: unknown): data is BatchDetail {
  return data !== null && typeof data === 'object' && 'hardwareStatus' in data;
}

const CATEGORY_ICONS = {
  measurement: Gauge,
  control: Zap,
  configuration: Settings,
  diagnostic: Search,
};

const CATEGORY_LABELS = {
  measurement: 'Measurement',
  control: 'Control',
  configuration: 'Configuration',
  diagnostic: 'Diagnostic',
};

export function ManualControlPage() {
  const { data: batches, isLoading } = useBatchList();
  const [activeTab, setActiveTab] = useState<'commands' | 'sequence'>('commands');

  // Store state
  const selectedBatchId = useManualControlStore((s) => s.selectedBatchId);
  const selectedHardwareId = useManualControlStore((s) => s.selectedHardwareId);
  const selectDevice = useManualControlStore((s) => s.selectDevice);
  const selectedCommand = useManualControlStore((s) => s.selectedCommand);
  const selectCommand = useManualControlStore((s) => s.selectCommand);
  const parameterValues = useManualControlStore((s) => s.parameterValues);
  const setParameterValue = useManualControlStore((s) => s.setParameterValue);
  const resultHistory = useManualControlStore((s) => s.resultHistory);

  // Fetch batch detail
  const { data: batchDetail } = useBatch(selectedBatchId);

  // Fetch hardware commands
  const { data: commandsData, isLoading: loadingCommands } = useHardwareCommands(
    selectedBatchId,
    selectedHardwareId
  );

  // Execute command mutation
  const executeCommand = useExecuteCommand();

  // Group commands by category
  const groupedCommands = useMemo(() => {
    if (!commandsData?.commands) return {};
    return selectGroupedCommands(commandsData.commands);
  }, [commandsData]);

  // Batch options (only idle batches for manual control)
  const batchOptions = useMemo(() => {
    return (
      batches
        ?.filter((b) => b.status === 'idle')
        .map((b) => ({
          value: b.id,
          label: `${b.name} - ${b.sequenceName ?? 'No sequence'}`,
        })) ?? []
    );
  }, [batches]);

  // Hardware options from batch detail
  const hardwareOptions = useMemo(() => {
    if (!isBatchDetail(batchDetail) || !batchDetail.hardwareStatus) return [];
    return Object.entries(batchDetail.hardwareStatus).map(([id, status]) => ({
      value: id,
      label: `${id} (${(status as HardwareStatus).driver})`,
    }));
  }, [batchDetail]);

  const handleExecute = async () => {
    if (!selectedBatchId || !selectedHardwareId || !selectedCommand) return;

    await executeCommand.mutateAsync({
      batchId: selectedBatchId,
      request: {
        hardware: selectedHardwareId,
        command: selectedCommand.name,
        params: parameterValues,
      },
      command: selectedCommand,
    });
  };

  if (isLoading) {
    return <LoadingOverlay message="Loading batches..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Wrench className="w-6 h-6 text-brand-500" />
          <h2
            className="text-2xl font-bold"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Manual Control
          </h2>
        </div>

        {/* Tab Toggle */}
        <div className="flex gap-2 p-1 rounded-lg" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          <button
            onClick={() => setActiveTab('commands')}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium transition-all',
              activeTab === 'commands'
                ? 'bg-brand-500 text-white'
                : 'hover:bg-brand-500/20'
            )}
            style={activeTab !== 'commands' ? { color: 'var(--color-text-secondary)' } : {}}
          >
            <Cpu className="w-4 h-4 inline mr-2" />
            Hardware Commands
          </button>
          <button
            onClick={() => setActiveTab('sequence')}
            className={cn(
              'px-4 py-2 rounded-md text-sm font-medium transition-all',
              activeTab === 'sequence'
                ? 'bg-brand-500 text-white'
                : 'hover:bg-brand-500/20'
            )}
            style={activeTab !== 'sequence' ? { color: 'var(--color-text-secondary)' } : {}}
          >
            <ListOrdered className="w-4 h-4 inline mr-2" />
            Manual Sequence
          </button>
        </div>
      </div>

      {/* Warning Banner */}
      <div className="flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
        <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
        <span className="text-yellow-400 text-sm">
          Manual control mode. Use with caution - direct hardware access can affect system state.
        </span>
      </div>

      {/* Device Selection Bar */}
      <div
        className="p-4 rounded-lg border flex flex-wrap gap-4 items-end"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <div className="flex-1 min-w-[200px]">
          <Select
            label="Test Station (Batch)"
            options={batchOptions}
            value={selectedBatchId ?? ''}
            onChange={(e) => {
              selectDevice(e.target.value || null, null);
              selectCommand(null);
            }}
            placeholder="Select idle batch..."
          />
        </div>
        <div className="flex-1 min-w-[200px]">
          <Select
            label="Hardware Device"
            options={hardwareOptions}
            value={selectedHardwareId ?? ''}
            onChange={(e) => {
              selectDevice(selectedBatchId, e.target.value || null);
              selectCommand(null);
            }}
            placeholder="Select hardware..."
            disabled={!selectedBatchId}
          />
        </div>
        {commandsData && (
          <div className="flex items-center gap-2">
            <StatusBadge
              status={commandsData.connected ? 'connected' : 'disconnected'}
              size="sm"
            />
            <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              {commandsData.driver}
            </span>
          </div>
        )}
      </div>

      {/* Main Content */}
      {activeTab === 'commands' ? (
        <CommandsTab
          groupedCommands={groupedCommands}
          selectedCommand={selectedCommand}
          selectCommand={selectCommand}
          parameterValues={parameterValues}
          setParameterValue={setParameterValue}
          resultHistory={resultHistory}
          onExecute={handleExecute}
          isExecuting={executeCommand.isPending}
          isDisabled={!selectedBatchId || !selectedHardwareId}
          loadingCommands={loadingCommands}
        />
      ) : (
        <SequenceTab batchId={selectedBatchId} />
      )}
    </div>
  );
}

// ============================================================================
// Commands Tab
// ============================================================================

interface CommandsTabProps {
  groupedCommands: Record<string, CommandInfo[]>;
  selectedCommand: CommandInfo | null;
  selectCommand: (cmd: CommandInfo | null) => void;
  parameterValues: Record<string, unknown>;
  setParameterValue: (name: string, value: unknown) => void;
  resultHistory: Array<{
    id: string;
    hardware: string;
    command: string;
    result: unknown;
    success: boolean;
    duration: number;
    timestamp: Date;
    unit?: string;
  }>;
  onExecute: () => void;
  isExecuting: boolean;
  isDisabled: boolean;
  loadingCommands: boolean;
}

function CommandsTab({
  groupedCommands,
  selectedCommand,
  selectCommand,
  parameterValues,
  setParameterValue,
  resultHistory,
  onExecute,
  isExecuting,
  isDisabled,
  loadingCommands,
}: CommandsTabProps) {
  const [activeCategory, setActiveCategory] = useState<string>('measurement');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Command Selection Panel */}
      <div
        className="p-4 rounded-lg border space-y-4"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <h3
          className="text-lg font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Commands
        </h3>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-1">
          {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
            const Icon = CATEGORY_ICONS[key as keyof typeof CATEGORY_ICONS];
            const count = groupedCommands[key]?.length ?? 0;
            return (
              <button
                key={key}
                onClick={() => setActiveCategory(key)}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
                  activeCategory === key
                    ? 'bg-brand-500 text-white'
                    : 'hover:bg-brand-500/20'
                )}
                style={
                  activeCategory !== key
                    ? { color: 'var(--color-text-secondary)' }
                    : {}
                }
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
                {count > 0 && (
                  <span
                    className={cn(
                      'px-1.5 py-0.5 rounded text-xs',
                      activeCategory === key
                        ? 'bg-white/20'
                        : 'bg-gray-600/50'
                    )}
                  >
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Command List */}
        <div className="space-y-1 max-h-64 overflow-y-auto">
          {loadingCommands ? (
            <p
              className="text-sm py-4 text-center"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Loading commands...
            </p>
          ) : (groupedCommands[activeCategory]?.length ?? 0) === 0 ? (
            <p
              className="text-sm py-4 text-center"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {isDisabled
                ? 'Select a batch and hardware device'
                : 'No commands available'}
            </p>
          ) : (
            groupedCommands[activeCategory]?.map((cmd) => (
              <button
                key={cmd.name}
                onClick={() => selectCommand(cmd)}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-md transition-all',
                  selectedCommand?.name === cmd.name
                    ? 'bg-brand-500/20 border border-brand-500/50'
                    : 'hover:bg-brand-500/10'
                )}
              >
                <div
                  className="font-medium text-sm"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {cmd.displayName}
                </div>
                {cmd.description && (
                  <div
                    className="text-xs mt-0.5 line-clamp-1"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    {cmd.description}
                  </div>
                )}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Parameter Form Panel */}
      <div
        className="p-4 rounded-lg border space-y-4"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <h3
          className="text-lg font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {selectedCommand?.displayName ?? 'Parameters'}
        </h3>

        {selectedCommand ? (
          <>
            {selectedCommand.description && (
              <p
                className="text-sm"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {selectedCommand.description}
              </p>
            )}

            {selectedCommand.parameters.length > 0 ? (
              <div className="space-y-3">
                {selectedCommand.parameters.map((param) => (
                  <ParameterInput
                    key={param.name}
                    parameter={param}
                    value={parameterValues[param.name]}
                    onChange={(v) => setParameterValue(param.name, v)}
                  />
                ))}
              </div>
            ) : (
              <p
                className="text-sm italic"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                No parameters required
              </p>
            )}

            <Button
              variant="primary"
              className="w-full mt-4"
              onClick={onExecute}
              isLoading={isExecuting}
              disabled={isDisabled}
            >
              <Send className="w-4 h-4 mr-2" />
              Execute {selectedCommand.displayName}
            </Button>

            {selectedCommand.returnUnit && (
              <p
                className="text-xs text-center"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Returns: {selectedCommand.returnType} ({selectedCommand.returnUnit})
              </p>
            )}
          </>
        ) : (
          <p
            className="text-sm py-8 text-center"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            Select a command to configure parameters
          </p>
        )}
      </div>

      {/* Results Panel */}
      <div
        className="p-4 rounded-lg border space-y-4"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <h3
          className="text-lg font-semibold flex items-center gap-2"
          style={{ color: 'var(--color-text-primary)' }}
        >
          <History className="w-5 h-5" />
          Results
        </h3>

        {/* Last Result */}
        {resultHistory[0] && (
          <div
            className={cn(
              'p-3 rounded-lg border',
              resultHistory[0].success
                ? 'border-green-500/30 bg-green-500/10'
                : 'border-red-500/30 bg-red-500/10'
            )}
          >
            <div className="flex items-center justify-between mb-2">
              <span
                className="text-sm font-medium"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {resultHistory[0].hardware}.{resultHistory[0].command}
              </span>
              <StatusBadge
                status={resultHistory[0].success ? 'pass' : 'fail'}
                size="sm"
              />
            </div>
            <div
              className="text-2xl font-bold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {formatResult(resultHistory[0].result)}
              {resultHistory[0].unit && (
                <span className="text-sm ml-1">{resultHistory[0].unit}</span>
              )}
            </div>
            <div
              className="text-xs mt-1"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {resultHistory[0].duration}ms
            </div>
          </div>
        )}

        {/* History List */}
        <div className="space-y-1 max-h-64 overflow-y-auto">
          {resultHistory.length === 0 ? (
            <p
              className="text-sm text-center py-4"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              No commands executed yet
            </p>
          ) : (
            resultHistory.slice(1).map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between p-2 rounded-md text-sm"
                style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
              >
                <div className="flex items-center gap-2">
                  {entry.success ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500" />
                  )}
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    {entry.command}
                  </span>
                </div>
                <span
                  className="text-xs"
                  style={{ color: 'var(--color-text-tertiary)' }}
                >
                  {entry.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Sequence Tab
// ============================================================================

interface SequenceTabProps {
  batchId: string | null;
}

function SequenceTab({ batchId }: SequenceTabProps) {
  const { data: steps, isLoading } = useManualSteps(batchId);
  const sequenceSteps = useManualControlStore((s) => s.sequenceSteps);
  const currentStepIndex = useManualControlStore((s) => s.currentStepIndex);
  const stepOverrides = useManualControlStore((s) => s.stepOverrides);
  const setStepOverride = useManualControlStore((s) => s.setStepOverride);

  const runStep = useRunManualStep();
  const skipStep = useSkipManualStep();
  const resetSequence = useResetManualSequence();

  const handleRunStep = (stepName: string) => {
    if (!batchId) return;
    runStep.mutate({
      batchId,
      stepName,
      parameters: stepOverrides[stepName],
    });
  };

  const handleSkipStep = (stepName: string) => {
    if (!batchId) return;
    skipStep.mutate({ batchId, stepName });
  };

  const handleReset = () => {
    if (!batchId) return;
    resetSequence.mutate(batchId);
  };

  if (!batchId) {
    return (
      <div
        className="p-8 text-center rounded-lg border"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <ListOrdered
          className="w-12 h-12 mx-auto mb-4"
          style={{ color: 'var(--color-text-tertiary)' }}
        />
        <p style={{ color: 'var(--color-text-tertiary)' }}>
          Select a batch to view sequence steps
        </p>
      </div>
    );
  }

  if (isLoading) {
    return <LoadingOverlay message="Loading sequence steps..." />;
  }

  const displaySteps = sequenceSteps.length > 0 ? sequenceSteps : steps ?? [];

  return (
    <div
      className="p-4 rounded-lg border"
      style={{
        backgroundColor: 'var(--color-bg-secondary)',
        borderColor: 'var(--color-border-default)',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3
          className="text-lg font-semibold flex items-center gap-2"
          style={{ color: 'var(--color-text-primary)' }}
        >
          <ListOrdered className="w-5 h-5" />
          Manual Sequence Execution
        </h3>
        <Button variant="ghost" size="sm" onClick={handleReset}>
          <RotateCcw className="w-4 h-4 mr-1" />
          Reset
        </Button>
      </div>

      {displaySteps.length === 0 ? (
        <p
          className="text-sm text-center py-8"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          No sequence steps available
        </p>
      ) : (
        <div className="space-y-2">
          {displaySteps.map((step, index) => (
            <StepCard
              key={step.name}
              step={step}
              index={index}
              isCurrent={index === currentStepIndex}
              overrides={stepOverrides[step.name]}
              onRun={() => handleRunStep(step.name)}
              onSkip={() => handleSkipStep(step.name)}
              onUpdateOverrides={(overrides) =>
                setStepOverride(step.name, overrides)
              }
              isRunning={runStep.isPending}
            />
          ))}
        </div>
      )}

      {/* Bulk Actions */}
      {displaySteps.length > 0 && (
        <div className="flex gap-2 mt-4">
          <Button
            className="flex-1"
            onClick={() => {
              const nextPending = displaySteps.find(
                (s) => s.status === 'pending'
              );
              if (nextPending) {
                handleRunStep(nextPending.name);
              }
            }}
            disabled={
              !displaySteps.some((s) => s.status === 'pending') ||
              runStep.isPending
            }
          >
            <Play className="w-4 h-4 mr-1" />
            Run Next Step
          </Button>
          <Button
            variant="secondary"
            disabled={true} // TODO: Implement run all
          >
            <FastForward className="w-4 h-4 mr-1" />
            Run All Remaining
          </Button>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Step Card Component
// ============================================================================

interface StepCardProps {
  step: ManualStepInfo;
  index: number;
  isCurrent: boolean;
  overrides?: Record<string, unknown>;
  onRun: () => void;
  onSkip: () => void;
  onUpdateOverrides: (overrides: Record<string, unknown>) => void;
  isRunning: boolean;
}

function StepCard({
  step,
  index,
  isCurrent,
  overrides: _overrides,
  onRun,
  onSkip,
  onUpdateOverrides: _onUpdateOverrides,
  isRunning,
}: StepCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors = {
    pending: 'border-gray-500/30',
    running: 'border-blue-500 bg-blue-500/10',
    completed: 'border-green-500 bg-green-500/10',
    failed: 'border-red-500 bg-red-500/10',
    skipped: 'border-gray-500 bg-gray-500/10',
  };

  const StatusIcon = {
    pending: Clock,
    running: Play,
    completed: CheckCircle,
    failed: XCircle,
    skipped: SkipForward,
  }[step.status];

  return (
    <div
      className={cn(
        'p-3 rounded-lg border transition-all',
        statusColors[step.status],
        isCurrent && 'ring-2 ring-brand-500'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon
            className={cn(
              'w-5 h-5',
              step.status === 'running' && 'animate-pulse',
              step.status === 'completed' && 'text-green-500',
              step.status === 'failed' && 'text-red-500',
              step.status === 'skipped' && 'text-gray-500'
            )}
            style={
              step.status === 'pending' || step.status === 'running'
                ? { color: 'var(--color-text-secondary)' }
                : {}
            }
          />
          <div>
            <span
              className="font-medium"
              style={{ color: 'var(--color-text-primary)' }}
            >
              {index + 1}. {step.displayName}
            </span>
            {step.duration !== undefined && (
              <span
                className="ml-2 text-xs"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {step.duration.toFixed(1)}s
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {step.status === 'pending' && isCurrent && (
            <>
              <Button size="sm" onClick={onRun} isLoading={isRunning}>
                <Play className="w-3 h-3" />
              </Button>
              {step.manual?.skippable && (
                <Button size="sm" variant="ghost" onClick={onSkip}>
                  Skip
                </Button>
              )}
            </>
          )}
          {step.status === 'failed' && (
            <Button size="sm" variant="secondary" onClick={onRun}>
              <RotateCcw className="w-3 h-3 mr-1" />
              Retry
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div
          className="mt-3 pt-3 border-t"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          {step.manual?.prompt && (
            <p
              className="text-sm mb-2 italic"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {step.manual.prompt}
            </p>
          )}

          {step.result && (
            <div className="mt-2">
              <h4
                className="text-sm font-medium mb-1"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Result
              </h4>
              <pre
                className="text-xs p-2 rounded overflow-auto max-h-32"
                style={{
                  backgroundColor: 'var(--color-bg-tertiary)',
                  color: 'var(--color-text-secondary)',
                }}
              >
                {JSON.stringify(step.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Parameter Input Component
// ============================================================================

interface ParameterInputProps {
  parameter: CommandParameter;
  value: unknown;
  onChange: (value: unknown) => void;
}

function ParameterInput({ parameter, value, onChange }: ParameterInputProps) {
  switch (parameter.type) {
    case 'number':
      return (
        <div>
          <label
            className="block text-sm font-medium mb-1"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {parameter.displayName}
            {parameter.unit && (
              <span className="ml-1 text-xs">({parameter.unit})</span>
            )}
          </label>
          <input
            type="number"
            value={value as number ?? parameter.default ?? ''}
            onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
            min={parameter.min}
            max={parameter.max}
            step="any"
            className="w-full px-3 py-2 rounded-lg text-sm"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              borderColor: 'var(--color-border-default)',
              color: 'var(--color-text-primary)',
            }}
          />
          {(parameter.min !== undefined || parameter.max !== undefined) && (
            <p
              className="text-xs mt-1"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Range: {parameter.min ?? '-∞'} to {parameter.max ?? '∞'}
            </p>
          )}
        </div>
      );

    case 'boolean':
      return (
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={value as boolean ?? parameter.default as boolean ?? false}
            onChange={(e) => onChange(e.target.checked)}
            className="w-4 h-4 rounded"
          />
          <span style={{ color: 'var(--color-text-secondary)' }}>
            {parameter.displayName}
          </span>
        </label>
      );

    case 'select':
      return (
        <Select
          label={parameter.displayName}
          value={String(value ?? parameter.default ?? '')}
          onChange={(e) => onChange(e.target.value)}
          options={
            parameter.options?.map((opt) => ({
              value: String(opt.value),
              label: opt.label,
            })) ?? []
          }
        />
      );

    default:
      return (
        <Input
          label={parameter.displayName}
          value={String(value ?? parameter.default ?? '')}
          onChange={(e) => onChange(e.target.value)}
          placeholder={parameter.description}
        />
      );
  }
}

// ============================================================================
// Helpers
// ============================================================================

function formatResult(result: unknown): string {
  if (typeof result === 'number') {
    return result.toFixed(4);
  }
  if (typeof result === 'boolean') {
    return result ? 'TRUE' : 'FALSE';
  }
  if (typeof result === 'string') {
    return result;
  }
  if (result === null || result === undefined) {
    return '-';
  }
  return JSON.stringify(result);
}
