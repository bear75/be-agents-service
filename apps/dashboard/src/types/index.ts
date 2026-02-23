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

// ─── SQLite Database Types (from API server) ─────────────────────────────────

export interface Team {
  id: string;
  name: string;
  domain: 'engineering' | 'marketing' | 'management';
  description: string | null;
  created_at: string;
  updated_at: string;
  agents?: Agent[];
}

export interface Agent {
  id: string;
  team_id: string;
  name: string;
  role: string;
  emoji: string | null;
  llm_preference: string;
  success_rate: number;
  total_tasks_completed: number;
  total_tasks_failed: number;
  avg_duration_seconds: number;
  is_active: number | boolean;
  team_name?: string;
  team_domain?: string;
  created_at?: string;
}

export interface Session {
  id: string;
  team_id: string;
  team_name?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked';
  target_repo: string;
  priority_file: string | null;
  branch_name: string | null;
  pr_url: string | null;
  iteration_count: number;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  exit_code: number | null;
  tasks?: DbTask[];
}

export interface DbTask {
  id: string;
  session_id: string;
  agent_id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | null;
  llm_used: string | null;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  agent_name?: string;
  agent_emoji?: string;
  team_name?: string;
}

export interface DashboardStats {
  totalSessions: number;
  activeSessions: number | null;
  totalTasks: number;
  completedTasks: number | null;
  failedTasks: number | null;
  totalAgents: number;
  activeAgents: number | null;
  totalExperiments: number;
  activeExperiments: number | null;
}

/** Agent from database (alias for Agent) */
export type DbAgent = Agent;

/** Job info from job executor */
export interface JobInfo {
  id: string;
  team?: string;
  status?: string;
  priorityFile?: string;
  branchName?: string;
  targetRepo?: string;
  startedAt?: string;
  [key: string]: unknown;
}

/** Integration from database (settings) */
export interface DbIntegration {
  id: string;
  type?: string;
  platform?: string;
  name?: string;
  is_active?: number;
  credentials?: unknown;
  config?: unknown;
  [key: string]: unknown;
}
