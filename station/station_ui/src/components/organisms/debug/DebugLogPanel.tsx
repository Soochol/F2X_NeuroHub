/**
 * DebugLogPanel - Main debug panel component with tabs for logs, step data, params, and config.
 */

import { useMemo, useState, useCallback, useEffect } from 'react';
import { FileText, Database, Download, Trash2, Settings, Sliders, Copy, Check } from 'lucide-react';
import { useDebugPanelStore, type DebugPanelTab } from '../../../stores/debugPanelStore';
import { useLogStore } from '../../../stores';
import { LogFilters } from './LogFilters';
import { LogEntryList } from './LogEntryList';
import { StepDataViewer } from './StepDataViewer';
import { BatchConfigEditor } from './BatchConfigEditor';
import { ParametersEditor } from './ParametersEditor';
import { Button } from '../../atoms/Button';
import type { StepResult } from '../../../types';

interface DebugLogPanelProps {
  /** Batch ID for filtering logs */
  batchId: string;
  /** Step results to display in data tab */
  steps: StepResult[];
  /** Whether batch is currently running (disables config editing) */
  isRunning?: boolean;
  /** Callback when there are pending unsaved changes */
  onPendingChangesChange?: (hasPending: boolean) => void;
}

interface TabButtonProps {
  tab: DebugPanelTab;
  label: string;
  icon: React.ReactNode;
  isActive: boolean;
  onClick: () => void;
}

function TabButton({ label, icon, isActive, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-t transition-colors ${
        isActive
          ? 'bg-zinc-800 text-zinc-100 border-b-2 border-brand-500'
          : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

export function DebugLogPanel({ batchId, steps, isRunning = false, onPendingChangesChange }: DebugLogPanelProps) {
  const { activeTab, setActiveTab, selectedStep, logLevel, searchQuery } = useDebugPanelStore();
  const logs = useLogStore((s) => s.logs);
  const clearLogs = useLogStore((s) => s.clearLogs);

  // Track dirty state from both editors
  const [configDirty, setConfigDirty] = useState(false);
  const [paramsDirty, setParamsDirty] = useState(false);

  // Track clipboard copy success state
  const [copied, setCopied] = useState(false);

  // Combined pending changes state
  const hasPendingChanges = configDirty || paramsDirty;

  // Notify parent when pending changes state changes
  useEffect(() => {
    onPendingChangesChange?.(hasPendingChanges);
  }, [hasPendingChanges, onPendingChangesChange]);

  // Callbacks for editors
  const handleConfigDirtyChange = useCallback((isDirty: boolean) => {
    setConfigDirty(isDirty);
  }, []);

  const handleParamsDirtyChange = useCallback((isDirty: boolean) => {
    setParamsDirty(isDirty);
  }, []);

  // Get unique step names for filter dropdown
  const stepNames = useMemo(() => {
    return steps.map((s) => s.name);
  }, [steps]);

  // Filter logs for export
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      if (log.batchId !== batchId) return false;
      if (logLevel && log.level !== logLevel) return false;
      if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      if (selectedStep && !log.message.toLowerCase().includes(selectedStep.toLowerCase())) return false;
      return true;
    });
  }, [logs, batchId, logLevel, searchQuery, selectedStep]);

  // Format logs as text content
  const formatLogsAsText = useCallback(() => {
    return filteredLogs
      .map((log) => {
        const time = log.timestamp.toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        });
        return `${time} [${log.level.toUpperCase()}] ${log.message}`;
      })
      .join('\n');
  }, [filteredLogs]);

  const handleCopyLogs = useCallback(async () => {
    const content = formatLogsAsText();
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy logs:', err);
    }
  }, [formatLogsAsText]);

  const handleExportLogs = () => {
    const content = formatLogsAsText();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debug-log-${batchId}-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportData = () => {
    const data = steps.map((step) => ({
      order: step.order,
      name: step.name,
      status: step.status,
      pass: step.pass,
      duration: step.duration,
      result: step.result,
      error: step.error,
    }));

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `step-data-${batchId}-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Tab bar */}
      <div
        className="flex items-center justify-between px-2 py-1 border-b"
        style={{
          backgroundColor: 'var(--color-bg-tertiary)',
          borderColor: 'var(--color-border-default)',
        }}
      >
        <div className="flex items-center gap-1">
          <TabButton
            tab="logs"
            label="Logs"
            icon={<FileText className="w-3.5 h-3.5" />}
            isActive={activeTab === 'logs'}
            onClick={() => setActiveTab('logs')}
          />
          <TabButton
            tab="data"
            label="Data"
            icon={<Database className="w-3.5 h-3.5" />}
            isActive={activeTab === 'data'}
            onClick={() => setActiveTab('data')}
          />
          <TabButton
            tab="params"
            label="Params"
            icon={<Sliders className="w-3.5 h-3.5" />}
            isActive={activeTab === 'params'}
            onClick={() => setActiveTab('params')}
          />
          <TabButton
            tab="config"
            label="Config"
            icon={<Settings className="w-3.5 h-3.5" />}
            isActive={activeTab === 'config'}
            onClick={() => setActiveTab('config')}
          />
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-1">
          {activeTab === 'logs' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopyLogs}
              disabled={filteredLogs.length === 0}
              title={copied ? 'Copied!' : 'Copy logs to clipboard'}
              className="p-1"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={activeTab === 'logs' ? handleExportLogs : handleExportData}
            disabled={activeTab === 'logs' ? filteredLogs.length === 0 : steps.length === 0}
            title="Export"
            className="p-1"
          >
            <Download className="w-3.5 h-3.5" />
          </Button>
          {activeTab === 'logs' && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearLogs}
              disabled={logs.length === 0}
              title="Clear logs"
              className="p-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>

      {/* Filters (only for logs tab) */}
      {activeTab === 'logs' && <LogFilters stepNames={stepNames} />}

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'logs' && <LogEntryList batchId={batchId} />}
        {activeTab === 'data' && <StepDataViewer steps={steps} />}
        {activeTab === 'params' && (
          <ParametersEditor
            batchId={batchId}
            isRunning={isRunning}
            onDirtyChange={handleParamsDirtyChange}
          />
        )}
        {activeTab === 'config' && (
          <BatchConfigEditor
            batchId={batchId}
            isRunning={isRunning}
            onDirtyChange={handleConfigDirtyChange}
          />
        )}
      </div>
    </div>
  );
}
