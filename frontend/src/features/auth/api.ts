import { apiClient } from '@/shared/api/client';
import type { User, Tokens } from './types';

export const refreshTokens = async (refresh: string): Promise<Tokens> => {
  console.log('Attempting to refresh tokens with:', { refresh: refresh.substring(0, 10) + '...' });
  try {
    const { data } = await apiClient.post('/auth/refresh/', { refresh });
    console.log('Tokens refreshed successfully:', { access: data.access.substring(0, 10) + '...' });
    apiClient.defaults.headers.common.Authorization = `Bearer ${data.access}`;
    return { access: data.access, refresh };
  } catch (error) {
    console.error('Token refresh failed:', error);
    throw error;
  }
};

export const fetchCurrentUser = async (): Promise<User> => {
  console.log('Fetching current user');
  try {
    const token = apiClient.defaults.headers.common.Authorization;
    console.log('Current token:', token ? 'present' : 'missing');
    
    const { data } = await apiClient.get('/auth/me/');
    console.log('Current user fetched successfully:', data);
    return data as User;
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    throw error;
  }
};
