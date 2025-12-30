/**
 * Equipment Hooks with TanStack Query
 *
 * Provides data fetching, caching, and mutation for equipment entities.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { equipmentApi, type EquipmentCreate, type EquipmentUpdate } from '@/api/endpoints/equipment';

/** Query keys for equipment-related queries */
export const equipmentKeys = {
  all: ['equipment'] as const,
  lists: () => [...equipmentKeys.all, 'list'] as const,
  list: (filters?: { skip?: number; limit?: number }) => [...equipmentKeys.lists(), filters] as const,
  active: () => [...equipmentKeys.all, 'active'] as const,
  needsMaintenance: () => [...equipmentKeys.all, 'needs-maintenance'] as const,
  details: () => [...equipmentKeys.all, 'detail'] as const,
  detail: (id: number) => [...equipmentKeys.details(), id] as const,
  byLine: (lineId: number) => [...equipmentKeys.all, 'line', lineId] as const,
  byProcess: (processId: number) => [...equipmentKeys.all, 'process', processId] as const,
};

/**
 * Fetch all equipment with optional pagination
 */
export function useEquipment(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: equipmentKeys.list(params),
    queryFn: () => equipmentApi.getEquipment(params),
  });
}

/**
 * Fetch active equipment only
 */
export function useActiveEquipment() {
  return useQuery({
    queryKey: equipmentKeys.active(),
    queryFn: () => equipmentApi.getActiveEquipment(),
    staleTime: 30 * 1000, // 30 seconds - equipment status can change frequently
  });
}

/**
 * Fetch single equipment by ID
 */
export function useEquipmentById(equipmentId: number | undefined) {
  return useQuery({
    queryKey: equipmentKeys.detail(equipmentId!),
    queryFn: () => equipmentApi.getEquipmentById(equipmentId!),
    enabled: !!equipmentId,
  });
}

/**
 * Fetch equipment by production line
 */
export function useEquipmentByLine(productionLineId: number | undefined) {
  return useQuery({
    queryKey: equipmentKeys.byLine(productionLineId!),
    queryFn: () => equipmentApi.getEquipmentByLine(productionLineId!),
    enabled: !!productionLineId,
  });
}

/**
 * Fetch equipment by process
 */
export function useEquipmentByProcess(processId: number | undefined) {
  return useQuery({
    queryKey: equipmentKeys.byProcess(processId!),
    queryFn: () => equipmentApi.getEquipmentByProcess(processId!),
    enabled: !!processId,
  });
}

/**
 * Fetch equipment that needs maintenance
 */
export function useEquipmentNeedsMaintenance() {
  return useQuery({
    queryKey: equipmentKeys.needsMaintenance(),
    queryFn: () => equipmentApi.getNeedsMaintenance(),
  });
}

/**
 * Create new equipment
 */
export function useCreateEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EquipmentCreate) => equipmentApi.createEquipment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equipmentKeys.all });
    },
  });
}

/**
 * Update equipment
 */
export function useUpdateEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EquipmentUpdate }) =>
      equipmentApi.updateEquipment(id, data),
    onSuccess: (updatedEquipment) => {
      // Update the specific equipment in cache
      queryClient.setQueryData(
        equipmentKeys.detail(updatedEquipment.id),
        updatedEquipment
      );
      // Invalidate list queries
      queryClient.invalidateQueries({ queryKey: equipmentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.active() });
    },
  });
}

/**
 * Delete equipment
 */
export function useDeleteEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (equipmentId: number) => equipmentApi.deleteEquipment(equipmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equipmentKeys.all });
    },
  });
}
