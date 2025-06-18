import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/api/client';

export const useFlows = () =>
  useQuery({
    queryKey: ['flows'],
    queryFn: async () => {
      const { data } = await apiClient.get('/my/flows');
      return data.results;
    },
  });

export const useFlow = (id: string) =>
  useQuery({
    queryKey: ['flow', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${id}`);
      return data;
    },
    enabled: Boolean(id),
  });

export const useFlowSteps = (flowId: string) =>
  useQuery({
    queryKey: ['flow-steps', flowId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${flowId}/steps/`);
      return data.results;
    },
    enabled: Boolean(flowId),
  });

export const useStepTask = (
  flowId: string,
  stepId: string,
  enabled: boolean = true
) =>
  useQuery({
    queryKey: ['step-task', flowId, stepId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${flowId}/steps/${stepId}/task/`);
      return data;
    },
    enabled: Boolean(flowId && stepId && enabled),
  });

export const useStepQuiz = (
  flowId: string,
  stepId: string,
  enabled: boolean = true
) =>
  useQuery({
    queryKey: ['step-quiz', flowId, stepId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/flows/${flowId}/steps/${stepId}/quiz/`);
      return data;
    },
    enabled: Boolean(flowId && stepId && enabled),
  });

export const useReadStep = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ flowId, stepId }: { flowId: string; stepId: string }) => {
      const { data } = await apiClient.post(`/flows/${flowId}/steps/${stepId}/read/`);
      return data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries(['flow-steps', variables.flowId]);
    },
  });
};

export const useSubmitTaskAnswer = () =>
  {
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: async ({ flowId, stepId, answer }: { flowId: string; stepId: string; answer: string }) => {
        const { data } = await apiClient.post(`/flows/${flowId}/steps/${stepId}/task/`, { answer });
        return data;
      },
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries(['flow-steps', variables.flowId]);
      },
    });
  };

export const useSubmitQuizAnswer = () =>
  {
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: async ({
        flowId,
        stepId,
        questionId,
        answerId,
      }: {
        flowId: string;
        stepId: string;
        questionId: number;
        answerId: number;
      }) => {
        const { data } = await apiClient.post(`/flows/${flowId}/steps/${stepId}/quiz/${questionId}/`, {
          answer_id: answerId,
        });
        return data;
      },
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries(['flow-steps', variables.flowId]);
      },
    });
  };
