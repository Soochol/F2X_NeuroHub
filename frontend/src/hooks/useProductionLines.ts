import { useQuery } from '@tanstack/react-query';
import { productionLinesApi } from '@/api';

export const useProductionLines = () => {
    return useQuery({
        queryKey: ['productionLines'],
        queryFn: () => productionLinesApi.getActiveProductionLines(),
    });
};
