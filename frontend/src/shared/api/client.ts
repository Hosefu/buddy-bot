import axios from 'axios';
import { store } from '@/app/store';

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
