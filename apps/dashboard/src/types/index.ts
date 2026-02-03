export interface Repository {
  name: string;
  enabled: boolean;
  path: string;
  valid: boolean;
  schedule: {
    review: string;
    compound: string;
  };
  github: {
    owner: string;
    repo: string;
    default_branch: string;
  };
}

export interface AgentStatus {
  name: string;
  enabled: boolean;
  running: boolean;
  lastRun?: string;
  lastSuccess?: string;
  lastError?: string;
  nextScheduledRun?: {
    review: string;
    compound: string;
  };
}

export interface Priority {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
}

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'error' | 'warn' | 'debug';
  message: string;
  source: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
