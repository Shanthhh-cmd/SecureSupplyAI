import axios from 'axios';
import {
  User, Project, ScanSession, ScanDetail, Vulnerability,
  SecurityPolicy, ExecutiveSummary
} from '../types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const projectService = {
  listProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },
  getProject: async (id: number): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
  createProject: async (formData: FormData): Promise<Project> => {
    const response = await api.post('/projects', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  deleteProject: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

export const scanService = {
  triggerScan: async (projectId: number): Promise<ScanDetail> => {
    const response = await api.post(`/scans/trigger/${projectId}`);
    return response.data;
  },
  getProjectScans: async (projectId: number): Promise<ScanSession[]> => {
    const response = await api.get(`/scans/project/${projectId}`);
    return response.data;
  },
  getScanDetail: async (scanId: number): Promise<ScanDetail> => {
    const response = await api.get(`/scans/${scanId}`);
    return response.data;
  },
  getScanSBOM: async (scanId: number): Promise<{ sbom: string }> => {
    const response = await api.get(`/scans/${scanId}/sbom`);
    return response.data;
  },
};

export const vulnerabilityService = {
  listVulnerabilities: async (severity?: string, cve?: string): Promise<Vulnerability[]> => {
    const params: Record<string, string> = {};
    if (severity) params.severity = severity;
    if (cve) params.cve = cve;
    const response = await api.get('/vulnerabilities', { params });
    return response.data;
  },
};

export const policyService = {
  listPolicies: async (): Promise<SecurityPolicy[]> => {
    const response = await api.get('/policies');
    return response.data;
  },
  createPolicy: async (policy: Partial<SecurityPolicy>): Promise<SecurityPolicy> => {
    const response = await api.post('/policies', policy);
    return response.data;
  },
  activatePolicy: async (id: number): Promise<SecurityPolicy> => {
    const response = await api.put(`/policies/${id}/activate`);
    return response.data;
  },
};

export const dashboardService = {
  getSummary: async (): Promise<ExecutiveSummary> => {
    const response = await api.get('/dashboard/summary');
    return response.data;
  },
};

export const reportService = {
  getDownloadUrl: (reportId: number) => `${API_BASE_URL}/reports/download/${reportId}`,
  listScanReports: async (scanId: number) => {
    const response = await api.get(`/reports/scan/${scanId}`);
    return response.data;
  },
};

export default api;
