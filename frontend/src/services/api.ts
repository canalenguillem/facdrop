import axios from 'axios';

// VITE_API_URL apunta al backend (ej: http://localhost:18080). La API cuelga de /api.
const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? ''}/api`,
});

// Adjunta el JWT en cada petición si existe.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Si el backend devuelve 401, limpia sesión y manda a login.
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      const path = window.location.pathname;
      if (!path.startsWith('/login') && !path.startsWith('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default api;
