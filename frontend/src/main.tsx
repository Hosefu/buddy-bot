import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { AppQueryClientProvider } from './app/providers/QueryClientProvider';
import { App } from './app/App';
import { store } from './app/store';
import './styles.css';
import './shared/utils/httpDebug';

console.log('%c[LS] auth =>', 'color:#ffa502', localStorage.getItem('auth'));

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Provider store={store}>
      <AppQueryClientProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AppQueryClientProvider>
    </Provider>
  </React.StrictMode>
);
