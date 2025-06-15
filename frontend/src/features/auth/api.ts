import { apiClient } from '@/shared/api/client';
import type { User, Tokens } from './types';

export const refreshTokens = async (refresh: string): Promise<Tokens> => {
  const { data } = await apiClient.post('/auth/refresh/', { refresh });
  return { access: data.access, refresh };
};

export const fetchCurrentUser = async (): Promise<User> => {
  const { data } = await apiClient.get('/auth/me/');
  return data as User;
};
