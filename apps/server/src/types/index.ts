export interface RepoConfig {
  path: string;
  schedule: {
    review: string;
    compound: string;
  };
  priorities_dir: string;
  logs_dir: string;
  tasks_dir: string;
  enabled: boolean;
  github: {
    owner: string;
    repo: string;
    default_branch: string;
  };
  env?: Record<string, string>;
}

export interface ReposConfig {
  repos: Record<string, RepoConfig>;
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
