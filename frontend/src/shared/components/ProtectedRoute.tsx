import { Navigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';

type Props = {
  children: JSX.Element;
  requiredRoles?: string[];
};

export const ProtectedRoute = ({ children, requiredRoles }: Props) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/auth" />;
  }

  if (requiredRoles && requiredRoles.length) {
    const hasRole = user.roles.some((r) => requiredRoles.includes(r));
    if (!hasRole) return <Navigate to="/" />;
  }

  return children;
};
