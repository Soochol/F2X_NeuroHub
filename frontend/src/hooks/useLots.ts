import { useQuery } from '@tanstack/react-query';
import { lotsApi } from '@/api';
import type { LotStatus, Lot } from '@/types/api';

interface UseLotsParams {
    skip?: number;
    limit?: number;
    status?: LotStatus | '';
    sort_by?: string;
    sort_direction?: 'asc' | 'desc';
}

interface LotsData {
    lots: Lot[];
    total: number;
}

export const useLots = (params: UseLotsParams) => {
    return useQuery<LotsData>({
        queryKey: ['lots', params],
        queryFn: async () => {
            const response = await lotsApi.getLots(params as any);
            // Handle potential inconsistent API response (Array vs Paginated Object)
            if (Array.isArray(response)) {
                return {
                    lots: response,
                    total: response.length // Note: If paginated array without total, this might be inaccurate for total count
                };
            } else {
                // Assuming response has items and total if not array
                const anyResponse = response as any;
                return {
                    lots: anyResponse.items || [],
                    total: anyResponse.total || 0
                };
            }
        },
        placeholderData: (previousData) => previousData,
    });
};
