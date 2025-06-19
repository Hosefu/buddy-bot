import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageLayout } from '@/shared/components/PageLayout';
import { 
  useGetAvailableUsersQuery, 
  useGetFlowDetailsQuery,
  useAssignFlowMutation 
} from '@/features/flows/flowApi';
import { User } from '@/features/flows/types';

export const AssignFlowPage = () => {
  const { flowId } = useParams<{flowId: string}>();
  const navigate = useNavigate();
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  
  const { data: users, isLoading: isLoadingUsers } = useGetAvailableUsersQuery();
  const { data: flow, isLoading: isLoadingFlow } = useGetFlowDetailsQuery(flowId || '', {
    skip: !flowId,
  });
  const [assignFlow, { isLoading: isAssigning }] = useAssignFlowMutation();

  const handleAssign = async () => {
    if (!selectedUserId || !flowId) return;
    try {
      await assignFlow({ userId: selectedUserId, flowId }).unwrap();
      navigate('/buddy/dashboard');
    } catch (error) {
      // TODO: Add proper error handling (e.g., show a toast notification)
      console.error('Failed to assign flow:', error);
      alert('Не удалось назначить поток. Попробуйте снова.');
    }
  };

  const isLoading = isLoadingUsers || (flowId && isLoadingFlow);

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Загрузка...</div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-xl font-bold mb-6">Назначить поток</h1>
        
        {flow && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-medium mb-2">{flow.title}</h2>
            <p className="text-gray-600">{flow.description}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium mb-4">Выберите пользователя</h3>
          
          {!users?.length ? (
            <div className="text-gray-600">
              Нет доступных пользователей для назначения
            </div>
          ) : (
            <div className="space-y-4">
              {users.map((user: User) => (
                <label
                  key={user.id}
                  className={`
                    flex items-center p-4 rounded-lg border cursor-pointer
                    ${selectedUserId === user.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
                  `}
                >
                  <input
                    type="radio"
                    name="user"
                    value={user.id}
                    checked={selectedUserId === user.id}
                    onChange={() => setSelectedUserId(user.id)}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium">{user.name}</div>
                    {user.telegram_username && (
                      <div className="text-sm text-gray-500">
                        @{user.telegram_username}
                      </div>
                    )}
                  </div>
                </label>
              ))}

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => navigate('/buddy/dashboard')}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAssign}
                  disabled={!selectedUserId || isAssigning}
                  className={`
                    px-4 py-2 rounded text-white
                    ${!selectedUserId || isAssigning
                      ? 'bg-blue-300 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600'}
                  `}
                >
                  {isAssigning ? 'Назначаем...' : 'Назначить поток'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}; 