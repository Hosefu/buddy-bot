import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';
import { PageLayout } from '@/shared/components/PageLayout';
import { useState } from 'react';

// TODO: Вынести типы в общий файл
interface Answer {
  id: number;
  answer_text: string;
  is_correct?: boolean;
}

interface Question {
  id: number;
  question: string;
  answers: Answer[];
}

interface Quiz {
  id: number;
  title: string;
  description: string;
  questions: Question[];
}

interface Task {
  id: number;
  title: string;
  description: string;
  instruction: string;
}

interface Article {
  id: number;
  title: string;
  content: string;
  summary: string;
}

interface FlowStep {
  id: number;
  title: string;
  description: string;
  order: number;
  article: Article | null;
  task: Task | null;
  quiz: Quiz | null;
}

interface Flow {
  id: number;
  title: string;
  description: string;
  flow_steps: FlowStep[];
}

const useFlowDetails = (flowId: string) => {
  return useQuery<Flow>({
    queryKey: ['flow-details', flowId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${flowId}/`);
      return data;
    },
    enabled: !!flowId,
  });
};

export const FlowPreviewPage = () => {
  const { flowId } = useParams<{ flowId: string }>();
  const { data: flow, isLoading, error } = useFlowDetails(flowId || '');
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
          {flow.flow_steps.map((step) => (
            <div key={step.id} className="border rounded-md">
              <button
                className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 flex justify-between items-center"
                onClick={() => setOpenStep(openStep === step.id ? null : step.id)}
              >
                <h3 className="text-lg font-medium">
                  <span className="mr-4 text-gray-400">#{step.order}</span>
                  {step.title}
                </h3>
                <span>{openStep === step.id ? 'Свернуть' : 'Развернуть'}</span>
              </button>
              {openStep === step.id && (
                <div className="prose max-w-none p-4 border-t">
                  <p className="lead">{step.description}</p>
                  {step.article && (
                    <div>
                      <h3>Материал для чтения</h3>
                      <h4>{step.article.title}</h4>
                      <div dangerouslySetInnerHTML={{ __html: step.article.content }} />
                    </div>
                  )}
                  {step.task && (
                    <div>
                      <h3>Задание</h3>
                      <h4>{step.task.title}</h4>
                      <p>{step.task.description}</p>
                      <p><strong>Инструкция:</strong> {step.task.instruction}</p>
                    </div>
                  )}
                  {step.quiz && (
                    <div>
                      <h3>Квиз: {step.quiz.title}</h3>
                      <p>{step.quiz.description}</p>
                      <ul className="list-decimal pl-5 mt-4 space-y-4">
                        {step.quiz.questions.map(q => (
                          <li key={q.id}>
                            <p className="font-semibold">{q.question}</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                              {q.answers.map(a => (
                                <li key={a.id} className={a.is_correct ? 'text-green-600 font-bold' : ''}>
                                  {a.answer_text} {a.is_correct && '(Верный ответ)'}
                                </li>
                              ))}
                            </ul>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </PageLayout>
  );
}; 