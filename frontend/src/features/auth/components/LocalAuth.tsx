import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAppDispatch } from '../hooks/useAuth';
import { loginStart, loginSuccess, loginFailure } from '../slice';
import { refreshTokens, fetchCurrentUser } from '../api';

const schema = z.object({
  refresh: z.string().min(10),
});

type FormValues = z.infer<typeof schema>;

export const LocalAuth = () => {
  const dispatch = useAppDispatch();
  const { register, handleSubmit, formState } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormValues) => {
    dispatch(loginStart());
    try {
      const tokens = await refreshTokens(data.refresh);
      const user = await fetchCurrentUser();
      dispatch(loginSuccess({ user, tokens }));
    } catch (e) {
      dispatch(loginFailure('Auth failed'));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-4">
      <textarea
        className="border p-2 w-full h-24"
        placeholder="Refresh token"
        {...register('refresh')}
      />
      {formState.errors.refresh && (
        <p className="text-red-500 text-sm">Token is required</p>
      )}
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        type="submit"
      >
        Dev Login
      </button>
    </form>
  );
};
