const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Token management
const TOKEN_KEY = 'auth_token';

export const authUtils = {
  setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
  },
  
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },
  
  removeToken() {
    localStorage.removeItem(TOKEN_KEY);
  },
  
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
};

// Helper to add auth header
function getAuthHeaders(): HeadersInit {
  const token = authUtils.getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

// Auth interfaces
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  createdAt: string;
}

// Job interfaces
export interface ImportJob {
  jobId: number;
  status: string;
  selectedSources: string[];
  progress: Record<string, SourceProgress>;
  error: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface SourceProgress {
  completed: number;
  total: number;
  status: string;
}

export interface CreateJobRequest {
  selectedSources: string[];
  credentials: Record<string, Record<string, string>>;
}

export interface CreateJobResponse {
  jobId: number;
  status: string;
  createdAt: string;
}

export interface ImportedItem {
  id: number;
  source: string;
  remoteId: number;
  status: string;
  createdAt: string;
  payload: any;
}

export interface DashboardStats {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  totalProducts: number;
  totalCarts: number;
  recentItems: ImportedItem[];
}

export const api = {
  // Auth endpoints
  async register(request: RegisterRequest): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to register');
    }
    
    const data = await response.json();
    authUtils.setToken(data.accessToken);
    return data;
  },

  async login(request: LoginRequest): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to login');
    }
    
    const data = await response.json();
    authUtils.setToken(data.accessToken);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authUtils.removeToken();
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get user');
    }
    
    return response.json();
  },

  logout() {
    authUtils.removeToken();
  },

  // Job endpoints
  async createJob(request: CreateJobRequest): Promise<CreateJobResponse> {
    const response = await fetch(`${API_BASE_URL}/import_jobs`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authUtils.removeToken();
        window.location.href = '/login';
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create job');
    }
    
    return response.json();
  },

  async getJob(jobId: number): Promise<ImportJob> {
    const response = await fetch(`${API_BASE_URL}/import_jobs/${jobId}`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authUtils.removeToken();
        window.location.href = '/login';
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get job');
    }
    
    return response.json();
  },

  async listJobs(): Promise<ImportJob[]> {
    const response = await fetch(`${API_BASE_URL}/import_jobs`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authUtils.removeToken();
        window.location.href = '/login';
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to list jobs');
    }
    
    return response.json();
  },

  async getDashboard(): Promise<DashboardStats> {
    const response = await fetch(`${API_BASE_URL}/dashboard`, {
      headers: getAuthHeaders(),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authUtils.removeToken();
        window.location.href = '/login';
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get dashboard stats');
    }
    
    return response.json();
  },
};
