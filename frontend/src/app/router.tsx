import { createBrowserRouter, Navigate } from 'react-router-dom';
import { DashboardPage } from '@/pages/Dashboard';
import { BuddyDashboardPage } from '@/pages/BuddyDashboard';
import { AssignFlowPage } from '@/pages/AssignFlow';
import { FlowPreviewPage } from '@/pages/FlowPreview';
import { BuddyFlowPreviewPage } from '@/pages/BuddyFlowPreview';
import { FlowStepPage } from '@/pages/FlowStepPage';
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
      <ProtectedRoute>
        <BuddyDashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/buddy/assign-flow',
    element: (
      <ProtectedRoute>
        <AssignFlowPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/buddy/assign-flow/:flowId',
    element: (
      <ProtectedRoute>
        <AssignFlowPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/buddy/flows/:flowId',
    element: (
      <ProtectedRoute requiredRole="buddy">
        <BuddyFlowPreviewPage />
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
  {
    path: '/flows/:flowId/step/:stepId',
    element: (
      <ProtectedRoute>
        <FlowStepPage />
      </ProtectedRoute>
    ),
  },
]); 