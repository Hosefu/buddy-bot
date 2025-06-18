import { useSelector, TypedUseSelectorHook, useDispatch } from 'react-redux';
import type { RootState, AppDispatch } from '@/app/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export interface User {
  id: number;
  name: string;
  telegram_id: string;
  telegram_username: string | null;
  role: string;
}

export interface Tokens {
  access: string;
  refresh: string;
}

export const useAuth = () => {
  const { user, tokens, isLoading } = useAppSelector((state) => state.auth);
  
  return {
    user,
    tokens,
    isLoading,
    isAuthenticated: !!tokens?.access,
  };
};
