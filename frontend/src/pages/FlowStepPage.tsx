import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useGetMyFlowsQuery } from '@/features/flows/flowApi';
import { FlowStepComponent } from '@/features/flows/components/FlowStepComponent';
import { PageLayout } from '@/shared/components/PageLayout';

export const FlowStepPage = () => {
  const { flowId, stepId } = useParams<{ flowId: string; stepId: string }>();
  const navigate = useNavigate();
  const { data: userFlows, isLoading, error } = useGetMyFlowsQuery();

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Загрузка...</div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-red-600 mb-2">Ошибка загрузки данных</div>
          <button 
            onClick={() => window.location.reload()} 
            className="text-blue-600 underline"
          >
            Попробовать снова
          </button>
        </div>
      </PageLayout>
    );
  }

  const userFlow = userFlows?.find((uf) => String(uf.flow.id) === flowId);

  if (!userFlow) {
    return (
      <PageLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-red-600 mb-2">Поток не найден</div>
          <button 
            onClick={() => navigate('/')} 
            className="text-blue-600 underline"
          >
            Вернуться к списку потоков
          </button>
        </div>
      </PageLayout>
    );
  }

  const step = userFlow.current_step;

  if (!step || String(step.id) !== stepId) {
    return (
      <PageLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-red-600 mb-2">Этап не найден или не является текущим</div>
          <button 
            onClick={() => navigate('/')} 
            className="text-blue-600 underline"
          >
            Вернуться к списку потоков
          </button>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={() => navigate('/')} 
          className="mb-4 text-blue-600 hover:underline flex items-center gap-2"
        >
          ← Вернуться к списку потоков
        </button>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold mb-2">{userFlow.flow.title}</h1>
          <h2 className="text-xl font-semibold text-gray-600 mb-6">{step.title}</h2>
          <FlowStepComponent step={step} />
        </div>
      </div>
    </PageLayout>
  );
}; 