import { useParams, Link } from 'react-router-dom';
import { PageLayout, PageLoader, NotFound } from '@/shared/components/PageLayout';

// Mock data
const flows = {
  '1': {
    id: '1',
    title: 'Onboarding Flow',
    steps: [
      { id: 'step1', title: 'Welcome' },
      { id: 'step2', title: 'First Task' },
    ],
  },
};

export const FlowDetailPage = () => {
  const { flowId } = useParams<{ flowId: string }>();
  const flow = flows[flowId ?? ''];

  if (!flow) return <NotFound />;

  return (
    <PageLayout>
      <h1 className="text-xl font-bold mb-4">{flow.title}</h1>
      <ul className="space-y-2">
        {flow.steps.map((s) => (
          <li key={s.id}>
            <Link
              className="text-blue-600 underline"
              to={`/flows/${flow.id}/steps/${s.id}`}
            >
              {s.title}
            </Link>
          </li>
        ))}
      </ul>
    </PageLayout>
  );
};
