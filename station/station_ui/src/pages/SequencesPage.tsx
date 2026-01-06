/**
 * Sequences page - Unified sequence registry with local and remote sequences.
 */

import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  GitBranch,
  ChevronRight,
  Clock,
  Settings2,
  Cpu,
  ArrowRight,
  Download,
  Trash2,
  Zap,
  Play,
  Eye,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  CloudDownload,
  ArrowUpCircle,
  CircleDot,
  Circle,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  AlertTriangle,
  X,
} from 'lucide-react';
import {
  useSequenceRegistry,
  useSequence,
  useDeleteSequence,
  useDownloadSequence,
  usePullSequence,
  useSyncSequences,
  useSimulation,
  useAutoSyncStatus,
  useConfigureAutoSync,
} from '../hooks';
import { LoadingOverlay, LoadingSpinner } from '../components/atoms/LoadingSpinner';
import { toast } from '../utils/toast';
import { Button } from '../components/atoms/Button';
import { ROUTES, getSequenceDetailRoute } from '../constants';
import type {
  SequencePackage,
  SequenceRegistryItem,
  SequenceStatus,
  StepSchema,
  ParameterSchema,
  HardwareSchema,
  SimulationMode,
  SimulationResult,
  StepPreview,
  SimulationStepResult,
} from '../types';

// Filter options
type FilterOption = 'all' | 'installed' | 'updates' | 'not_installed';

export function SequencesPage() {
  const { sequenceName } = useParams<{ sequenceName?: string }>();
  const navigate = useNavigate();
  const [filter, setFilter] = useState<FilterOption>('all');
  const [dismissedWarning, setDismissedWarning] = useState(false);

  const { data: registryResponse, isLoading: listLoading } = useSequenceRegistry();
  const registry = registryResponse?.items;
  const warnings = registryResponse?.warnings;
  const { data: selectedSequence, isLoading: detailLoading } = useSequence(sequenceName ?? null);
  const deleteMutation = useDeleteSequence();
  const downloadMutation = useDownloadSequence();
  const pullMutation = usePullSequence();
  const syncMutation = useSyncSequences();

  // Auto-sync hooks
  const { data: autoSyncStatus } = useAutoSyncStatus();
  const configureAutoSync = useConfigureAutoSync();

  const handleToggleAutoSync = async () => {
    if (!autoSyncStatus) return;
    try {
      await configureAutoSync.mutateAsync({
        enabled: !autoSyncStatus.enabled,
        poll_interval: autoSyncStatus.pollInterval,
        auto_pull: autoSyncStatus.autoPull,
      });
      toast.success(`Auto-sync ${!autoSyncStatus.enabled ? '활성화' : '비활성화'}됨`);
    } catch {
      // Error handled by global mutation error handler
    }
  };

  // Filter sequences
  const filteredRegistry = useMemo(() => {
    if (!registry) return [];

    switch (filter) {
      case 'installed':
        return registry.filter((s) =>
          ['installed_latest', 'update_available', 'local_only'].includes(s.status)
        );
      case 'updates':
        return registry.filter((s) => s.status === 'update_available');
      case 'not_installed':
        return registry.filter((s) => s.status === 'not_installed');
      default:
        return registry;
    }
  }, [registry, filter]);

  // Count by status
  const counts = useMemo(() => {
    if (!registry) return { all: 0, installed: 0, updates: 0, not_installed: 0 };
    return {
      all: registry.length,
      installed: registry.filter((s) =>
        ['installed_latest', 'update_available', 'local_only'].includes(s.status)
      ).length,
      updates: registry.filter((s) => s.status === 'update_available').length,
      not_installed: registry.filter((s) => s.status === 'not_installed').length,
    };
  }, [registry]);

  const handleSelectSequence = (name: string) => {
    navigate(getSequenceDetailRoute(name));
  };

  const handleCloseSequence = () => {
    navigate(ROUTES.SEQUENCES);
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Are you sure you want to delete sequence "${name}"?`)) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(name);
      toast.success(`시퀀스 "${name}" 삭제 완료`);
      if (sequenceName === name) {
        navigate(ROUTES.SEQUENCES);
      }
    } catch {
      // Error handled by global mutation error handler
    }
  };

  const handleDownload = async (name: string) => {
    try {
      await downloadMutation.mutateAsync(name);
      toast.success(`시퀀스 "${name}" 다운로드 시작`);
    } catch {
      // Error handled by global mutation error handler
    }
  };

  const handlePull = async (name: string, force: boolean = false) => {
    try {
      const result = await pullMutation.mutateAsync({ name, force });
      if (result.updated) {
        toast.success(`시퀀스 "${name}" 업데이트 완료`);
      } else if (!result.needsUpdate) {
        toast.info(`시퀀스 "${name}"는 이미 최신 버전입니다`);
      } else {
        toast.success(`시퀀스 "${name}" 설치 완료`);
      }
    } catch {
      // Error handled by global mutation error handler
    }
  };

  const handleSyncAll = async () => {
    try {
      const result = await syncMutation.mutateAsync(undefined);
      if (result.sequencesFailed > 0) {
        toast.warning(`동기화 완료: ${result.sequencesUpdated}개 업데이트, ${result.sequencesFailed}개 실패`);
      } else if (result.sequencesUpdated > 0) {
        toast.success(`동기화 완료: ${result.sequencesUpdated}개 시퀀스 업데이트됨`);
      } else {
        toast.info('모든 시퀀스가 최신 상태입니다');
      }
    } catch {
      // Error handled by global mutation error handler
    }
  };

  if (listLoading) {
    return <LoadingOverlay message="Loading sequences..." />;
  }

  return (
    <div className="space-y-6">
      {/* Backend Connection Warning */}
      {warnings && warnings.length > 0 && !dismissedWarning && (
        <div
          className="flex items-start gap-3 p-4 rounded-lg border"
          style={{
            backgroundColor: 'rgba(251, 191, 36, 0.1)',
            borderColor: 'rgba(251, 191, 36, 0.3)',
          }}
        >
          <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-medium text-amber-500">백엔드 연결 문제</h4>
            {warnings.map((warning, index) => (
              <p key={index} className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                {warning}
              </p>
            ))}
          </div>
          <button
            onClick={() => setDismissedWarning(true)}
            className="p-1 rounded hover:bg-amber-500/20 transition-colors"
          >
            <X className="w-4 h-4 text-amber-500" />
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            Sequences
          </h2>
        </div>
        <div className="flex items-center gap-4">
          {/* Auto-sync toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleToggleAutoSync}
              disabled={configureAutoSync.isPending}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors"
              style={{
                backgroundColor: autoSyncStatus?.enabled
                  ? 'rgba(34, 197, 94, 0.1)'
                  : 'var(--color-bg-tertiary)',
                border: `1px solid ${autoSyncStatus?.enabled ? 'rgba(34, 197, 94, 0.3)' : 'var(--color-border-default)'}`,
              }}
            >
              {autoSyncStatus?.enabled ? (
                <ToggleRight className="w-5 h-5 text-green-500" />
              ) : (
                <ToggleLeft className="w-5 h-5" style={{ color: 'var(--color-text-secondary)' }} />
              )}
              <span
                className="text-sm font-medium"
                style={{ color: autoSyncStatus?.enabled ? '#22c55e' : 'var(--color-text-secondary)' }}
              >
                Auto-sync
              </span>
              {autoSyncStatus?.running && (
                <RefreshCw className="w-3 h-3 text-green-500 animate-spin" />
              )}
            </button>
            {autoSyncStatus?.enabled && autoSyncStatus.lastCheckAt && (
              <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                Last: {new Date(autoSyncStatus.lastCheckAt).toLocaleTimeString()}
              </span>
            )}
          </div>
          <Button
            variant="secondary"
            onClick={handleSyncAll}
            disabled={syncMutation.isPending}
          >
            {syncMutation.isPending ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <CloudDownload className="w-4 h-4 mr-2" />
            )}
            Sync All
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        <FilterTab
          label="All"
          count={counts.all}
          active={filter === 'all'}
          onClick={() => setFilter('all')}
        />
        <FilterTab
          label="Installed"
          count={counts.installed}
          active={filter === 'installed'}
          onClick={() => setFilter('installed')}
        />
        <FilterTab
          label="Updates"
          count={counts.updates}
          active={filter === 'updates'}
          onClick={() => setFilter('updates')}
          highlight={counts.updates > 0}
        />
        <FilterTab
          label="Not Installed"
          count={counts.not_installed}
          active={filter === 'not_installed'}
          onClick={() => setFilter('not_installed')}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Sequence List */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {filter === 'all'
              ? `All Sequences (${filteredRegistry.length})`
              : filter === 'installed'
              ? `Installed (${filteredRegistry.length})`
              : filter === 'updates'
              ? `Updates Available (${filteredRegistry.length})`
              : `Available to Install (${filteredRegistry.length})`}
          </h3>
          <SequenceList
            sequences={filteredRegistry}
            selectedName={sequenceName}
            onSelect={handleSelectSequence}
            onDelete={handleDelete}
            onDownload={handleDownload}
            onPull={handlePull}
            isDeleting={deleteMutation.isPending}
            isDownloading={downloadMutation.isPending}
            isPulling={pullMutation.isPending}
          />
        </div>

        {/* Sequence Detail & Actions */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            Sequence Details
          </h3>
          {sequenceName ? (
            <SequenceDetail
              sequence={selectedSequence ?? null}
              registryItem={registryResponse?.items?.find((r) => r.name === sequenceName) ?? null}
              isLoading={detailLoading}
              onClose={handleCloseSequence}
              onDelete={() => handleDelete(sequenceName)}
              onDownload={() => handleDownload(sequenceName)}
              onPull={(force) => handlePull(sequenceName, force)}
              isPulling={pullMutation.isPending}
            />
          ) : (
            <div
              className="p-8 rounded-lg border text-center"
              style={{
                backgroundColor: 'var(--color-bg-secondary)',
                borderColor: 'var(--color-border-default)',
              }}
            >
              <p style={{ color: 'var(--color-text-tertiary)' }}>Select a sequence to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Filter Tab Component
// ============================================================================

interface FilterTabProps {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
  highlight?: boolean;
}

function FilterTab({ label, count, active, onClick, highlight }: FilterTabProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      style={{
        backgroundColor: active ? 'var(--color-brand-500)' : 'var(--color-bg-secondary)',
        color: active ? 'white' : highlight ? 'var(--color-warning-text)' : 'var(--color-text-secondary)',
        border: `1px solid ${active ? 'var(--color-brand-500)' : highlight ? 'var(--color-warning-border)' : 'var(--color-border-default)'}`,
      }}
    >
      {label}
      <span
        className="ml-2 px-2 py-0.5 rounded-full text-xs"
        style={{
          backgroundColor: active ? 'rgba(255,255,255,0.2)' : 'var(--color-bg-tertiary)',
        }}
      >
        {count}
      </span>
    </button>
  );
}

// ============================================================================
// Status Badge Component
// ============================================================================

function StatusBadge({ status }: { status: SequenceStatus }) {
  const config = {
    installed_latest: {
      icon: CheckCircle,
      label: 'Up to date',
      color: 'text-green-500',
      bg: 'bg-green-500/10',
    },
    update_available: {
      icon: ArrowUpCircle,
      label: 'Update available',
      color: 'text-amber-500',
      bg: 'bg-amber-500/10',
    },
    not_installed: {
      icon: Circle,
      label: 'Not installed',
      color: 'text-zinc-400',
      bg: 'bg-zinc-500/10',
    },
    local_only: {
      icon: CircleDot,
      label: 'Local only',
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
    },
  };

  const { icon: Icon, label, color, bg } = config[status];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs ${color} ${bg}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}

// ============================================================================
// Sequence List Component
// ============================================================================

interface SequenceListProps {
  sequences: SequenceRegistryItem[];
  selectedName?: string;
  onSelect: (name: string) => void;
  onDelete: (name: string) => void;
  onDownload: (name: string) => void;
  onPull: (name: string, force?: boolean) => void;
  isDeleting: boolean;
  isDownloading: boolean;
  isPulling: boolean;
}

function SequenceList({
  sequences,
  selectedName,
  onSelect,
  onDelete,
  onDownload,
  onPull,
  isDeleting,
  isDownloading,
  isPulling,
}: SequenceListProps) {
  return (
    <div>
      {sequences.length === 0 ? (
        <div
          className="p-8 text-center rounded-lg border"
          style={{
            backgroundColor: 'var(--color-bg-secondary)',
            borderColor: 'var(--color-border-default)',
            color: 'var(--color-text-tertiary)',
          }}
        >
          <p>No sequences found</p>
          <p className="text-sm mt-2">Try a different filter or sync from server</p>
        </div>
      ) : (
        <div className="space-y-2">
          {sequences.map((seq) => (
            <div
              key={seq.name}
              className="p-4 rounded-lg border transition-colors"
              style={{
                backgroundColor:
                  selectedName === seq.name
                    ? 'rgba(var(--color-brand-rgb), 0.1)'
                    : 'var(--color-bg-secondary)',
                borderColor:
                  selectedName === seq.name
                    ? 'rgba(var(--color-brand-rgb), 0.5)'
                    : 'var(--color-border-default)',
              }}
            >
              <button onClick={() => onSelect(seq.name)} className="w-full text-left">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                        {seq.displayName || seq.name}
                      </h4>
                      <StatusBadge status={seq.status} />
                    </div>
                    <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                      {seq.name}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <VersionDisplay item={seq} />
                    <ChevronRight className="w-4 h-4" style={{ color: 'var(--color-text-secondary)' }} />
                  </div>
                </div>
                {seq.description && (
                  <p className="text-sm mt-2 line-clamp-2" style={{ color: 'var(--color-text-secondary)' }}>
                    {seq.description}
                  </p>
                )}
              </button>

              {/* Action buttons */}
              <div className="flex gap-2 mt-3 pt-3 border-t" style={{ borderColor: 'var(--color-border-subtle)' }}>
                {/* Install/Update button */}
                {seq.status === 'not_installed' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onPull(seq.name);
                    }}
                    disabled={isPulling}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors text-brand-400 hover:text-brand-300 hover:bg-brand-500/10 disabled:opacity-50"
                  >
                    <CloudDownload className="w-3 h-3" />
                    Install
                  </button>
                )}
                {seq.status === 'update_available' && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onPull(seq.name);
                    }}
                    disabled={isPulling}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors text-amber-400 hover:text-amber-300 hover:bg-amber-500/10 disabled:opacity-50"
                  >
                    <ArrowUpCircle className="w-3 h-3" />
                    Update
                  </button>
                )}

                {/* Download (for installed sequences) */}
                {['installed_latest', 'update_available', 'local_only'].includes(seq.status) && (
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
                )}

                {/* Delete (for installed sequences) */}
                {['installed_latest', 'update_available', 'local_only'].includes(seq.status) && (
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
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Version Display Component
// ============================================================================

function VersionDisplay({ item }: { item: SequenceRegistryItem }) {
  if (item.status === 'update_available') {
    return (
      <div className="flex items-center gap-1 text-xs">
        <span style={{ color: 'var(--color-text-tertiary)' }}>v{item.localVersion}</span>
        <ArrowRight className="w-3 h-3 text-amber-500" />
        <span className="text-amber-500">v{item.remoteVersion}</span>
      </div>
    );
  }

  if (item.status === 'not_installed') {
    return (
      <span
        className="text-xs px-2 py-1 rounded"
        style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
      >
        v{item.remoteVersion}
      </span>
    );
  }

  return (
    <span
      className="text-xs px-2 py-1 rounded"
      style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
    >
      v{item.localVersion}
    </span>
  );
}

// ============================================================================
// Sequence Detail Component
// ============================================================================

interface SequenceDetailProps {
  sequence: SequencePackage | null;
  registryItem: SequenceRegistryItem | null;
  isLoading: boolean;
  onClose: () => void;
  onDelete: () => void;
  onDownload: () => void;
  onPull: (force: boolean) => void;
  isPulling: boolean;
}

function SequenceDetail({
  sequence,
  registryItem,
  isLoading,
  onClose,
  onDelete,
  onDownload,
  onPull,
  isPulling,
}: SequenceDetailProps) {
  const [activeTab, setActiveTab] = useState<'steps' | 'params' | 'hardware' | 'test'>('steps');

  if (isLoading) {
    return (
      <div
        className="p-8 flex items-center justify-center rounded-lg border"
        style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}
      >
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Show install prompt if not installed
  if (registryItem?.status === 'not_installed') {
    return (
      <div
        className="p-8 rounded-lg border text-center"
        style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}
      >
        <CloudDownload className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--color-text-tertiary)' }} />
        <h4 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>
          {registryItem.displayName || registryItem.name}
        </h4>
        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
          {registryItem.description || 'This sequence is not installed yet.'}
        </p>
        <Button variant="primary" onClick={() => onPull(false)} disabled={isPulling}>
          {isPulling ? (
            <LoadingSpinner size="sm" className="mr-2" />
          ) : (
            <CloudDownload className="w-4 h-4 mr-2" />
          )}
          Install v{registryItem.remoteVersion}
        </Button>
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
    <div
      className="rounded-lg border"
      style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border-default)' }}
    >
      {/* Header */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--color-border-default)' }}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                {sequence.displayName}
              </h3>
              {registryItem && <StatusBadge status={registryItem.status} />}
            </div>
            <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
              {sequence.name} v{sequence.version}
              {registryItem?.status === 'update_available' && (
                <span className="text-amber-500 ml-2">
                  (v{registryItem.remoteVersion} available)
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {registryItem?.status === 'update_available' && (
              <Button variant="primary" size="sm" onClick={() => onPull(false)} disabled={isPulling}>
                {isPulling ? <LoadingSpinner size="sm" /> : <ArrowUpCircle className="w-4 h-4" />}
              </Button>
            )}
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
          <p className="text-sm mt-2" style={{ color: 'var(--color-text-secondary)' }}>
            {sequence.description}
          </p>
        )}
        {sequence.author && (
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
            Author: {sequence.author}
          </p>
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
          <TestTabContent sequenceName={sequence.name} defaultParameters={defaultParameters} />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Tab Button Component
// ============================================================================

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

// ============================================================================
// Step List Component
// ============================================================================

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
          <span
            className="w-6 h-6 flex items-center justify-center text-xs font-medium rounded-full"
            style={{ backgroundColor: 'var(--color-bg-secondary)', color: 'var(--color-text-secondary)' }}
          >
            {step.order}
          </span>
          <div className="flex-1">
            <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
              {step.displayName}
            </h4>
            <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              {step.name}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            <Clock className="w-3 h-3" />
            {step.timeout}s
          </div>
          {step.cleanup && (
            <span
              className="text-xs px-2 py-0.5 rounded"
              style={{ backgroundColor: 'var(--color-warning-bg)', color: 'var(--color-warning-text)' }}
            >
              cleanup
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// Parameter List Component
// ============================================================================

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
              <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                {param.displayName}
              </h4>
              <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                {param.name}
              </p>
            </div>
            <span
              className="text-xs px-2 py-0.5 rounded"
              style={{ backgroundColor: 'var(--color-bg-secondary)', color: 'var(--color-text-secondary)' }}
            >
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

// ============================================================================
// Hardware List Component
// ============================================================================

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
              <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                {hw.displayName}
              </h4>
              <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                {hw.id}
              </p>
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

// ============================================================================
// Test Tab Content
// ============================================================================

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
      if (simResult.status === 'completed') {
        toast.success(`${mode === 'preview' ? 'Preview' : 'Dry run'} 완료`);
      }
    } catch {
      // Error handled by global mutation error handler
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
          'Running...'
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
                  <h4 className="text-xs font-medium uppercase" style={{ color: 'var(--color-text-secondary)' }}>
                    Steps
                  </h4>
                  {result.steps.map((step: StepPreview) => (
                    <StepPreviewItem
                      key={step.name}
                      step={step}
                      result={result.stepResults?.find((r: SimulationStepResult) => r.name === step.name)}
                    />
                  ))}
                </div>
              )}

              {/* Error if any */}
              {result.error && (
                <div className="p-2 bg-red-500/10 rounded text-xs text-red-400">Error: {result.error}</div>
              )}

              {/* Timing Info */}
              <div
                className="flex items-center gap-4 text-xs pt-2 border-t"
                style={{ color: 'var(--color-text-tertiary)', borderColor: 'var(--color-border-default)' }}
              >
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

// ============================================================================
// Step Preview Item
// ============================================================================

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
          backgroundColor:
            result?.status === 'passed'
              ? 'rgba(34, 197, 94, 0.2)'
              : result?.status === 'failed'
              ? 'rgba(239, 68, 68, 0.2)'
              : 'var(--color-bg-secondary)',
          color:
            result?.status === 'passed'
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
            <span
              className="text-xs px-1.5 py-0.5 rounded"
              style={{ backgroundColor: 'var(--color-warning-bg)', color: 'var(--color-warning-text)' }}
            >
              cleanup
            </span>
          )}
        </div>
        {step.description && (
          <p className="text-xs truncate" style={{ color: 'var(--color-text-tertiary)' }}>
            {step.description}
          </p>
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
      {result &&
        (result.status === 'passed' ? (
          <CheckCircle className="w-4 h-4 text-green-500" />
        ) : result.status === 'failed' ? (
          <XCircle className="w-4 h-4 text-red-500" />
        ) : null)}
    </div>
  );
}
