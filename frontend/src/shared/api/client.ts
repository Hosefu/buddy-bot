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
  console.log('Request interceptor:', {
    url: config.url,
    method: config.method,
    hasToken: !!token
  });
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    console.log('Response interceptor success:', {
      url: response.config.url,
      status: response.status
    });
    return response;
  },
  async (error) => {
    console.error('Response interceptor error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.message
    });

    const refresh = store.getState().auth.tokens?.refresh;
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && refresh && !originalRequest._retry) {
      console.log('Attempting token refresh...');
      originalRequest._retry = true;
      try {
        const tokenResponse = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh,
        });
        const newAccessToken = tokenResponse.data.access;
        
        console.log('Token refresh successful, updating store...');
        
        store.dispatch(
          loginSuccess({
            user: store.getState().auth.user,
            tokens: { 
              access: newAccessToken,
              refresh 
            },
          })
        );
        
        apiClient.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        
        console.log('Retrying original request with new token');
        return apiClient(originalRequest);
      } catch (e) {
        console.error('Token refresh failed, logging out:', e);
        store.dispatch(logout());
        throw e;
      }
    }
    return Promise.reject(error);
  }
);
