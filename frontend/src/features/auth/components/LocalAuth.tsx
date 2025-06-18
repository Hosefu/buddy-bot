import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAppDispatch } from '../hooks/useAuth';
import { loginStart, loginSuccess } from '../slice';
import { refreshTokens, fetchCurrentUser } from '../api';
import { apiClient } from '@/shared/api/client';

const schema = z.object({
  refresh: z.string().min(10),
});

type FormValues = z.infer<typeof schema>;

export const LocalAuth = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormValues) => {
    dispatch(loginStart());
    try {
      // Сначала получаем новые токены
      const tokens = await refreshTokens(data.refresh);
      apiClient.defaults.headers.common.Authorization = `Bearer ${tokens.access}`;
      
      // Получаем информацию о пользователе
      const user = await fetchCurrentUser();
      
      dispatch(loginSuccess({ user, tokens }));

      // Редирект в зависимости от роли
      if (user.role === 'buddy') {
        navigate('/buddy/dashboard');
      } else {
        navigate('/');
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Войти в систему
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="refresh" className="sr-only">
                Refresh Token
              </label>
              <input
                id="refresh"
                type="text"
                {...register('refresh')}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Введите refresh token"
              />
              {errors.refresh && (
                <p className="mt-2 text-sm text-red-600">
                  {errors.refresh.message}
                </p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Войти
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
