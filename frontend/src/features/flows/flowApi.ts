import { api } from '@/shared/api/api';
import { PaginatedResponse } from '@/shared/api/types';
import { UserFlow, Flow, User, Article } from './types';

const flowApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getMyFlows: builder.query<UserFlow[], void>({
      query: () => 'my/flows/',
      transformResponse: (response: PaginatedResponse<UserFlow>) => {
        return response.results;
      },
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'UserFlow' as const, id })),
              { type: 'UserFlow', id: 'LIST' },
            ]
          : [{ type: 'UserFlow', id: 'LIST' }],
    }),
    getBuddyFlows: builder.query<UserFlow[], void>({
      query: () => 'buddy/my-flows/',
      transformResponse: (response: PaginatedResponse<UserFlow>) => response.results,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'UserFlow' as const, id })),
              { type: 'UserFlow', id: 'BUDDY_LIST' },
            ]
          : [{ type: 'UserFlow', id: 'BUDDY_LIST' }],
    }),
    getBuddyFlowDetails: builder.query<UserFlow, string>({
      query: (flowId) => `buddy/flows/${flowId}/`,
      providesTags: (result) => result ? [{ type: 'UserFlow', id: result.id }] : [],
    }),
    getAvailableFlows: builder.query<Flow[], void>({
      query: () => 'buddy/flows/',
      transformResponse: (response: PaginatedResponse<Flow>) => response.results,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Flow' as const, id })),
              { type: 'Flow', id: 'AVAILABLE_LIST' },
            ]
          : [{ type: 'Flow', id: 'AVAILABLE_LIST' }],
    }),
    getFlowDetails: builder.query<Flow, number>({
      query: (flowId) => `flows/${flowId}/`,
      providesTags: (result) => result ? [{ type: 'Flow', id: result.id }] : [],
    }),
    getArticleDetails: builder.query<Article, string>({
      query: (articleSlug) => `guides/articles/${articleSlug}/`,
      providesTags: (result) => result ? [{ type: 'Article', id: result.id }] : [],
    }),
    getAvailableUsers: builder.query<User[], void>({
      query: () => 'buddy/users/',
      transformResponse: (response: PaginatedResponse<User>) => response.results,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'User' as const, id })),
              { type: 'User', id: 'LIST' },
            ]
          : [{ type: 'User', id: 'LIST' }],
    }),
    assignFlow: builder.mutation<void, { userId: number; flowId: number }>({
      query: ({ userId, flowId }) => ({
        url: `buddy/flows/${flowId}/start/`,
        method: 'POST',
        body: { user_id: userId },
      }),
      invalidatesTags: [{ type: 'UserFlow', id: 'BUDDY_LIST' }],
    }),
  }),
});

export const { 
  useGetMyFlowsQuery, 
  useGetBuddyFlowsQuery,
  useGetBuddyFlowDetailsQuery,
  useGetAvailableFlowsQuery, 
  useGetFlowDetailsQuery,
  useGetArticleDetailsQuery,
  useGetAvailableUsersQuery,
  useAssignFlowMutation,
} = flowApi; 