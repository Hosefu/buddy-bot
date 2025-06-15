import { useSelector, TypedUseSelectorHook, useDispatch } from 'react-redux';
import type { RootState, AppDispatch } from '@/app/store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export const useAuth = () => {
  const { user, tokens, isLoading } = useAppSelector((state) => state.auth);
  return { user, tokens, isLoading };
};
