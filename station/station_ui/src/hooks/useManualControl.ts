/**
 * Manual Control Hooks
 *
 * React Query hooks for enhanced manual hardware control.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getBatchHardware,
  getHardwareCommands,
  getManualSteps,
  runManualStep,
  skipManualStep,
  resetManualSequence,
  listPresets,
  createPreset,
  deletePreset,
} from '../api/endpoints/manual';
import { manualControl } from '../api/endpoints/batches';
import { useManualControlStore } from '../stores/manualControlStore';
import { toast, getErrorMessage } from '../utils';
import type {
  ManualControlRequest,
  CreatePresetRequest,
  CommandInfo,
} from '../types';

/**
 * Query keys for manual control.
 */
export const manualQueryKeys = {
  hardware: (batchId: string) => ['manual', 'hardware', batchId] as const,
  commands: (batchId: string, hardwareId: string) =>
    ['manual', 'commands', batchId, hardwareId] as const,
  steps: (batchId: string) => ['manual', 'steps', batchId] as const,
  presets: () => ['manual', 'presets'] as const,
};

/**
 * Hook to fetch hardware devices for a batch.
 */
export function useBatchHardware(batchId: string | null) {
  return useQuery({
    queryKey: manualQueryKeys.hardware(batchId ?? ''),
    queryFn: () => getBatchHardware(batchId!),
    enabled: !!batchId,
    staleTime: 10 * 1000, // 10 seconds
  });
}

/**
 * Hook to fetch available commands for a hardware device.
 */
export function useHardwareCommands(
  batchId: string | null,
  hardwareId: string | null
) {
  return useQuery({
    queryKey: manualQueryKeys.commands(batchId ?? '', hardwareId ?? ''),
    queryFn: () => getHardwareCommands(batchId!, hardwareId!),
    enabled: !!batchId && !!hardwareId,
    staleTime: 60 * 1000, // 1 minute - commands don't change often
  });
}

/**
 * Hook to fetch sequence steps for manual execution.
 */
export function useManualSteps(batchId: string | null) {
  const setSequenceSteps = useManualControlStore(
    (state) => state.setSequenceSteps
  );

  const query = useQuery({
    queryKey: manualQueryKeys.steps(batchId ?? ''),
    queryFn: () => getManualSteps(batchId!),
    enabled: !!batchId,
    staleTime: 30 * 1000, // 30 seconds
  });

  // Sync with store when data changes
  if (query.data) {
    setSequenceSteps(query.data);
  }

  return query;
}

/**
 * Hook for executing manual control commands.
 */
export function useExecuteCommand() {
  const addResultToHistory = useManualControlStore(
    (state) => state.addResultToHistory
  );

  return useMutation({
    mutationFn: async ({
      batchId,
      request,
      command,
    }: {
      batchId: string;
      request: ManualControlRequest;
      command?: CommandInfo;
    }) => {
      const startTime = Date.now();
      const response = await manualControl(batchId, request);
      const duration = Date.now() - startTime;
      return { response, duration, command };
    },
    onSuccess: ({ response, duration, command }, { request }) => {
      addResultToHistory({
        hardware: request.hardware,
        command: request.command,
        params: request.params ?? {},
        result: response.result,
        success: true,
        duration,
        unit: command?.returnUnit,
      });
      toast.success('Command executed successfully');
    },
    onError: (error: unknown, { request }) => {
      addResultToHistory({
        hardware: request.hardware,
        command: request.command,
        params: request.params ?? {},
        result: { error: getErrorMessage(error) },
        success: false,
        duration: 0,
      });
      toast.error(`Command failed: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook for running a manual step.
 */
export function useRunManualStep() {
  const queryClient = useQueryClient();
  const updateStepStatus = useManualControlStore(
    (state) => state.updateStepStatus
  );
  const setCurrentStepIndex = useManualControlStore(
    (state) => state.setCurrentStepIndex
  );
  const sequenceSteps = useManualControlStore((state) => state.sequenceSteps);

  return useMutation({
    mutationFn: async ({
      batchId,
      stepName,
      parameters,
    }: {
      batchId: string;
      stepName: string;
      parameters?: Record<string, unknown>;
    }) => {
      updateStepStatus(stepName, 'running');
      const startTime = Date.now();
      const result = await runManualStep(batchId, stepName, parameters);
      const duration = (Date.now() - startTime) / 1000; // Convert to seconds
      return { result, duration };
    },
    onSuccess: ({ result, duration }, { batchId, stepName }) => {
      const passed = result.passed !== false;
      updateStepStatus(
        stepName,
        passed ? 'completed' : 'failed',
        result,
        duration
      );

      // Advance to next step if passed
      if (passed) {
        const currentIndex = sequenceSteps.findIndex(
          (s) => s.name === stepName
        );
        if (currentIndex >= 0 && currentIndex < sequenceSteps.length - 1) {
          setCurrentStepIndex(currentIndex + 1);
        }
      }

      queryClient.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId),
      });
      toast.success(`Step "${stepName}" completed`);
    },
    onError: (error: unknown, { stepName }) => {
      updateStepStatus(stepName, 'failed');
      toast.error(`Step failed: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook for skipping a manual step.
 */
export function useSkipManualStep() {
  const queryClient = useQueryClient();
  const updateStepStatus = useManualControlStore(
    (state) => state.updateStepStatus
  );
  const setCurrentStepIndex = useManualControlStore(
    (state) => state.setCurrentStepIndex
  );
  const sequenceSteps = useManualControlStore((state) => state.sequenceSteps);

  return useMutation({
    mutationFn: ({
      batchId,
      stepName,
    }: {
      batchId: string;
      stepName: string;
    }) => skipManualStep(batchId, stepName),
    onSuccess: (_, { batchId, stepName }) => {
      updateStepStatus(stepName, 'skipped');

      // Advance to next step
      const currentIndex = sequenceSteps.findIndex((s) => s.name === stepName);
      if (currentIndex >= 0 && currentIndex < sequenceSteps.length - 1) {
        setCurrentStepIndex(currentIndex + 1);
      }

      queryClient.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId),
      });
      toast.info(`Step "${stepName}" skipped`);
    },
    onError: (error: unknown) => {
      toast.error(`Failed to skip step: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook for resetting manual sequence.
 */
export function useResetManualSequence() {
  const queryClient = useQueryClient();
  const resetSequence = useManualControlStore((state) => state.resetSequence);

  return useMutation({
    mutationFn: (batchId: string) => resetManualSequence(batchId),
    onSuccess: (_, batchId) => {
      resetSequence();
      queryClient.invalidateQueries({
        queryKey: manualQueryKeys.steps(batchId),
      });
      toast.success('Sequence reset');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to reset sequence: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook to fetch command presets.
 */
export function usePresets() {
  return useQuery({
    queryKey: manualQueryKeys.presets(),
    queryFn: listPresets,
    staleTime: 60 * 1000, // 1 minute
  });
}

/**
 * Hook for creating a command preset.
 */
export function useCreatePreset() {
  const queryClient = useQueryClient();
  const addPreset = useManualControlStore((state) => state.addPreset);

  return useMutation({
    mutationFn: (request: CreatePresetRequest) => createPreset(request),
    onSuccess: (preset) => {
      addPreset(preset);
      queryClient.invalidateQueries({ queryKey: manualQueryKeys.presets() });
      toast.success(`Preset "${preset.name}" saved`);
    },
    onError: (error: unknown) => {
      toast.error(`Failed to save preset: ${getErrorMessage(error)}`);
    },
  });
}

/**
 * Hook for deleting a command preset.
 */
export function useDeletePreset() {
  const queryClient = useQueryClient();
  const removePreset = useManualControlStore((state) => state.removePreset);

  return useMutation({
    mutationFn: (presetId: string) => deletePreset(presetId),
    onSuccess: (_, presetId) => {
      removePreset(presetId);
      queryClient.invalidateQueries({ queryKey: manualQueryKeys.presets() });
      toast.success('Preset deleted');
    },
    onError: (error: unknown) => {
      toast.error(`Failed to delete preset: ${getErrorMessage(error)}`);
    },
  });
}
