import { LocalAuth } from '@/features/auth/components/LocalAuth';

export const AuthPage = () => {
  return (
    <div className="flex flex-col items-center mt-10">
      <h1 className="text-lg font-bold mb-4">BudTest Login</h1>
      <LocalAuth />
    </div>
  );
};
