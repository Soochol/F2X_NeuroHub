import { useQuery } from '@tanstack/react-query';
import { serialsApi } from '@/api';

interface UseSerialsParams {
    limit?: number;
    skip?: number;
}

export const useSerials = (params: UseSerialsParams = { limit: 500 }) => {
    return useQuery({
        queryKey: ['serials', params],
        queryFn: async () => {
            const response = await serialsApi.getSerials(params);
            // Handle potential paginated response if needed, but for now assuming similar behavior to lots or handling in component
            // Based on LotsPage: const serialsList = Array.isArray(serialsResponse) ? serialsResponse : serialsResponse.items || [];
            return response;
        },
    });
};
