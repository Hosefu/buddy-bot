import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { App } from './app/App';
import { store, persistor } from './app/store';
import './styles.css';
import './shared/utils/httpDebug';

console.log('%c[LS] auth =>', 'color:#ffa502', localStorage.getItem('auth'));

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <App />
      </PersistGate>
    </Provider>
  </React.StrictMode>
);
