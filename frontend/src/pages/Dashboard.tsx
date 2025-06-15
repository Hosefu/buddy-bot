import { Link } from 'react-router-dom';
import { useFlows } from '@/features/flows/api/hooks';
import { PageLayout } from '@/shared/components/PageLayout';

export const DashboardPage = () => {
  const { data: flows, isLoading } = useFlows();

  if (isLoading) return <PageLayout>Loading...</PageLayout>;

  return (
    <PageLayout>
      <h1 className="text-xl font-bold mb-4">My Flows</h1>
      <ul className="space-y-2">
        {flows?.map((flow: any) => (
          <li key={flow.id}>
            <Link className="text-blue-600 underline" to={`/flows/${flow.id}`}>
              {flow.title}
            </Link>
          </li>
        ))}
      </ul>
    </PageLayout>
  );
};
