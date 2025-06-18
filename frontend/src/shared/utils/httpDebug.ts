import axios from 'axios';

// Логирование axios
axios.interceptors.request.use((config) => {
  const { method, url, data } = config;
  console.log(`%c[AXIOS REQUEST] ${method?.toUpperCase()} ${url}`, 'color: #6ab04c', { data, config });
  return config;
});

axios.interceptors.response.use(
  (response) => {
    const { status, config, data } = response;
    console.log(`%c[AXIOS RESPONSE] ${status} ${config.url}`, 'color: #22a6b3', { data });
    return response;
  },
  (error) => {
    if (error.response) {
      const { status, config, data } = error.response;
      console.log(`%c[AXIOS ERROR] ${status} ${config.url}`, 'color: #eb4d4b', { data });
    } else {
      console.log('%c[AXIOS ERROR] Network or CORS', 'color: #eb4d4b', error);
    }
    return Promise.reject(error);
  }
);

// Логирование fetch
const originalFetch = window.fetch.bind(window);
window.fetch = async (...args) => {
  const [input, init] = args;
  const method = init?.method || 'GET';
  const url = typeof input === 'string' ? input : (input as Request).url;
  console.log(`%c[FETCH REQUEST] ${method} ${url}`, 'color: #f0932b', { init });
  try {
    const response = await originalFetch(...args);
    console.log(`%c[FETCH RESPONSE] ${response.status} ${url}`, 'color: #be2edd', response);
    return response;
  } catch (err) {
    console.log(`%c[FETCH ERROR] ${method} ${url}`, 'color: #eb4d4b', err);
    throw err;
  }
}; 