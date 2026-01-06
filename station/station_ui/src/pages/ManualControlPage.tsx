/**
 * Enhanced Manual Control Page
 *
 * Features:
 * - Smart command discovery with category tabs
 * - Type-aware parameter inputs
 * - Result visualization with history
 * - Manual sequence step-by-step execution
 */

import { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import {
  Wrench,
  Play,
  SkipForward,
  ChevronDown,
  ChevronUp,
  ListOrdered,
  CheckCircle,
  XCircle,
  Clock,
  FastForward,
  FlaskConical,
  RefreshCw,
  StopCircle,
  Plug,
  Terminal,
  Settings,
  Bug,
  Trash2,
} from 'lucide-react';
import {
  useSequenceList,
  useSequence,
  useSimulationSession,
  useCreateSimulationSession,
  useInitializeSimulationSession,
  useFinalizeSimulationSession,
  useAbortSimulationSession,
  useRunSimulationStep,
  useSkipSimulationStep,
  useDeleteSimulationSession,
  // Manual Sequence (real hardware) hooks
  useManualSession,
  useCreateManualSession,
  useInitializeManualSession,
  useFinalizeManualSession,
  useAbortManualSession,
  useRunManualSequenceStep,
  useSkipManualSequenceStep,
  useDeleteManualSession,
} from '../hooks';
import { Button } from '../components/atoms/Button';
import { Select } from '../components/atoms/Select';
import { StatusBadge } from '../components/atoms/StatusBadge';
import { cn, getErrorMessage } from '../utils';
import type { ManualStepState } from '../hooks';
import type { ParameterSchema } from '../types';

export function ManualControlPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Wrench className="w-6 h-6 text-brand-500" />
        <h2
          className="text-2xl font-bold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Manual Control
        </h2>
      </div>

      {/* Main Content */}
      <ManualTestTab />
    </div>
  );
}

// ============================================================================
// Debug Log Types
// ============================================================================

interface DebugLogEntry {
  id: number;
  timestamp: Date;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  data?: unknown;
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

// ============================================================================
// Manual Test Tab (Real Hardware or Mock Mode)
// ============================================================================

function ManualTestTab() {
  const { data: sequences, isLoading: loadingSequences } = useSequenceList();
  const [selectedSequence, setSelectedSequence] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<Record<string, unknown>>({});
  const [mockMode, setMockMode] = useState(false);

  // Debug log state
  const [debugLogs, setDebugLogs] = useState<DebugLogEntry[]>([]);
  const [showDebugPanel, setShowDebugPanel] = useState(true);
  const logIdRef = useRef(0);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Add debug log helper
  const addLog = useCallback((level: DebugLogEntry['level'], message: string, data?: unknown) => {
    setDebugLogs(prev => {
      const newLog: DebugLogEntry = {
        id: ++logIdRef.current,
        timestamp: new Date(),
        level,
        message,
        data,
      };
      // Keep last 100 logs
      const updated = [...prev, newLog].slice(-100);
      return updated;
    });
  }, []);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [debugLogs]);

  // Clear logs
  const clearLogs = useCallback(() => {
    setDebugLogs([]);
  }, []);

  // Fetch sequence details for parameters
  const { data: sequenceDetails } = useSequence(selectedSequence || null);

  // Session management - conditionally use manual or simulation hooks
  // Manual (real hardware) hooks
  const manualSessionQuery = useManualSession(mockMode ? null : sessionId);
  const createManualSession = useCreateManualSession();
  const initializeManualSession = useInitializeManualSession();
  const finalizeManualSession = useFinalizeManualSession();
  const abortManualSession = useAbortManualSession();
  const deleteManualSession = useDeleteManualSession();
  const runManualStep = useRunManualSequenceStep();
  const skipManualStep = useSkipManualSequenceStep();

  // Simulation (mock) hooks
  const simulationSessionQuery = useSimulationSession(mockMode ? sessionId : null);
  const createSimulationSession = useCreateSimulationSession();
  const initializeSimulationSession = useInitializeSimulationSession();
  const finalizeSimulationSession = useFinalizeSimulationSession();
  const abortSimulationSession = useAbortSimulationSession();
  const deleteSimulationSession = useDeleteSimulationSession();
  const runSimulationStep = useRunSimulationStep();
  const skipSimulationStep = useSkipSimulationStep();

  // Unified session data
  const session = mockMode ? simulationSessionQuery.data : manualSessionQuery.data;
  const loadingSession = mockMode ? simulationSessionQuery.isLoading : manualSessionQuery.isLoading;

  const sequenceOptions = useMemo(() => {
    return (
      sequences?.map((s) => ({
        value: s.name,
        label: `${s.displayName} (v${s.version})`,
      })) ?? []
    );
  }, [sequences]);

  const handleCreateSession = async () => {
    if (!selectedSequence) return;
    // Clear debug logs for new session
    clearLogs();
    try {
      // Build parameters with overrides
      const params: Record<string, unknown> = {};
      if (sequenceDetails?.parameters) {
        for (const param of sequenceDetails.parameters) {
          params[param.name] = parameterValues[param.name] ?? param.default;
        }
      }
      const modeLabel = mockMode ? '[Mock]' : '[Hardware]';
      addLog('info', `${modeLabel} Creating session for "${selectedSequence}"...`, { params, mockMode });

      const newSession = mockMode
        ? await createSimulationSession.mutateAsync({
            sequenceName: selectedSequence,
            parameters: Object.keys(params).length > 0 ? params : undefined,
          })
        : await createManualSession.mutateAsync({
            sequenceName: selectedSequence,
            parameters: Object.keys(params).length > 0 ? params : undefined,
          });

      setSessionId(newSession.id);
      addLog('success', `Session created: ${newSession.id}`, {
        status: newSession.status,
        steps: newSession.steps.length,
      });
    } catch (error) {
      addLog('error', `Failed to create session: ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  const handleInitialize = async () => {
    if (!sessionId) return;
    // Clear logs before initializing
    clearLogs();
    try {
      if (mockMode) {
        addLog('info', 'Initializing simulation session...');
        const result = await initializeSimulationSession.mutateAsync(sessionId);
        addLog('success', `Session initialized.`, { status: result.status });
      } else {
        addLog('info', 'Initializing session (connecting hardware)...');
        const result = await initializeManualSession.mutateAsync(sessionId);
        const hwConnected = result.hardware.filter((h) => h.connected).length;
        addLog('success', `Session initialized. Hardware: ${hwConnected}/${result.hardware.length} connected`, {
          status: result.status,
          hardware: result.hardware.map((h) => ({ id: h.id, connected: h.connected, error: h.error })),
        });
      }
    } catch (error) {
      addLog('error', `Failed to initialize session: ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  const handleFinalize = async () => {
    if (!sessionId) return;
    try {
      addLog('info', 'Finalizing session...');
      const result = mockMode
        ? await finalizeSimulationSession.mutateAsync(sessionId)
        : await finalizeManualSession.mutateAsync(sessionId);
      addLog('success', `Session finalized. Overall: ${result.overallPass ? 'PASS' : 'FAIL'}`, {
        status: result.status,
        overallPass: result.overallPass,
      });
    } catch (error) {
      addLog('error', `Failed to finalize session: ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  const handleAbort = async () => {
    if (!sessionId) return;
    try {
      addLog('warning', 'Aborting session...');
      if (mockMode) {
        await abortSimulationSession.mutateAsync(sessionId);
      } else {
        await abortManualSession.mutateAsync(sessionId);
      }
      addLog('warning', 'Session aborted');
    } catch (error) {
      addLog('error', `Failed to abort session: ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  const handleReset = async () => {
    if (sessionId) {
      if (mockMode) {
        await deleteSimulationSession.mutateAsync(sessionId);
      } else {
        await deleteManualSession.mutateAsync(sessionId);
      }
    }
    setSessionId(null);
    setSelectedSequence('');
    setParameterValues({});
    // Clear debug logs on reset
    clearLogs();
  };

  const handleRunStep = async (stepName: string) => {
    if (!sessionId) return;
    try {
      // Build parameter overrides from modified values
      const overrides = Object.keys(parameterValues).length > 0 ? parameterValues : undefined;
      if (overrides) {
        addLog('info', `Running step: ${stepName} with parameter overrides...`, overrides);
      } else {
        addLog('info', `Running step: ${stepName}...`);
      }

      const result = mockMode
        ? await runSimulationStep.mutateAsync({ sessionId, stepName, parameterOverrides: overrides })
        : await runManualStep.mutateAsync({ sessionId, stepName, parameterOverrides: overrides });

      if (result.status === 'passed') {
        addLog('success', `Step "${stepName}" passed (${result.duration.toFixed(2)}s)`, {
          measurements: result.measurements,
          result: result.result,
        });
      } else {
        addLog('error', `Step "${stepName}" failed: ${result.error}`, {
          measurements: result.measurements,
          error: result.error,
        });
      }
    } catch (error) {
      addLog('error', `Failed to run step "${stepName}": ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  const handleSkipStep = async (stepName: string) => {
    if (!sessionId) return;
    try {
      addLog('warning', `Skipping step: ${stepName}`);
      if (mockMode) {
        await skipSimulationStep.mutateAsync({ sessionId, stepName });
      } else {
        await skipManualStep.mutateAsync({ sessionId, stepName });
      }
      addLog('info', `Step "${stepName}" skipped`);
    } catch (error) {
      addLog('error', `Failed to skip step "${stepName}": ${getErrorMessage(error)}`, error);
      // Error toast handled by global mutation error handler
    }
  };

  // Initialize parameters when sequence is selected
  const handleSequenceChange = (sequenceName: string) => {
    setSelectedSequence(sequenceName);
    setParameterValues({});
  };

  // Update parameter value
  const handleParameterChange = (name: string, value: unknown) => {
    setParameterValues((prev) => ({ ...prev, [name]: value }));
  };

  // Session status helpers
  const isCreated = session?.status === 'created';
  const isConnecting = session?.status === 'connecting';
  const isReady = session?.status === 'ready';
  const isRunning = session?.status === 'running';
  const isActive = isReady || isRunning;

  return (
    <div className="space-y-4">
      {/* Session Setup / Control */}
      <div
        className="p-4 rounded-lg border"
        style={{
          backgroundColor: 'var(--color-bg-secondary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        {!session ? (
          <div className="space-y-4">
            <h3
              className="text-lg font-semibold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Create Test Session
            </h3>

            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Select
                  label="Select Sequence"
                  options={sequenceOptions}
                  value={selectedSequence}
                  onChange={(e) => handleSequenceChange(e.target.value)}
                  placeholder="Choose a sequence..."
                  disabled={loadingSequences}
                />
              </div>
              {/* Mock Mode Toggle */}
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={mockMode}
                    onChange={(e) => setMockMode(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div
                    className={cn(
                      'w-11 h-6 rounded-full transition-colors',
                      mockMode ? 'bg-brand-500' : 'bg-gray-600'
                    )}
                  />
                  <div
                    className={cn(
                      'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                      mockMode && 'translate-x-5'
                    )}
                  />
                </div>
                <span
                  className="text-sm font-medium flex items-center gap-1"
                  style={{ color: mockMode ? 'var(--color-brand-500)' : 'var(--color-text-secondary)' }}
                >
                  <FlaskConical className="w-4 h-4" />
                  Mock
                </span>
              </label>
              <Button
                variant="primary"
                onClick={handleCreateSession}
                isLoading={mockMode ? createSimulationSession.isPending : createManualSession.isPending}
                disabled={!selectedSequence}
              >
                <Terminal className="w-4 h-4 mr-2" />
                Create Session
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3
                  className="text-lg font-semibold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {session.sequenceName}
                  <span
                    className="ml-2 text-sm font-normal"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    v{session.sequenceVersion}
                  </span>
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <StatusBadge
                    status={
                      session.status === 'completed' && session.overallPass
                        ? 'pass'
                        : session.status === 'completed' && !session.overallPass
                        ? 'fail'
                        : session.status === 'ready'
                        ? 'idle'
                        : session.status === 'running'
                        ? 'running'
                        : session.status === 'connecting'
                        ? 'running'
                        : session.status === 'failed'
                        ? 'error'
                        : 'idle'
                    }
                    size="sm"
                  />
                  <span
                    className="text-sm"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    Session: {session.id}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                {isCreated && (
                  <Button
                    variant="primary"
                    onClick={handleInitialize}
                    isLoading={
                      mockMode
                        ? initializeSimulationSession.isPending
                        : initializeManualSession.isPending || isConnecting
                    }
                  >
                    {mockMode ? (
                      <>
                        <Play className="w-4 h-4 mr-1" />
                        Initialize
                      </>
                    ) : (
                      <>
                        <Plug className="w-4 h-4 mr-1" />
                        Connect & Initialize
                      </>
                    )}
                  </Button>
                )}
                {isActive && (
                  <>
                    <Button
                      variant="secondary"
                      onClick={handleFinalize}
                      isLoading={mockMode ? finalizeSimulationSession.isPending : finalizeManualSession.isPending}
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Finalize
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={handleAbort}
                      isLoading={mockMode ? abortSimulationSession.isPending : abortManualSession.isPending}
                    >
                      <StopCircle className="w-4 h-4 mr-1" />
                      Abort
                    </Button>
                  </>
                )}
                <Button variant="ghost" onClick={handleReset}>
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Reset
                </Button>
              </div>
            </div>

            {/* Hardware Status - Only show for manual mode */}
            {!mockMode && 'hardware' in session && session.hardware.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {session.hardware.map((hw) => (
                  <div
                    key={hw.id}
                    className={cn(
                      'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm',
                      hw.connected
                        ? 'bg-green-500/10 border border-green-500/30'
                        : 'bg-gray-500/10 border border-gray-500/30'
                    )}
                  >
                    <Plug
                      className={cn(
                        'w-4 h-4',
                        hw.connected ? 'text-green-500' : 'text-gray-500'
                      )}
                    />
                    <span style={{ color: 'var(--color-text-secondary)' }}>
                      {hw.displayName}
                    </span>
                    {hw.error && (
                      <span className="text-red-400 text-xs">({hw.error})</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Progress Bar */}
            {session.steps.length > 0 && (
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span style={{ color: 'var(--color-text-tertiary)' }}>
                    Progress
                  </span>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>
                    {session.steps.filter((s) => s.status !== 'pending').length} /{' '}
                    {session.steps.length} steps
                  </span>
                </div>
                <div
                  className="h-2 rounded-full overflow-hidden"
                  style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
                >
                  <div
                    className="h-full bg-brand-500 transition-all duration-300"
                    style={{
                      width: `${
                        (session.steps.filter((s) => s.status !== 'pending').length /
                          session.steps.length) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Three-column layout: Test Steps | Parameters | Debug Logs */}
      {session && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Column 1: Test Steps */}
          <div
            className="p-4 rounded-lg border"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border-default)',
            }}
          >
            <h3
              className="text-lg font-semibold mb-4 flex items-center gap-2"
              style={{ color: 'var(--color-text-primary)' }}
            >
              <ListOrdered className="w-5 h-5" />
              Test Steps
            </h3>

            {loadingSession ? (
              <p
                className="text-sm text-center py-4"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                Loading session...
              </p>
            ) : session.steps.length === 0 ? (
              <p
                className="text-sm text-center py-4"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                No steps available
              </p>
            ) : (
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {session.steps.map((step, index) => {
                  // Handle skippable - only exists in ManualStepState
                  const isSkippable = 'skippable' in step ? step.skippable : true;
                  return (
                    <ManualTestStepCard
                      key={step.name}
                      step={{
                        ...step,
                        skippable: isSkippable,
                        parameterOverrides: 'parameterOverrides' in step ? step.parameterOverrides : [],
                      }}
                      index={index}
                      isCurrent={index === session.currentStepIndex}
                      canRun={isReady && step.status === 'pending'}
                      canSkip={isReady && step.status === 'pending' && isSkippable}
                      onRun={() => handleRunStep(step.name)}
                      onSkip={() => handleSkipStep(step.name)}
                      isRunning={mockMode ? runSimulationStep.isPending : runManualStep.isPending}
                    />
                  );
                })}
              </div>
            )}

            {/* Run All Button */}
            {session && isReady && session.steps.some((s) => s.status === 'pending') && (
              <div className="mt-4">
                <Button
                  className="w-full"
                  onClick={async () => {
                    for (const step of session.steps) {
                      if (step.status === 'pending') {
                        await handleRunStep(step.name);
                      }
                    }
                  }}
                  isLoading={mockMode ? runSimulationStep.isPending : runManualStep.isPending}
                >
                  <FastForward className="w-4 h-4 mr-1" />
                  Run All Remaining
                </Button>
              </div>
            )}
          </div>

          {/* Column 2: Parameters */}
          <div
            className="p-4 rounded-lg border"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border-default)',
            }}
          >
            <h3
              className="text-lg font-semibold mb-4 flex items-center gap-2"
              style={{ color: 'var(--color-text-primary)' }}
            >
              <Settings className="w-5 h-5" />
              Parameters
            </h3>

            {sequenceDetails?.parameters && sequenceDetails.parameters.length > 0 ? (
              <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {sequenceDetails.parameters.map((param) => {
                  // Use parameterValues if set, otherwise fall back to session.parameters or default
                  const currentValue = parameterValues[param.name] ?? session.parameters?.[param.name] ?? param.default;
                  return (
                    <ParameterInput
                      key={param.name}
                      param={param}
                      value={currentValue}
                      onChange={(value) => handleParameterChange(param.name, value)}
                    />
                  );
                })}
                {Object.keys(parameterValues).length > 0 && (
                  <p
                    className="text-xs italic"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    * Modified parameters will be applied to next step execution
                  </p>
                )}
              </div>
            ) : (
              <p
                className="text-sm text-center py-4"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                No parameters configured
              </p>
            )}
          </div>

          {/* Column 3: Debug Logs */}
          <div
            className="p-4 rounded-lg border"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              borderColor: 'var(--color-border-default)',
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <h3
                className="text-lg font-semibold flex items-center gap-2"
                style={{ color: 'var(--color-text-primary)' }}
              >
                <Bug className="w-5 h-5" />
                Debug Logs
              </h3>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowDebugPanel(!showDebugPanel)}
                >
                  {showDebugPanel ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={clearLogs}
                  disabled={debugLogs.length === 0}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {showDebugPanel && (
              <div
                ref={logContainerRef}
                className="font-mono text-xs space-y-1 max-h-[500px] overflow-y-auto p-2 rounded"
                style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
              >
                {debugLogs.length === 0 ? (
                  <p
                    className="text-center py-4"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    No logs yet. Actions will be logged here.
                  </p>
                ) : (
                  debugLogs.map((log) => (
                    <DebugLogRow key={log.id} log={log} />
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Debug Log Row Component
// ============================================================================

function DebugLogRow({ log }: { log: DebugLogEntry }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const levelColors = {
    info: 'text-blue-400',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  };

  const levelLabels = {
    info: 'INFO',
    success: 'PASS',
    warning: 'WARN',
    error: 'ERR ',
  };

  const formatTimestamp = (date: Date) => {
    const time = date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    const ms = String(date.getMilliseconds()).padStart(3, '0');
    return `${time}.${ms}`;
  };

  const hasData = log.data !== undefined && log.data !== null;

  return (
    <div
      className="py-1 border-b last:border-b-0"
      style={{ borderColor: 'var(--color-border-default)' }}
    >
      <div className="flex items-start gap-2">
        <span style={{ color: 'var(--color-text-tertiary)' }}>{formatTimestamp(log.timestamp)}</span>
        <span className={cn('font-bold', levelColors[log.level])}>
          [{levelLabels[log.level]}]
        </span>
        <span
          className="flex-1"
          style={{ color: 'var(--color-text-primary)' }}
        >
          {log.message}
        </span>
        {hasData && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-1 hover:bg-white/10 rounded"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {isExpanded ? '[-]' : '[+]'}
          </button>
        )}
      </div>
      {isExpanded && hasData && (
        <pre
          className="mt-1 ml-20 p-2 rounded text-xs overflow-auto max-h-32"
          style={{
            backgroundColor: 'var(--color-bg-secondary)',
            color: 'var(--color-text-secondary)',
          }}
        >
          {JSON.stringify(log.data, null, 2)}
        </pre>
      )}
    </div>
  );
}

// ============================================================================
// Manual Test Step Card
// ============================================================================

interface ManualTestStepCardProps {
  step: ManualStepState;
  index: number;
  isCurrent: boolean;
  canRun: boolean;
  canSkip: boolean;
  onRun: () => void;
  onSkip: () => void;
  isRunning: boolean;
}

function ManualTestStepCard({
  step,
  index,
  isCurrent,
  canRun,
  canSkip,
  onRun,
  onSkip,
  isRunning,
}: ManualTestStepCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors: Record<string, string> = {
    pending: 'border-gray-500/30',
    running: 'border-blue-500 bg-blue-500/10',
    passed: 'border-green-500 bg-green-500/10',
    failed: 'border-red-500 bg-red-500/10',
    skipped: 'border-gray-500 bg-gray-500/10',
  };

  const StatusIcon = {
    pending: Clock,
    running: Play,
    passed: CheckCircle,
    failed: XCircle,
    skipped: SkipForward,
  }[step.status] ?? Clock;

  return (
    <div
      className={cn(
        'p-3 rounded-lg border transition-all',
        statusColors[step.status] ?? 'border-gray-500/30',
        isCurrent && 'ring-2 ring-brand-500'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusIcon
            className={cn(
              'w-5 h-5',
              step.status === 'running' && 'animate-pulse',
              step.status === 'passed' && 'text-green-500',
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
            {step.duration > 0 && (
              <span
                className="ml-2 text-xs"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {step.duration.toFixed(2)}s
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {canRun && (
            <Button size="sm" onClick={onRun} isLoading={isRunning}>
              <Play className="w-3 h-3" />
            </Button>
          )}
          {canSkip && (
            <Button size="sm" variant="ghost" onClick={onSkip}>
              Skip
            </Button>
          )}
          {(step.result || step.error || Object.keys(step.measurements).length > 0) && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? <ChevronUp /> : <ChevronDown />}
            </Button>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div
          className="mt-3 pt-3 border-t space-y-2"
          style={{ borderColor: 'var(--color-border-default)' }}
        >
          {step.error && (
            <div className="p-2 rounded bg-red-500/10 text-red-400 text-sm">
              Error: {step.error}
            </div>
          )}

          {Object.keys(step.measurements).length > 0 && (
            <div>
              <h4
                className="text-sm font-medium mb-1"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Measurements
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(step.measurements).map(([key, value]) => (
                  <div
                    key={key}
                    className="p-2 rounded text-sm"
                    style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
                  >
                    <span style={{ color: 'var(--color-text-tertiary)' }}>
                      {key}:
                    </span>{' '}
                    <span style={{ color: 'var(--color-text-primary)' }}>
                      {formatResult(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {step.result && (
            <div>
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
  param: ParameterSchema;
  value: unknown;
  onChange: (value: unknown) => void;
}

function ParameterInput({ param, value, onChange }: ParameterInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const rawValue = e.target.value;

    switch (param.type) {
      case 'float':
        onChange(rawValue === '' ? param.default : parseFloat(rawValue));
        break;
      case 'integer':
        onChange(rawValue === '' ? param.default : parseInt(rawValue, 10));
        break;
      case 'boolean':
        onChange(rawValue === 'true');
        break;
      default:
        onChange(rawValue);
    }
  };

  const inputClasses = cn(
    'w-full px-3 py-2 rounded-md text-sm',
    'border transition-colors',
    'focus:outline-none focus:ring-2 focus:ring-brand-500/50'
  );

  const inputStyle = {
    backgroundColor: 'var(--color-bg-secondary)',
    borderColor: 'var(--color-border-default)',
    color: 'var(--color-text-primary)',
  };

  return (
    <div className="space-y-1">
      <label
        className="text-sm font-medium flex items-center gap-2"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        {param.displayName}
        {param.unit && (
          <span
            className="text-xs px-1.5 py-0.5 rounded"
            style={{
              backgroundColor: 'var(--color-bg-secondary)',
              color: 'var(--color-text-tertiary)',
            }}
          >
            {param.unit}
          </span>
        )}
      </label>

      {param.type === 'boolean' ? (
        <select
          className={inputClasses}
          style={inputStyle}
          value={String(value)}
          onChange={handleChange}
        >
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      ) : param.options && param.options.length > 0 ? (
        <select
          className={inputClasses}
          style={inputStyle}
          value={String(value)}
          onChange={handleChange}
        >
          {param.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={param.type === 'float' || param.type === 'integer' ? 'number' : 'text'}
          className={inputClasses}
          style={inputStyle}
          value={value === null || value === undefined ? '' : String(value)}
          onChange={handleChange}
          min={param.min}
          max={param.max}
          step={param.type === 'float' ? 'any' : param.type === 'integer' ? 1 : undefined}
          placeholder={param.description}
        />
      )}

      {param.description && (
        <p
          className="text-xs"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          {param.description}
        </p>
      )}
    </div>
  );
}
