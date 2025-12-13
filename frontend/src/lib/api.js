import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (email, password) =>
    api.post('/api/v1/auth/register', { email, password }),

  login: (email, password) =>
    api.post('/api/v1/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getMe: () => api.get('/api/v1/auth/me'),
};

// Monitor APIs
export const monitorAPI = {
  list: () => api.get('/api/v1/monitors/'),
  get: (id) => api.get(`/api/v1/monitors/${id}`),
  create: (data) => api.post('/api/v1/monitors/', data),
  update: (id, data) => api.put(`/api/v1/monitors/${id}`, data),
  delete: (id) => api.delete(`/api/v1/monitors/${id}`),
};

// Metrics APIs
export const metricsAPI = {
  getHealthChecks: (monitorId, params) =>
    api.get(`/api/v1/metrics/${monitorId}/health-checks`, { params }),

  getStats: (monitorId, hours = 24) =>
    api.get(`/api/v1/metrics/${monitorId}/stats`, { params: { hours } }),

  getIncidents: (monitorId) =>
    api.get(`/api/v1/metrics/${monitorId}/incidents`),

  getDashboard: (hours = 24) =>
    api.get('/api/v1/metrics/dashboard', { params: { hours } }),
};

export default api;
