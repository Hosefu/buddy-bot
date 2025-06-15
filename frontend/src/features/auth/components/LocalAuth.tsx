import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAppDispatch } from '../hooks/useAuth';
import { loginSuccess } from '../slice';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(4),
});

type FormValues = z.infer<typeof schema>;

export const LocalAuth = () => {
  const dispatch = useAppDispatch();
  const { register, handleSubmit, formState } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormValues) => {
    // mock login success
    dispatch(
      loginSuccess({
        user: {
          id: 1,
          firstName: 'Dev',
          roles: ['user'],
        },
        tokens: { access: 'mock', refresh: 'mock' },
      })
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 p-4">
      <input
        className="border p-2 w-full"
        placeholder="Email"
        {...register('email')}
      />
      <input
        className="border p-2 w-full"
        type="password"
        placeholder="Password"
        {...register('password')}
      />
      {formState.errors.email && (
        <p className="text-red-500 text-sm">Invalid email</p>
      )}
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        type="submit"
      >
        Login
      </button>
    </form>
  );
};
