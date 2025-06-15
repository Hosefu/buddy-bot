import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from './Dashboard';
import { store } from '@/app/store';

describe('DashboardPage', () => {
  it('renders heading', () => {
    const client = new QueryClient();
    client.setQueryData(['flows'], [{ id: '1', title: 'Test Flow' }]);
    const { getByText } = render(
      <Provider store={store}>
        <QueryClientProvider client={client}>
          <BrowserRouter>
            <DashboardPage />
          </BrowserRouter>
        </QueryClientProvider>
      </Provider>
    );

    expect(getByText(/My Flows/)).toBeTruthy();
  });
});
