/**
 * Batches page - Batch monitoring and control.
 * Enhanced with create batch wizard and statistics panel.
 * Detail view is now a separate page (/batches/:batchId).
 */

import { useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Plus } from 'lucide-react';
import {
  useBatchList,
  useStartBatch,
  useStopBatch,
  useStartSequence,
  useStopSequence,
  useWebSocket,
  useSequenceList,
  useCreateBatches,
} from '../hooks';
import { useBatchStore } from '../stores/batchStore';
import { useShallow } from 'zustand/react/shallow';
import { BatchList } from '../components/organisms/batches/BatchList';
import { CreateBatchWizard } from '../components/organisms/batches/CreateBatchWizard';
import { BatchStatisticsPanel } from '../components/organisms/batches/BatchStatisticsPanel';
import { Button } from '../components/atoms/Button';
import { LoadingOverlay } from '../components/atoms/LoadingSpinner';
import { getBatchDetailRoute } from '../constants';
import type { CreateBatchRequest, SequencePackage } from '../types';
import { getSequence } from '../api/endpoints/sequences';

export function BatchesPage() {
  const navigate = useNavigate();

  const { data: batches, isLoading: batchesLoading } = useBatchList();
  const { data: sequences } = useSequenceList();
  const { subscribe, unsubscribe } = useWebSocket();

  // Use useShallow to prevent re-renders when map contents haven't changed
  const batchesMap = useBatchStore(useShallow((state) => state.batches));
  const localBatches = useBatchStore(useShallow((state) => state.localBatches));
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));
  const localBatchStats = useBatchStore(useShallow((state) => state.localBatchStats));
  const isWizardOpen = useBatchStore((state) => state.isWizardOpen);
  const openWizard = useBatchStore((state) => state.openWizard);
  const closeWizard = useBatchStore((state) => state.closeWizard);
  const removeLocalBatch = useBatchStore((state) => state.removeLocalBatch);
  const clearLocalBatchSteps = useBatchStore((state) => state.clearLocalBatchSteps);

  // Combine API batches and local batches
  const storeBatches = useMemo(() => {
    const apiBatches = Array.from(batchesMap.values());
    const localBatchArray = Array.from(localBatches.values());
    return [...apiBatches, ...localBatchArray];
  }, [batchesMap, localBatches]);

  // Combine statistics from both sources
  const combinedStatistics = useMemo(() => {
    const combined = new Map<string, { total: number; pass: number; fail: number; passRate: number }>();
    batchStatistics.forEach((stats, id) => combined.set(id, stats));
    localBatchStats.forEach((stats, id) => combined.set(id, stats));
    return combined;
  }, [batchStatistics, localBatchStats]);

  const startBatch = useStartBatch();
  const stopBatch = useStopBatch();
  const startSequence = useStartSequence();
  const stopSequence = useStopSequence();
  const createBatches = useCreateBatches();

  // Subscribe to all batches for real-time updates
  useEffect(() => {
    if (batches && batches.length > 0) {
      const batchIds = batches.map((b) => b.id);
      subscribe(batchIds);
      return () => unsubscribe(batchIds);
    }
  }, [batches, subscribe, unsubscribe]);

  // Use store batches if available (more up-to-date from WebSocket)
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches ?? [];

  const handleSelectBatch = (id: string) => {
    navigate(getBatchDetailRoute(id));
  };

  const handleStartBatch = async (id: string) => {
    // For local batches, use startSequence which handles simulation
    if (id.startsWith('local-batch-')) {
      await startSequence.mutateAsync({ batchId: id, request: undefined });
    } else {
      await startBatch.mutateAsync(id);
    }
  };

  const handleStopBatch = async (id: string) => {
    // For local batches, use stopSequence
    if (id.startsWith('local-batch-')) {
      await stopSequence.mutateAsync(id);
    } else {
      await stopBatch.mutateAsync(id);
    }
  };

  const handleCreateBatches = async (request: CreateBatchRequest) => {
    await createBatches.mutateAsync(request);
    closeWizard();
  };

  const handleDeleteBatch = (id: string) => {
    if (id.startsWith('local-batch-') && window.confirm('Are you sure you want to delete this batch?')) {
      clearLocalBatchSteps(id);
      removeLocalBatch(id);
    }
  };

  const getSequenceDetail = useCallback(async (name: string): Promise<SequencePackage> => {
    return getSequence(name);
  }, []);

  if (batchesLoading) {
    return <LoadingOverlay message="Loading batches..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Layers className="w-6 h-6 text-brand-500" />
          <h2 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Batches</h2>
        </div>
        <Button variant="primary" onClick={openWizard}>
          <Plus className="w-4 h-4 mr-2" />
          Create Batch
        </Button>
      </div>

      {/* Statistics Panel */}
      <BatchStatisticsPanel batches={displayBatches} statistics={combinedStatistics} />

      {/* Batch List */}
      <BatchList
        batches={displayBatches}
        onStart={handleStartBatch}
        onStop={handleStopBatch}
        onDelete={handleDeleteBatch}
        onSelect={handleSelectBatch}
        isLoading={startBatch.isPending || stopBatch.isPending || startSequence.isPending || stopSequence.isPending}
      />

      {/* Create Batch Wizard Modal */}
      <CreateBatchWizard
        isOpen={isWizardOpen}
        onClose={closeWizard}
        onSubmit={handleCreateBatches}
        sequences={sequences ?? []}
        getSequenceDetail={getSequenceDetail}
        isSubmitting={createBatches.isPending}
      />
    </div>
  );
}
