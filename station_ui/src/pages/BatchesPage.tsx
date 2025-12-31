/**
 * Batches page - Batch monitoring and control.
 * Enhanced with create batch wizard and statistics panel.
 * Detail view is now a separate page (/batches/:batchId).
 */

import { useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Plus, WifiOff } from 'lucide-react';
import {
  useBatchList,
  useStartBatch,
  useStopBatch,
  useDeleteBatch,
  useWebSocket,
  useSequenceList,
  useCreateBatches,
} from '../hooks';
import { useBatchStore } from '../stores/batchStore';
import { useConnectionStore } from '../stores/connectionStore';
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
  const { subscribe, unsubscribe, isConnected } = useWebSocket();

  // Connection status for Create Batch button
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const isServerConnected = isConnected && websocketStatus === 'connected';

  // Use useShallow to prevent re-renders when map contents haven't changed
  const batchesMap = useBatchStore(useShallow((state) => state.batches));
  const batchStatistics = useBatchStore(useShallow((state) => state.batchStatistics));
  const isWizardOpen = useBatchStore((state) => state.isWizardOpen);
  const openWizard = useBatchStore((state) => state.openWizard);
  const closeWizard = useBatchStore((state) => state.closeWizard);

  // Get server batches only (no local batches)
  const storeBatches = useMemo(() => {
    return Array.from(batchesMap.values());
  }, [batchesMap]);

  const startBatch = useStartBatch();
  const stopBatch = useStopBatch();
  const deleteBatch = useDeleteBatch();
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
    await startBatch.mutateAsync(id);
  };

  const handleStopBatch = async (id: string) => {
    await stopBatch.mutateAsync(id);
  };

  const handleCreateBatches = async (request: CreateBatchRequest) => {
    await createBatches.mutateAsync(request);
    closeWizard();
  };

  const handleDeleteBatch = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this batch?')) {
      await deleteBatch.mutateAsync(id);
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
        <div className="flex items-center gap-3">
          {!isServerConnected && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-amber-500/10 border border-amber-500/30">
              <WifiOff className="w-4 h-4 text-amber-500" />
              <span className="text-sm text-amber-500">Server disconnected</span>
            </div>
          )}
          <Button
            variant="primary"
            onClick={openWizard}
            disabled={!isServerConnected}
            title={!isServerConnected ? 'Server connection required to create batches' : undefined}
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Batch
          </Button>
        </div>
      </div>

      {/* Statistics Panel */}
      <BatchStatisticsPanel batches={displayBatches} statistics={batchStatistics} />

      {/* Batch List */}
      <BatchList
        batches={displayBatches}
        onStart={handleStartBatch}
        onStop={handleStopBatch}
        onDelete={handleDeleteBatch}
        onSelect={handleSelectBatch}
        isLoading={startBatch.isPending || stopBatch.isPending || deleteBatch.isPending}
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
