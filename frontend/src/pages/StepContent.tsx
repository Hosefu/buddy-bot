import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useFlowSteps,
  useStepTask,
  useStepQuiz,
  useReadStep,
  useSubmitTaskAnswer,
  useSubmitQuizAnswer,
} from '@/features/flows/api/hooks';
import { PageLayout } from '@/shared/components/PageLayout';

export const StepContentPage = () => {
  const { flowId, stepId } = useParams<{ flowId: string; stepId: string }>();

  const { data: steps } = useFlowSteps(flowId || '');
  const step = steps?.find((s: any) => String(s.id) === String(stepId));

  const { data: task } = useStepTask(flowId || '', stepId || '', !!step?.task);
  const { data: quiz } = useStepQuiz(flowId || '', stepId || '', !!step?.quiz);

  const readStep = useReadStep();
  const submitTask = useSubmitTaskAnswer();
  const submitQuiz = useSubmitQuizAnswer();

  const [taskAnswer, setTaskAnswer] = useState('');
  const [quizResponses, setQuizResponses] = useState<Record<number, number>>({});
  const [quizMessage, setQuizMessage] = useState('');

  useEffect(() => {
    if (flowId && stepId) {
      readStep.mutate({ flowId, stepId });
    }
  }, [flowId, stepId]);

  if (!step) {
    return <PageLayout>Step not found</PageLayout>;
  }

  return (
    <PageLayout>
      <div className="prose max-w-none">
        <h1>{step.title}</h1>
        <p>{step.description}</p>
        {step.article && (
          <div>
            <h2>{step.article.title}</h2>
            <div dangerouslySetInnerHTML={{ __html: step.article.content }} />
          </div>
        )}

        {task && (
          <div className="mt-6">
            <h2 className="font-bold text-lg mb-2">{task.title}</h2>
            <p>{task.description}</p>
            <p className="italic mb-2">{task.instruction}</p>
            <input
              type="text"
              value={taskAnswer}
              onChange={(e) => setTaskAnswer(e.target.value)}
              className="border p-2 mr-2"
            />
            <button
              onClick={() =>
                submitTask.mutate({ flowId: flowId!, stepId: stepId!, answer: taskAnswer })
              }
              className="px-3 py-1 bg-blue-500 text-white rounded"
            >
              Отправить
            </button>
            {submitTask.data && (
              <p className="mt-2">
                {submitTask.data.is_correct ? 'Верно!' : 'Неверный ответ'}
              </p>
            )}
          </div>
        )}

        {quiz && (
          <div className="mt-6">
            <h2 className="font-bold text-lg mb-4">{quiz.title}</h2>
            <p>{quiz.description}</p>
            {quiz.questions.map((q: any) => (
              <div key={q.id} className="mb-4">
                <p className="font-semibold mb-1">{q.question}</p>
                <ul className="space-y-1">
                  {q.answers.map((a: any) => (
                    <li key={a.id}>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          value={a.id}
                          onChange={() =>
                            setQuizResponses((prev) => ({ ...prev, [q.id]: a.id }))
                          }
                        />
                        <span>{a.answer_text}</span>
                      </label>
                    </li>
                  ))}
                </ul>
                <button
                  className="mt-2 px-2 py-1 bg-blue-500 text-white rounded"
                  onClick={() => {
                    const answerId = quizResponses[q.id];
                    if (answerId) {
                      submitQuiz.mutate(
                        {
                          flowId: flowId!,
                          stepId: stepId!,
                          questionId: q.id,
                          answerId,
                        },
                        {
                          onSuccess: (data) => {
                            if (data.is_correct) setQuizMessage('Ответ верный');
                            else setQuizMessage('Ответ неверный');
                          },
                        }
                      );
                    }
                  }}
                >
                  Ответить
                </button>
              </div>
            ))}
            {quizMessage && <p className="mt-2">{quizMessage}</p>}
          </div>
        )}
      </div>
    </PageLayout>
  );
};
