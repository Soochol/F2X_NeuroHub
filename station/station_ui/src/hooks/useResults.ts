/**
 * Result-related React Query hooks.
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { queryKeys } from '../api/queryClient';
import {
  getResults,
  getResult,
  exportResult,
  type ResultsQueryParams,
  type ExportFormat,
} from '../api/endpoints/results';

/**
 * Hook to fetch execution results with filtering.
 */
export function useResultList(params?: ResultsQueryParams) {
  return useQuery({
    queryKey: queryKeys.results(params as Record<string, unknown> | undefined),
    queryFn: () => getResults(params),
  });
}

/**
 * Hook to fetch a specific result.
 */
export function useResult(resultId: string | null) {
  return useQuery({
    queryKey: queryKeys.result(resultId ?? ''),
    queryFn: () => getResult(resultId!),
    enabled: !!resultId,
  });
}

/**
 * Hook to export a result.
 */
export function useExportResult() {
  return useMutation({
    mutationFn: ({ resultId, format }: { resultId: string; format: ExportFormat }) =>
      exportResult(resultId, format),
    onSuccess: (blob, variables) => {
      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `result_${variables.resultId}.${variables.format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
  });
}
