import { QueryClient, QueryClientProvider as Provider } from '@tanstack/react-query';
import { PropsWithChildren } from 'react';

const queryClient = new QueryClient();

export const AppQueryClientProvider = ({ children }: PropsWithChildren) => (
  <Provider client={queryClient}>{children}</Provider>
);
