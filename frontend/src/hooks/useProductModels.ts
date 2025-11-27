import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import type { ProductModel } from '@/types/api';

interface UseProductModelsOptions {
    activeOnly?: boolean;
}

export const useProductModels = (options: UseProductModelsOptions = { activeOnly: true }) => {
    const { activeOnly = true } = options;

    return useQuery({
        queryKey: ['productModels', { activeOnly }],
        queryFn: async () => {
            const endpoint = activeOnly ? '/product-models/active' : '/product-models/';
            const response = await apiClient.get<ProductModel[]>(endpoint);
            return response.data;
        },
    });
};
