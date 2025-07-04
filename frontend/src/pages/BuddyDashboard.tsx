import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useGetBuddyFlowsQuery, useGetAvailableFlowsQuery } from '@/features/flows/flowApi';
import { PageLayout } from '@/shared/components/PageLayout';
import { UserFlow, Flow } from '@/features/flows/types';

export const BuddyDashboardPage = () => {
  const { data: buddyFlows, isLoading: isLoadingBuddyFlows, error: buddyFlowsError } = useGetBuddyFlowsQuery();
  const { data: availableFlows, isLoading: isLoadingAvailableFlows, error: availableFlowsError } = useGetAvailableFlowsQuery();
  const [activeTab, setActiveTab] = useState<'active' | 'available'>('active');

  if (isLoadingBuddyFlows || isLoadingAvailableFlows) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Загрузка...</div>
        </div>
      </PageLayout>
    );
  }

  if (buddyFlowsError || availableFlowsError) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-600">
            Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.
          </div>
        </div>
      </PageLayout>
    );
  }

  // TODO: Add proper typing for user
  // TODO: Add better progress visualization

  return (
    <PageLayout>
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">Панель бадди</h1>
          <Link
            to="/buddy/assign-flow"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Назначить поток
          </Link>
        </div>

        <div className="border-t border-gray-200">
          <div className="bg-gray-50 border-b border-gray-200">
            <nav className="-mb-px flex" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('active')}
                className={`
                  w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm
                  ${activeTab === 'active'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                `}
              >
                Активные потоки
              </button>
              <button
                onClick={() => setActiveTab('available')}
                className={`
                  w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm
                  ${activeTab === 'available'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                `}
              >
                Доступные потоки
              </button>
            </nav>
          </div>

          <div className="px-4 py-5 sm:p-6">
            {activeTab === 'active' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Потоки ваших подопечных</h2>
                {!buddyFlows?.length ? (
                  <div className="text-gray-500 text-center py-8">
                    У вас пока нет активных потоков подопечных
                  </div>
                ) : (
                  <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {buddyFlows.map((userFlow: UserFlow) => {
                      if (!userFlow?.flow) return null;
                      return (
                        <div
                          key={userFlow.id}
                          className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200"
                        >
                          <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg font-medium text-gray-900">
                              {userFlow.flow.title}
                            </h3>
                            <p className="mt-1 text-sm text-gray-500">
                              Пользователь: {userFlow.user?.name || `ID: ${userFlow.user?.id || 'Неизвестно'}`}
                            </p>
                            <div className="mt-4">
                              <div className="relative pt-1">
                                <div className="overflow-hidden h-2 text-xs flex rounded bg-blue-200">
                                  <div
                                    style={{ width: `${userFlow.progress_percentage || 0}%` }}
                                    className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                                  />
                                </div>
                                <div className="mt-1 text-xs text-gray-500 text-right">
                                  {userFlow.progress_percentage || 0}%
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="px-4 py-4 sm:px-6">
                            <Link
                              to={`/buddy/flows/${userFlow.flow.id}`}
                              className="text-sm font-medium text-blue-600 hover:text-blue-500"
                            >
                              Подробнее →
                            </Link>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'available' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Доступные потоки</h2>
                {!availableFlows?.length ? (
                  <div className="text-gray-500 text-center py-8">
                    Нет доступных потоков для назначения
                  </div>
                ) : (
                  <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {availableFlows.map((flow: Flow) => {
                      if (!flow) return null;
                      return (
                        <div
                          key={flow.id}
                          className="bg-white overflow-hidden shadow rounded-lg divide-y divide-gray-200"
                        >
                          <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg font-medium text-gray-900">
                              {flow.title}
                            </h3>
                            {flow.description && (
                              <p className="mt-1 text-sm text-gray-500">
                                {flow.description}
                              </p>
                            )}
                          </div>
                          <div className="px-4 py-4 sm:px-6 flex justify-between">
                            <Link
                              to={`/flows/preview/${flow.id}`}
                              className="text-sm font-medium text-green-600 hover:text-green-500"
                            >
                              Просмотр
                            </Link>
                            <Link
                              to={`/buddy/assign-flow/${flow.id}`}
                              className="text-sm font-medium text-blue-600 hover:text-blue-500"
                            >
                              Назначить →
                            </Link>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </PageLayout>
  );
}; 