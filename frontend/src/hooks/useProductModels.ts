import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import type { ProductModel } from '@/types/api';

export const useProductModels = () => {
    return useQuery({
        queryKey: ['productModels'],
        queryFn: async () => {
            const response = await apiClient.get<ProductModel[]>('/product-models/');
            return response.data;
        },
    });
};
