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

// ─── Shared Markdown Workspace Types ─────────────────────────────────────────

export interface InboxItem {
  id: string;
  text: string;
  done: boolean;
  date?: string;
  tags?: string[];
}

export interface WorkspaceTask {
  id: string;
  title: string;
  status: 'pending' | 'in-progress' | 'done' | 'blocked';
  priority?: 'high' | 'medium' | 'low';
  branch?: string;
  agent?: string;
  startedAt?: string;
  completedAt?: string;
  pr?: string;
  notes?: string;
}

export interface CheckIn {
  date: string;
  type: 'daily' | 'weekly' | 'monthly';
  filename: string;
  content: string;
  sections: Record<string, string>;
}

export interface MemoryEntry {
  filename: string;
  title: string;
  content: string;
  lastModified: string;
}

export interface FollowUp {
  id: string;
  text: string;
  done: boolean;
  dueDate?: string;
  tags?: string[];
}

export interface PlanDocument {
  slug: string;
  filename: string;
  title: string;
  priority?: number;
  status: 'planning' | 'in-progress' | 'blocked' | 'done' | 'docs-only';
  summary?: string;
  limitations?: string[];
  content?: string;
  lastModified: string;
}

export interface SetupStatus {
  workspace: {
    configured: boolean;
    exists: boolean;
    path?: string;
  };
  openclaw: {
    configured: boolean;
    configPath?: string;
  };
  telegram: {
    configured: boolean;
  };
  launchd: {
    morningBriefing: boolean;
    weeklyReview: boolean;
  };
}

export interface WorkspaceOverview {
  inbox: {
    total: number;
    pending: number;
    items: InboxItem[];
  };
  priorities: Priority[];
  tasks: {
    inProgress: WorkspaceTask[];
    pending: WorkspaceTask[];
    done: WorkspaceTask[];
  };
  latestCheckIn?: CheckIn;
  followUps: {
    total: number;
    pending: number;
    items: FollowUp[];
  };
  agentReport?: string;
}
