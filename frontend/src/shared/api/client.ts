import axios from 'axios';
import { store } from '@/app/store';
import { loginSuccess, logout } from '@/features/auth/slice';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = store.getState().auth.tokens?.access;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const refresh = store.getState().auth.tokens?.refresh;
    const originalRequest = error.config;
    if (error.response?.status === 401 && refresh && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data: tokenData } = await apiClient.post('/auth/refresh/', {
          refresh,
        });
        
        // Получаем данные пользователя после обновления токена
        const { data: userData } = await apiClient.get('/auth/me/', {
          headers: { Authorization: `Bearer ${tokenData.access}` }
        });
        
        store.dispatch(
          loginSuccess({
            user: userData,
            tokens: { access: tokenData.access, refresh },
          })
        );
        
        apiClient.defaults.headers.common.Authorization = `Bearer ${tokenData.access}`;
        originalRequest.headers.Authorization = `Bearer ${tokenData.access}`;
        return apiClient(originalRequest);
      } catch (e) {
        store.dispatch(logout());
      }
    }
    return Promise.reject(error);
  }
);
