import { createBrowserRouter, Navigate } from 'react-router-dom';
import { DashboardPage } from '@/pages/Dashboard';
import { BuddyDashboardPage } from '@/pages/BuddyDashboard';
import { AssignFlowPage } from '@/pages/AssignFlow';
import { FlowPreviewPage } from '@/pages/FlowPreview';
import { LocalAuth } from '@/features/auth/components/LocalAuth';
import { useAuth } from '@/features/auth/hooks/useAuth';

const ProtectedRoute = ({ children, requiredRole }: { children: React.ReactNode; requiredRole?: string }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/auth',
    element: <LocalAuth />,
  },
  {
    path: '/buddy/dashboard',
    element: (
      <ProtectedRoute requiredRole="buddy">
        <BuddyDashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/buddy/assign-flow',
    element: (
      <ProtectedRoute requiredRole="buddy">
        <AssignFlowPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/buddy/assign-flow/:flowId',
    element: (
      <ProtectedRoute requiredRole="buddy">
        <AssignFlowPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/flows/preview/:flowId',
    element: (
      <ProtectedRoute>
        <FlowPreviewPage />
      </ProtectedRoute>
    ),
  },
]); 