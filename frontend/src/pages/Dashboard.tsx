import { Link } from 'react-router-dom';
import { useFlows } from '@/features/flows/api/hooks';
import { PageLayout } from '@/shared/components/PageLayout';

export const DashboardPage = () => {
  const { data: flows, isLoading, error } = useFlows();

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

  if (!flows?.length) {
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
      <ul className="space-y-4">
        {flows.map((flow) => (
          <li key={flow.id} className="bg-white rounded-lg shadow p-4">
            <Link 
              to={`/flows/${flow.id}`}
              className="block hover:bg-gray-50 transition-colors"
            >
              <h2 className="text-lg font-medium text-blue-600">{flow.title}</h2>
              {flow.description && (
                <p className="text-gray-600 mt-1">{flow.description}</p>
              )}
              <div className="flex items-center mt-2">
                <div className="text-sm text-gray-500">
                  Прогресс: {flow.progress_percentage || 0}%
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </PageLayout>
  );
};
