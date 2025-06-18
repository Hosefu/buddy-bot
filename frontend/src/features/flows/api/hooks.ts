import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';

export const useFlows = () =>
  useQuery({
    queryKey: ['flows'],
    queryFn: async () => {
      const { data } = await apiClient.get('/my/flows');
      return data.results;
    },
  });

export const useFlow = (id: string) =>
  useQuery({
    queryKey: ['flow', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${id}`);
      return data;
    },
    enabled: Boolean(id),
  });
