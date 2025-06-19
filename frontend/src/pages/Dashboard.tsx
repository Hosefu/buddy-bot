import { Link } from 'react-router-dom';
import { useGetMyFlowsQuery } from '@/features/flows/flowApi';
import { PageLayout } from '@/shared/components/PageLayout';
import { FlowStep } from '@/features/flows/types';

export const DashboardPage = () => {
  const { data: userFlows, isLoading, error } = useGetMyFlowsQuery();

  console.log('User flows data:', userFlows);

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Загрузка потоков...</div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    console.error('Error loading flows:', error);
    return (
      <PageLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-red-600 mb-2">Ошибка загрузки потоков</div>
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

  if (!userFlows?.length) {
    return (
      <PageLayout>
        <h1 className="text-xl font-bold mb-4">Мои потоки</h1>
        <div className="text-gray-600">
          У вас пока нет активных потоков обучения
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <h1 className="text-xl font-bold mb-4">Мои потоки</h1>
      <ul className="space-y-6">
        {userFlows.map((userFlow) => {
          console.log('Processing userFlow:', userFlow);
          const isActionable = (userFlow.status === 'in_progress' || userFlow.status === 'not_started') && userFlow.current_step;
          const linkTo = isActionable ? `/flows/${userFlow.flow.id}/step/${userFlow.current_step!.id}` : '#';
          const buttonText = userFlow.status === 'in_progress' ? 'Продолжить' : 'Начать';

          return (
            <li key={userFlow.id} className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-800">{userFlow.flow.title}</h2>
                <p className="text-gray-600 mt-2">{userFlow.flow.description}</p>
                <div className="mt-6 flex justify-between items-center">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Статус: </span>
                    <span className="text-sm font-semibold text-gray-800">{userFlow.status}</span>
                  </div>
                  {isActionable && (
                    <Link 
                      to={linkTo} 
                      className="px-5 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
                    >
                      {buttonText}
                    </Link>
                  )}
                  {userFlow.status === 'completed' && (
                     <span className="px-5 py-2 bg-green-100 text-green-800 font-semibold rounded-lg">
                       Завершено
                     </span>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </PageLayout>
  );
};
