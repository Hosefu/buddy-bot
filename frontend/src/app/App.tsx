import { useEffect } from 'react';
import { RouterProvider } from 'react-router-dom';
import { useAuth, useAppDispatch } from '@/features/auth/hooks/useAuth';
import { loginSuccess } from '@/features/auth/slice';
import { fetchCurrentUser } from '@/features/auth/api';
import { router } from './router';

export const App = () => {
  const { tokens, user } = useAuth();
  const dispatch = useAppDispatch();

  // При наличии токена, но отсутствии пользователя – загружаем его
  useEffect(() => {
    const init = async () => {
      if (tokens?.access && !user) {
        try {
          const currentUser = await fetchCurrentUser();
          dispatch(loginSuccess({ user: currentUser as any, tokens: tokens! }));
        } catch (err) {
          console.error('Failed to init user', err);
        }
      }
    };
    init();
  }, [tokens, user, dispatch]);

  return <RouterProvider router={router} />;
};
