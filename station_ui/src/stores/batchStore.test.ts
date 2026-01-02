/**
 * Unit tests for batchStore.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useBatchStore } from './batchStore';
import type { Batch, BatchStatus } from '../types';

// Helper to create a mock batch
function createMockBatch(overrides: Partial<Batch> = {}): Batch {
  return {
    id: 'test-batch-id-123',
    name: 'Test Batch',
    status: 'idle' as BatchStatus,
    progress: 0,
    sequencePackage: 'test-sequence',
    elapsed: 0,
    hardwareConfig: {},
    autoStart: false,
    steps: [],
    ...overrides,
  };
}

describe('batchStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useBatchStore.setState({
      batches: new Map(),
      batchesVersion: 0,
      selectedBatchId: null,
      batchStatistics: new Map(),
      isWizardOpen: false,
    });
  });

  describe('setBatches', () => {
    it('should set batches from API response', () => {
      const batches = [
        createMockBatch({ id: 'batch-1', name: 'Batch 1' }),
        createMockBatch({ id: 'batch-2', name: 'Batch 2' }),
      ];

      useBatchStore.getState().setBatches(batches);

      const state = useBatchStore.getState();
      expect(state.batches.size).toBe(2);
      expect(state.batches.get('batch-1')?.name).toBe('Batch 1');
      expect(state.batches.get('batch-2')?.name).toBe('Batch 2');
      expect(state.batchesVersion).toBe(1);
    });

    it('should prevent status regression from completed to non-completed', () => {
      // First set a completed batch
      const completedBatch = createMockBatch({
        id: 'batch-1',
        status: 'completed',
        progress: 1,
      });
      useBatchStore.getState().setBatches([completedBatch]);

      // Try to regress status via API update
      const idleBatch = createMockBatch({
        id: 'batch-1',
        status: 'idle',
        progress: 0,
      });
      useBatchStore.getState().setBatches([idleBatch]);

      // Status should still be completed
      const batch = useBatchStore.getState().batches.get('batch-1');
      expect(batch?.status).toBe('completed');
    });

    it('should preserve WebSocket state for running batches', () => {
      // First set a running batch with WebSocket updates
      const runningBatch = createMockBatch({
        id: 'batch-1',
        status: 'running',
        progress: 0.5,
        currentStep: 'step-2',
        executionId: 'exec-123',
      });
      useBatchStore.getState().setBatches([runningBatch]);

      // API update with stale data
      const apiBatch = createMockBatch({
        id: 'batch-1',
        status: 'running',
        progress: 0.25, // Stale progress
        currentStep: 'step-1', // Stale step
      });
      useBatchStore.getState().setBatches([apiBatch]);

      // WebSocket state should be preserved
      const batch = useBatchStore.getState().batches.get('batch-1');
      expect(batch?.progress).toBe(0.5);
      expect(batch?.currentStep).toBe('step-2');
    });
  });

  describe('updateBatchStatus', () => {
    it('should update batch status', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'idle' });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().updateBatchStatus('batch-1', 'running', 'exec-123');

      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.status).toBe('running');
      expect(updated?.executionId).toBe('exec-123');
    });

    it('should set progress to 100% when status changes to completed', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'running', progress: 0.8 });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().updateBatchStatus('batch-1', 'completed');

      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.status).toBe('completed');
      expect(updated?.progress).toBe(1.0);
    });

    it('should block regression from completed to non-completed (except error/starting)', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'completed' });
      useBatchStore.getState().setBatches([batch]);

      // This should be blocked
      useBatchStore.getState().updateBatchStatus('batch-1', 'idle');
      expect(useBatchStore.getState().batches.get('batch-1')?.status).toBe('completed');

      // Error should be allowed
      useBatchStore.getState().updateBatchStatus('batch-1', 'error');
      expect(useBatchStore.getState().batches.get('batch-1')?.status).toBe('error');
    });

    it('should create minimal batch if batch does not exist', () => {
      useBatchStore.getState().updateBatchStatus('new-batch', 'running', 'exec-123');

      const batch = useBatchStore.getState().batches.get('new-batch');
      expect(batch).toBeDefined();
      expect(batch?.status).toBe('running');
      expect(batch?.name).toBe('Loading...');
    });
  });

  describe('updateStepProgress', () => {
    it('should update step progress', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'running' });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().updateStepProgress('batch-1', 'step-2', 1, 0.5, 'exec-123');

      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.currentStep).toBe('step-2');
      expect(updated?.stepIndex).toBe(1);
      expect(updated?.progress).toBe(0.5);
    });

    it('should prevent progress regression', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'running', progress: 0.8 });
      useBatchStore.getState().setBatches([batch]);

      // Try to regress progress
      useBatchStore.getState().updateStepProgress('batch-1', 'step-2', 1, 0.5);

      // Progress should be max of old and new
      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.progress).toBe(0.8);
    });

    it('should ignore updates with mismatched executionId', () => {
      const batch = createMockBatch({
        id: 'batch-1',
        status: 'running',
        progress: 0.5,
        executionId: 'exec-123',
      });
      useBatchStore.getState().setBatches([batch]);

      // Update with different executionId
      useBatchStore.getState().updateStepProgress('batch-1', 'step-5', 4, 0.9, 'exec-456');

      // Should be ignored
      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.progress).toBe(0.5);
    });
  });

  describe('startStep', () => {
    it('should add step to steps array', () => {
      const batch = createMockBatch({ id: 'batch-1', status: 'running', steps: [] });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().startStep('batch-1', 'step-1', 0, 5, 'exec-123');

      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.steps).toHaveLength(1);
      expect(updated?.steps?.[0]?.name).toBe('step-1');
      expect(updated?.steps?.[0]?.status).toBe('running');
    });

    it('should create batch if not exists', () => {
      useBatchStore.getState().startStep('new-batch', 'step-1', 0, 5, 'exec-123');

      const batch = useBatchStore.getState().batches.get('new-batch');
      expect(batch).toBeDefined();
      expect(batch?.steps).toHaveLength(1);
    });
  });

  describe('completeStep', () => {
    it('should mark step as completed with result', () => {
      const batch = createMockBatch({
        id: 'batch-1',
        status: 'running',
        steps: [{ order: 1, name: 'step-1', status: 'running' as const, pass: false }],
        totalSteps: 2,
      });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().completeStep('batch-1', 'step-1', 0, 1.5, true, { value: 42 });

      const updated = useBatchStore.getState().batches.get('batch-1');
      expect(updated?.steps?.[0]?.status).toBe('completed');
      expect(updated?.steps?.[0]?.pass).toBe(true);
      expect(updated?.steps?.[0]?.duration).toBe(1.5);
      expect(updated?.steps?.[0]?.result).toEqual({ value: 42 });
    });

    it('should calculate progress based on completed steps', () => {
      const batch = createMockBatch({
        id: 'batch-1',
        status: 'running',
        steps: [{ order: 1, name: 'step-1', status: 'running' as const, pass: false }],
        totalSteps: 4,
      });
      useBatchStore.getState().setBatches([batch]);

      useBatchStore.getState().completeStep('batch-1', 'step-1', 0, 1.0, true);

      const updated = useBatchStore.getState().batches.get('batch-1');
      // 1 completed out of 4 total
      expect(updated?.progress).toBe(0.25);
    });
  });

  describe('selectors', () => {
    it('getAllBatches should return array of batches', () => {
      useBatchStore.getState().setBatches([
        createMockBatch({ id: 'batch-1' }),
        createMockBatch({ id: 'batch-2' }),
      ]);

      const batches = useBatchStore.getState().getAllBatches();
      expect(batches).toHaveLength(2);
    });

    it('getRunningBatches should return only running batches', () => {
      useBatchStore.getState().setBatches([
        createMockBatch({ id: 'batch-1', status: 'running' }),
        createMockBatch({ id: 'batch-2', status: 'idle' }),
        createMockBatch({ id: 'batch-3', status: 'running' }),
      ]);

      const running = useBatchStore.getState().getRunningBatches();
      expect(running).toHaveLength(2);
      expect(running.every((b) => b.status === 'running')).toBe(true);
    });

    it('getSelectedBatch should return selected batch', () => {
      useBatchStore.getState().setBatches([
        createMockBatch({ id: 'batch-1', name: 'Selected' }),
        createMockBatch({ id: 'batch-2', name: 'Other' }),
      ]);
      useBatchStore.getState().selectBatch('batch-1');

      const selected = useBatchStore.getState().getSelectedBatch();
      expect(selected?.name).toBe('Selected');
    });
  });

  describe('statistics', () => {
    it('should set and get batch statistics', () => {
      useBatchStore.getState().setBatchStatistics('batch-1', {
        total: 10,
        passCount: 8,
        fail: 2,
        passRate: 0.8,
      });

      const stats = useBatchStore.getState().getBatchStats('batch-1');
      expect(stats?.total).toBe(10);
      expect(stats?.passRate).toBe(0.8);
    });

    it('should increment batch stats', () => {
      useBatchStore.getState().setBatchStatistics('batch-1', {
        total: 10,
        passCount: 8,
        fail: 2,
        passRate: 0.8,
      });

      useBatchStore.getState().incrementBatchStats('batch-1', true);

      const stats = useBatchStore.getState().getBatchStats('batch-1');
      expect(stats?.total).toBe(11);
      expect(stats?.passCount).toBe(9);
    });

    it('getTotalStats should aggregate all batch stats', () => {
      useBatchStore.getState().setBatchStatistics('batch-1', {
        total: 10,
        passCount: 8,
        fail: 2,
        passRate: 0.8,
      });
      useBatchStore.getState().setBatchStatistics('batch-2', {
        total: 20,
        passCount: 15,
        fail: 5,
        passRate: 0.75,
      });

      const total = useBatchStore.getState().getTotalStats();
      expect(total.total).toBe(30);
      expect(total.passCount).toBe(23);
      expect(total.fail).toBe(7);
    });
  });
});
