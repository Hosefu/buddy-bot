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
    const rolesArr: string[] = (user as any).roles || [];
    const isBuddyFlag = (user as any).is_buddy === true;
    const hasRole =
      rolesArr.some((r) => requiredRoles.includes(r) || requiredRoles.includes(r.toLowerCase())) ||
      (isBuddyFlag && requiredRoles.some((r) => ['buddy', 'бадди'].includes(r.toLowerCase())));
    if (!hasRole) return <Navigate to="/" />;
  }

  return children;
};
