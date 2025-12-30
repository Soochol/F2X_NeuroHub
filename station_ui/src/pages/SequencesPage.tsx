/**
 * Sequences page - Sequence package browser and viewer.
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  GitBranch,
  ChevronRight,
  Clock,
  Settings2,
  Cpu,
  ArrowRight,
  Upload,
  Download,
  Trash2,
  Zap,
  Play,
  Eye,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useSequenceList, useSequence, useDeleteSequence, useDownloadSequence, useSimulation } from '../hooks';
import { LoadingOverlay, LoadingSpinner } from '../components/atoms/LoadingSpinner';
import { Button } from '../components/atoms/Button';
import { SequenceUpload } from '../components/organisms/sequences';
import { ROUTES, getSequenceDetailRoute } from '../constants';
import type { SequencePackage, SequenceSummary, StepSchema, ParameterSchema, HardwareSchema, SimulationMode, SimulationResult, StepPreview, SimulationStepResult } from '../types';

export function SequencesPage() {
  const { sequenceName } = useParams<{ sequenceName?: string }>();
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);

  const { data: sequences, isLoading: listLoading, refetch } = useSequenceList();
  const { data: selectedSequence, isLoading: detailLoading } = useSequence(sequenceName ?? null);
  const deleteMutation = useDeleteSequence();
  const downloadMutation = useDownloadSequence();

  const handleSelectSequence = (name: string) => {
    navigate(getSequenceDetailRoute(name));
  };

  const handleCloseSequence = () => {
    navigate(ROUTES.SEQUENCES);
  };

  const handleUploadSuccess = () => {
    refetch();
    setShowUpload(false);
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete sequence "${name}"?`)) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(name);
      if (sequenceName === name) {
        navigate(ROUTES.SEQUENCES);
      }
    } catch (error) {
      console.error('Failed to delete sequence:', error);
    }
  };

  const handleDownload = async (name: string) => {
    try {
      await downloadMutation.mutateAsync(name);
    } catch (error) {
      console.error('Failed to download sequence:', error);
    }
  };

  if (listLoading) {
    return <LoadingOverlay message="Loading sequences..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Sequences</h2>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowUpload(!showUpload)}
        >
          <Upload className="w-4 h-4 mr-2" />
          {showUpload ? 'Cancel Upload' : 'Upload Package'}
        </Button>
      </div>

      {/* Upload Panel */}
      {showUpload && (
        <div className="rounded-lg border p-6" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
          <SequenceUpload
            onSuccess={handleUploadSuccess}
            onClose={() => setShowUpload(false)}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Sequence List */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Available Sequences ({sequences?.length ?? 0})</h3>
          <SequenceList
            sequences={sequences ?? []}
            selectedName={sequenceName}
            onSelect={handleSelectSequence}
            onDelete={handleDelete}
            onDownload={handleDownload}
            isDeleting={deleteMutation.isPending}
            isDownloading={downloadMutation.isPending}
          />
        </div>

        {/* Sequence Detail & Actions */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Sequence Details</h3>
          {sequenceName ? (
            <SequenceDetail
              sequence={selectedSequence ?? null}
              isLoading={detailLoading}
              onClose={handleCloseSequence}
              onDelete={() => handleDelete(sequenceName)}
              onDownload={() => handleDownload(sequenceName)}
            />
          ) : (
            <div className="p-8 rounded-lg border text-center" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
              <p style={{ color: 'var(--color-text-tertiary)' }}>Select a sequence to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface SequenceListProps {
  sequences: SequenceSummary[];
  selectedName?: string;
  onSelect: (name: string) => void;
  onDelete: (name: string) => void;
  onDownload: (name: string) => void;
  isDeleting: boolean;
  isDownloading: boolean;
}

function SequenceList({
  sequences,
  selectedName,
  onSelect,
  onDelete,
  onDownload,
  isDeleting,
  isDownloading,
}: SequenceListProps) {
  return (
    <div>
      {sequences.length === 0 ? (
        <div className="p-8 text-center rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)', color: 'var(--color-text-tertiary)' }}>
          <p>No sequence packages found</p>
          <p className="text-sm mt-2">Upload a package to get started</p>
        </div>
      ) : (
        <div className="space-y-2">
          {sequences.map((seq) => (
            <div
              key={seq.name}
              className="p-4 rounded-lg border transition-colors"
              style={{
                backgroundColor: selectedName === seq.name ? 'rgba(var(--color-brand-rgb), 0.1)' : 'var(--color-bg-secondary)',
                borderColor: selectedName === seq.name ? 'rgba(var(--color-brand-rgb), 0.5)' : 'var(--color-border-default)',
              }}
            >
              <button
                onClick={() => onSelect(seq.name)}
                className="w-full text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{seq.displayName}</h4>
                    <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>{seq.name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}>
                      v{seq.version}
                    </span>
                    <ChevronRight className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
                  </div>
                </div>
                {seq.description && (
                  <p className="text-sm mt-2 line-clamp-2" style={{ color: 'var(--color-text-secondary)' }}>{seq.description}</p>
                )}
              </button>

              {/* Action buttons */}
              <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDownload(seq.name);
                  }}
                  disabled={isDownloading}
                  className="flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors disabled:opacity-50"
                    style={{ color: 'var(--color-text-secondary)' }}
                >
                  <Download className="w-3 h-3" />
                  Download
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(seq.name);
                  }}
                  disabled={isDeleting}
                  className="flex items-center gap-1 px-2 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors disabled:opacity-50"
                >
                  <Trash2 className="w-3 h-3" />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface SequenceDetailProps {
  sequence: SequencePackage | null;
  isLoading: boolean;
  onClose: () => void;
  onDelete: () => void;
  onDownload: () => void;
}

function SequenceDetail({ sequence, isLoading, onClose, onDelete, onDownload }: SequenceDetailProps) {
  const [activeTab, setActiveTab] = useState<'steps' | 'params' | 'hardware' | 'test'>('steps');

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!sequence) {
    return null;
  }

  // Prepare default parameters for Test tab
  const defaultParameters = sequence.parameters.reduce(
    (acc, p) => ({ ...acc, [p.name]: p.default }),
    {}
  );

  return (
    <div className="rounded-lg border" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}>
      {/* Header */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>{sequence.displayName}</h3>
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              {sequence.name} v{sequence.version}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={onDownload}>
              <Download className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete} className="text-red-400 hover:text-red-300">
              <Trash2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
        {sequence.description && (
          <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary)' }}>{sequence.description}</p>
        )}
        {sequence.author && (
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>Author: {sequence.author}</p>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b" style={{ borderColor: 'var(--color-border-default)' }}>
        <TabButton
          active={activeTab === 'steps'}
          onClick={() => setActiveTab('steps')}
          icon={<ArrowRight className="w-4 h-4" />}
          label={`Steps (${sequence.steps.length})`}
        />
        <TabButton
          active={activeTab === 'params'}
          onClick={() => setActiveTab('params')}
          icon={<Settings2 className="w-4 h-4" />}
          label={`Parameters (${sequence.parameters.length})`}
        />
        <TabButton
          active={activeTab === 'hardware'}
          onClick={() => setActiveTab('hardware')}
          icon={<Cpu className="w-4 h-4" />}
          label={`Hardware (${sequence.hardware.length})`}
        />
        <TabButton
          active={activeTab === 'test'}
          onClick={() => setActiveTab('test')}
          icon={<Zap className="w-4 h-4" />}
          label="Test"
        />
      </div>

      {/* Content */}
      <div className="p-4 max-h-[500px] overflow-y-auto">
        {activeTab === 'steps' && <StepList steps={sequence.steps} />}
        {activeTab === 'params' && <ParameterList parameters={sequence.parameters} />}
        {activeTab === 'hardware' && <HardwareList hardware={sequence.hardware} />}
        {activeTab === 'test' && (
          <TestTabContent
            sequenceName={sequence.name}
            defaultParameters={defaultParameters}
          />
        )}
      </div>
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

function TabButton({ active, onClick, icon, label }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors"
      style={{
        color: active ? 'var(--color-brand-500)' : 'var(--color-text-secondary)',
        borderBottom: active ? '2px solid var(--color-brand-500)' : 'none',
      }}
    >
      {icon}
      {label}
    </button>
  );
}

function StepList({ steps }: { steps: StepSchema[] }) {
  if (steps.length === 0) {
    return <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No steps defined</p>;
  }

  return (
    <div className="space-y-2">
      {steps.map((step) => (
        <div
          key={step.name}
          className="flex items-center gap-3 p-3 rounded-lg"
          style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
        >
          <span className="w-6 h-6 flex items-center justify-center text-xs font-medium rounded-full" style={{ backgroundColor: 'var(--color-bg-secondary)', color: 'var(--color-text-secondary)' }}>
            {step.order}
          </span>
          <div className="flex-1">
            <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{step.displayName}</h4>
            <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{step.name}</p>
          </div>
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            <Clock className="w-3 h-3" />
            {step.timeout}s
          </div>
          {step.cleanup && (
            <span className="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
              cleanup
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

function ParameterList({ parameters }: { parameters: ParameterSchema[] }) {
  if (parameters.length === 0) {
    return <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No parameters defined</p>;
  }

  return (
    <div className="space-y-2">
      {parameters.map((param) => (
        <div key={param.name} className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{param.displayName}</h4>
              <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{param.name}</p>
            </div>
            <span className="text-xs px-2 py-0.5 rounded" style={{ backgroundColor: 'var(--color-bg-secondary)', color: 'var(--color-text-secondary)' }}>
              {param.type}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-4 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            <span>Default: {String(param.default ?? 'none')}</span>
            {param.min !== undefined && <span>Min: {param.min}</span>}
            {param.max !== undefined && <span>Max: {param.max}</span>}
            {param.unit && <span>Unit: {param.unit}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

function HardwareList({ hardware }: { hardware: HardwareSchema[] }) {
  if (hardware.length === 0) {
    return <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>No hardware defined</p>;
  }

  return (
    <div className="space-y-2">
      {hardware.map((hw) => (
        <div key={hw.id} className="p-3 rounded-lg" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{hw.displayName}</h4>
              <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{hw.id}</p>
            </div>
            <Cpu className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
          </div>
          <div className="mt-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            <span>Driver: {hw.driver}</span>
            <span className="ml-4">Class: {hw.className}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

// Test Tab Content (integrated from SimulationPanel)
interface TestTabContentProps {
  sequenceName: string;
  defaultParameters?: Record<string, unknown>;
}

function TestTabContent({ sequenceName, defaultParameters }: TestTabContentProps) {
  const [mode, setMode] = useState<SimulationMode>('preview');
  const [expanded, setExpanded] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);

  const simulation = useSimulation();

  const handleRun = async () => {
    try {
      const simResult = await simulation.mutateAsync({
        sequenceName,
        mode,
        parameters: defaultParameters,
      });
      setResult(simResult);
      setExpanded(true);
    } catch (error) {
      console.error('Simulation failed:', error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Mode Selection */}
      <div className="flex gap-2">
        <button
          onClick={() => setMode('preview')}
          className="flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-colors"
          style={{
            borderColor: mode === 'preview' ? 'var(--color-brand-500)' : 'var(--color-border-default)',
            backgroundColor: mode === 'preview' ? 'rgba(var(--color-brand-rgb), 0.1)' : 'var(--color-bg-tertiary)',
            color: mode === 'preview' ? 'var(--color-brand-500)' : 'var(--color-text-secondary)',
          }}
        >
          <Eye className="w-4 h-4" />
          <span className="text-sm font-medium">Preview</span>
        </button>
        <button
          onClick={() => setMode('dry_run')}
          className="flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border transition-colors"
          style={{
            borderColor: mode === 'dry_run' ? 'var(--color-brand-500)' : 'var(--color-border-default)',
            backgroundColor: mode === 'dry_run' ? 'rgba(var(--color-brand-rgb), 0.1)' : 'var(--color-bg-tertiary)',
            color: mode === 'dry_run' ? 'var(--color-brand-500)' : 'var(--color-text-secondary)',
          }}
        >
          <Play className="w-4 h-4" />
          <span className="text-sm font-medium">Dry Run</span>
        </button>
      </div>

      {/* Mode Description */}
      <p className="text-xs text-zinc-500">
        {mode === 'preview'
          ? 'View step information without executing any code.'
          : 'Execute sequence with mock hardware for testing.'}
      </p>

      {/* Run Button */}
      <Button
        variant="primary"
        className="w-full"
        onClick={handleRun}
        isLoading={simulation.isPending}
        disabled={simulation.isPending}
      >
        {simulation.isPending ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Running...
          </>
        ) : (
          <>
            <Play className="w-4 h-4 mr-2" />
            Run {mode === 'preview' ? 'Preview' : 'Dry Run'}
          </>
        )}
      </Button>

      {/* Error Display */}
      {simulation.isError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <XCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Simulation Failed</span>
          </div>
          <p className="text-xs text-red-300/80 mt-1">
            {(simulation.error as Error).message || 'Unknown error'}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="border rounded-lg overflow-hidden" style={{ borderColor: 'var(--color-border-default)' }}>
          {/* Result Header */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full p-3 flex items-center justify-between transition-colors"
            style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
          >
            <div className="flex items-center gap-2">
              {result.status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                {result.mode === 'preview' ? 'Preview' : 'Dry Run'} - {result.status}
              </span>
            </div>
            {expanded ? (
              <ChevronUp className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
            ) : (
              <ChevronDown className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
            )}
          </button>

          {/* Result Content */}
          {expanded && (
            <div className="p-3 space-y-3 max-h-64 overflow-y-auto">
              {/* Step Results */}
              {result.steps.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium uppercase" style={{ color: 'var(--color-text-secondary)' }}>Steps</h4>
                  {result.steps.map((step: StepPreview) => (
                    <StepPreviewItem
                      key={step.name}
                      step={step}
                      result={result.stepResults?.find(
                        (r: SimulationStepResult) => r.name === step.name
                      )}
                    />
                  ))}
                </div>
              )}

              {/* Error if any */}
              {result.error && (
                <div className="p-2 bg-red-500/10 rounded text-xs text-red-400">
                  Error: {result.error}
                </div>
              )}

              {/* Timing Info */}
              <div className="flex items-center gap-4 text-xs pt-2 border-t" style={{ color: 'var(--color-text-tertiary)', borderColor: 'var(--color-border-default)' }}>
                <span>ID: {result.id}</span>
                {result.completedAt && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(result.completedAt).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface StepPreviewItemProps {
  step: StepPreview;
  result?: SimulationStepResult;
}

function StepPreviewItem({ step, result }: StepPreviewItemProps) {
  return (
    <div className="flex items-center gap-3 p-2 rounded" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
      {/* Order badge */}
      <span
        className="w-5 h-5 flex items-center justify-center text-xs font-medium rounded-full"
        style={{
          backgroundColor: result?.status === 'passed'
            ? 'rgba(34, 197, 94, 0.2)'
            : result?.status === 'failed'
              ? 'rgba(239, 68, 68, 0.2)'
              : 'var(--color-bg-secondary)',
          color: result?.status === 'passed'
            ? '#4ade80'
            : result?.status === 'failed'
              ? '#f87171'
              : 'var(--color-text-secondary)',
        }}
      >
        {step.order}
      </span>

      {/* Step info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
            {step.displayName}
          </span>
          {step.cleanup && (
            <span className="text-xs px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
              cleanup
            </span>
          )}
        </div>
        {step.description && (
          <p className="text-xs truncate" style={{ color: 'var(--color-text-tertiary)' }}>{step.description}</p>
        )}
      </div>

      {/* Duration / Timeout */}
      <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
        <Clock className="w-3 h-3" />
        {result ? (
          <span className={result.status === 'passed' ? 'text-green-400' : 'text-red-400'}>
            {result.duration.toFixed(1)}s
          </span>
        ) : (
          <span>{step.timeout}s</span>
        )}
      </div>

      {/* Status icon */}
      {result && (
        result.status === 'passed' ? (
          <CheckCircle className="w-4 h-4 text-green-500" />
        ) : result.status === 'failed' ? (
          <XCircle className="w-4 h-4 text-red-500" />
        ) : null
      )}
    </div>
  );
}
