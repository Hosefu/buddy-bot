import { useParams } from 'react-router-dom';
import { PageLayout } from '@/shared/components/PageLayout';

// Mock
const steps = {
  step1: {
    id: 'step1',
    content: 'Welcome to BudTest! Read the article and proceed.',
  },
  step2: {
    id: 'step2',
    content: 'Complete your first task.',
  },
};

export const StepContentPage = () => {
  const { stepId } = useParams<{ stepId: string }>();
  const step = steps[stepId ?? ''];

  if (!step) return <PageLayout>Step not found</PageLayout>;

  return (
    <PageLayout>
      <p>{step.content}</p>
    </PageLayout>
  );
};
