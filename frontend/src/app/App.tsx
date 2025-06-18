import { useEffect } from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import { useAuth, useAppDispatch } from '@/features/auth/hooks/useAuth';
import { loginSuccess } from '@/features/auth/slice';
import { fetchCurrentUser } from '@/features/auth/api';
import { DashboardPage } from '../pages/Dashboard';
import { BuddyDashboardPage } from '../pages/BuddyDashboard';
import { AssignFlowPage } from '../pages/AssignFlow';
import { AuthPage } from '../pages/AuthPage';
import { FlowDetailPage } from '../pages/FlowDetail';
import { StepContentPage } from '../pages/StepContent';
import { ProtectedRoute } from '@/shared/components/ProtectedRoute';

export const App = () => {
  const { tokens, user } = useAuth();
  const dispatch = useAppDispatch();

  // При наличии токена, но отсутствии пользователя – загружаем его
  useEffect(() => {
    const init = async () => {
      if (tokens?.access && !user) {
        try {
          const currentUser = await fetchCurrentUser();
          dispatch(loginSuccess({ user: currentUser as any, tokens }));
        } catch (err) {
          console.error('Failed to init user', err);
        }
      }
    };
    init();
  }, [tokens, user, dispatch]);

  return (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="/buddy/dashboard" element={<ProtectedRoute><BuddyDashboardPage /></ProtectedRoute>} />
      <Route path="/buddy/assign-flow" element={<ProtectedRoute><AssignFlowPage /></ProtectedRoute>} />
      <Route path="/buddy/assign-flow/:flowId" element={<ProtectedRoute><AssignFlowPage /></ProtectedRoute>} />
      <Route
        path="/flows/:flowId"
        element={
          <ProtectedRoute>
            <FlowDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/flows/:flowId/steps/:stepId"
        element={
          <ProtectedRoute>
            <StepContentPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};
