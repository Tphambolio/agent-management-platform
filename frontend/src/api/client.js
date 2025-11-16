import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API collections for easier imports
export const agentsAPI = {
  list: (params) => apiClient.get('/api/agents', { params }),
  get: (id) => apiClient.get(`/api/agents/${id}`),
  create: (data) => apiClient.post('/api/agents', data),
  createIntelligent: (data) => apiClient.post('/api/agents/create-intelligent', data),
  sync: () => apiClient.post('/api/agents/sync'),
};

export const tasksAPI = {
  list: (params) => apiClient.get('/api/tasks', { params }),
  get: (id) => apiClient.get(`/api/tasks/${id}`),
  create: (data) => apiClient.post('/api/tasks', data),
  execute: (id) => apiClient.post(`/api/tasks/${id}/execute`),
};

export const reportsAPI = {
  list: (params) => apiClient.get('/api/reports', { params }),
  get: (id) => apiClient.get(`/api/reports/${id}`),
};

export const projectsAPI = {
  list: () => apiClient.get('/api/projects'),
  create: (data) => apiClient.post('/api/projects', data),
};

export const healthAPI = {
  check: () => apiClient.get('/health'),
  stats: () => apiClient.get('/api/stats'),
};

export const knowledgeAPI = {
  list: (params) => apiClient.get('/api/knowledge', { params }),
  search: (query, limit = 10) => apiClient.get('/api/knowledge/search', { params: { q: query, limit } }),
  get: (id) => apiClient.get(`/api/knowledge/${id}`),
  getPDF: (id) => `${API_BASE_URL}/api/knowledge/${id}/pdf`,
  stats: () => apiClient.get('/api/knowledge/stats'),
};

export const geospatialAPI = {
  capabilities: () => apiClient.get('/api/geospatial/capabilities'),
  downloadSatellite: (data) => apiClient.post('/api/geospatial/download-satellite', data),
};

// Backward compatibility - individual exports
export const getAgents = () => apiClient.get('/api/agents');
export const getAgent = (id) => apiClient.get(`/api/agents/${id}`);
export const syncAgents = () => apiClient.post('/api/agents/sync');
export const getTasks = (params) => apiClient.get('/api/tasks', { params });
export const getTask = (id) => apiClient.get(`/api/tasks/${id}`);
export const createTask = (data) => apiClient.post('/api/tasks', data);
export const getReports = (params) => apiClient.get('/api/reports', { params });
export const getReport = (id) => apiClient.get(`/api/reports/${id}`);
export const getProjects = () => apiClient.get('/api/projects');
export const createProject = (data) => apiClient.post('/api/projects', data);
export const getStats = () => apiClient.get('/api/stats');

export default apiClient;
