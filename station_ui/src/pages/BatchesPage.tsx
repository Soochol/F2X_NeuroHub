/**
 * Batches page - Batch monitoring and control.
 * Enhanced with create batch wizard and statistics panel.
 * Detail view is now a separate page (/batches/:batchId).
 */

import { useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Plus, WifiOff } from 'lucide-react';
import {
  useBatchList,
  useWebSocket,
  useSequenceList,
  useCreateBatches,
  useAllBatchStatistics,
} from '../hooks';
import { useBatchStore } from '../stores/batchStore';
import { useConnectionStore } from '../stores/connectionStore';
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
  const { data: allStatistics } = useAllBatchStatistics();
  const { subscribe, isConnected } = useWebSocket();

  // Connection status for Create Batch button
  const websocketStatus = useConnectionStore((state) => state.websocketStatus);
  const isServerConnected = isConnected && websocketStatus === 'connected';

  // Subscribe to both batches Map and version counter
  // The version counter ensures re-renders when Map contents change
  const batchesMap = useBatchStore((state) => state.batches);
  const batchesVersion = useBatchStore((state) => state.batchesVersion);
  const batchStatistics = useBatchStore((state) => state.batchStatistics);
  const setAllBatchStatistics = useBatchStore((state) => state.setAllBatchStatistics);
  const isWizardOpen = useBatchStore((state) => state.isWizardOpen);
  const openWizard = useBatchStore((state) => state.openWizard);
  const closeWizard = useBatchStore((state) => state.closeWizard);

  // Sync API statistics to store for real-time updates
  useEffect(() => {
    if (allStatistics) {
      setAllBatchStatistics(allStatistics);
    }
  }, [allStatistics, setAllBatchStatistics]);

  // Convert Map to array - batchesVersion in deps ensures recalculation on updates
  const storeBatches = useMemo(() => {
    const arr = Array.from(batchesMap.values());
    console.log(`[BatchesPage] storeBatches recalc: version=${batchesVersion}, size=${arr.length}`, arr.map(b => `${b.id.slice(0,8)}:${b.status}`));
    return arr;
  }, [batchesMap, batchesVersion]);

  const createBatches = useCreateBatches();

  // Subscribe to all batches for real-time updates
  // NOTE: We intentionally don't unsubscribe on cleanup because:
  // 1. React's cleanup runs BEFORE new component's effect, causing a gap where batches are unsubscribed
  // 2. During navigation, this gap causes missed WebSocket messages
  // 3. Subscriptions are idempotent and cleaned up on WebSocket disconnect
  useEffect(() => {
    if (batches && batches.length > 0) {
      const batchIds = batches.map((b) => b.id);
      subscribe(batchIds);
      // No cleanup - subscriptions persist across navigation
    }
  }, [batches, subscribe]);

  // Use store batches if available (more up-to-date from WebSocket)
  const displayBatches = storeBatches.length > 0 ? storeBatches : batches ?? [];

  const handleSelectBatch = (id: string) => {
    navigate(getBatchDetailRoute(id));
  };

  const handleCreateBatches = async (request: CreateBatchRequest) => {
    await createBatches.mutateAsync(request);
    closeWizard();
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

      {/* Batch List - Click to view details, controls only in detail page */}
      {/* key forces re-render when batch data changes */}
      <BatchList
        key={`batch-list-${batchesVersion}`}
        batches={displayBatches}
        statistics={batchStatistics}
        onSelect={handleSelectBatch}
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
