// ─── Repository Configuration ────────────────────────────────────────────────

export interface WorkspaceConfig {
  path: string;
  enabled: boolean;
}

export interface RepoConfig {
  path: string;
  workspace?: WorkspaceConfig;
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

// ─── Agent Status ────────────────────────────────────────────────────────────

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

// ─── Priorities (from reports/ in target repo) ──────────────────────────────

export interface Priority {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
}

// ─── Logs ────────────────────────────────────────────────────────────────────

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'error' | 'warn' | 'debug';
  message: string;
  source: string;
}

// ─── Shared Markdown Workspace Types ─────────────────────────────────────────

/** An item in inbox.md — quick-drop ideas, tasks, thoughts */
export interface InboxItem {
  id: string;
  text: string;
  done: boolean;
  date?: string;
  tags?: string[];
}

/** A task tracked in tasks.md with structured metadata */
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

/** A daily, weekly, or monthly check-in */
export interface CheckIn {
  date: string;
  type: 'daily' | 'weekly' | 'monthly';
  filename: string;
  content: string;
  sections: Record<string, string>;
}

/** A file from the memory/ directory */
export interface MemoryEntry {
  filename: string;
  title: string;
  content: string;
  lastModified: string;
}

/** An item in follow-ups.md */
export interface FollowUp {
  id: string;
  text: string;
  done: boolean;
  dueDate?: string;
  tags?: string[];
}

/** Combined overview of the entire workspace */
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
