import { Route, Routes, Navigate } from 'react-router-dom';
import { DashboardPage } from '../pages/Dashboard';
import { AuthPage } from '../pages/AuthPage';
import { FlowDetailPage } from '../pages/FlowDetail';
import { StepContentPage } from '../pages/StepContent';
import { ProtectedRoute } from '@/shared/components/ProtectedRoute';

export const App = () => {
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
