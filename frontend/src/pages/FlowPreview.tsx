import { useParams } from 'react-router-dom';
import { PageLayout } from '@/shared/components/PageLayout';
import { useState } from 'react';
import { useGetFlowDetailsQuery } from '@/features/flows/flowApi';
import { FlowStep } from '@/features/flows/types';
import { FlowStepComponent } from '@/features/flows/components/FlowStepComponent';

export const FlowPreviewPage = () => {
  const { flowId } = useParams<{ flowId: string }>();
  const { data: flow, isLoading, error } = useGetFlowDetailsQuery(flowId || '', {
    skip: !flowId,
  });
  const [openStep, setOpenStep] = useState<number | null>(null);

  if (isLoading) {
    return <PageLayout><p>Загрузка предпросмотра...</p></PageLayout>;
  }

  if (error || !flow) {
    return <PageLayout><p>Ошибка загрузки предпросмотра потока.</p></PageLayout>;
  }
  
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h1 className="text-3xl font-bold mb-2">{flow.title}</h1>
          <p className="text-lg text-gray-600">{flow.description}</p>
        </div>

        <h2 className="text-2xl font-bold mb-4">Этапы потока</h2>
        <div className="space-y-2">
          {(flow.steps || (flow as any).flow_steps)?.map((step: FlowStep) => (
            <div key={step.id} className="border rounded-md">
              <button
                className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 flex justify-between items-center"
                onClick={() => setOpenStep(openStep === step.id ? null : step.id)}
              >
                <h3 className="text-lg font-medium">
                  {/* TODO: Add order to FlowStep type */}
                  <span className="mr-4 text-gray-400">#</span>
                  {step.title}
                </h3>
                <span>{openStep === step.id ? 'Свернуть' : 'Развернуть'}</span>
              </button>
              {openStep === step.id && (
                <div className="p-4 border-t">
                  <FlowStepComponent step={step} isPreview={true} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </PageLayout>
  );
}; 