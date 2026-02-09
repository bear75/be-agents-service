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

// ─── DB types (sessions, tasks, agents, etc.) ───────────────────────────────

export interface DbSession {
  id: string;
  team_id: string;
  status: string;
  target_repo?: string;
  branch_name?: string;
  pr_url?: string;
  started_at?: string;
  completed_at?: string;
  team_name?: string;
}

export interface DbSessionWithTasks extends DbSession {
  tasks: DbTask[];
}

export interface DbTask {
  id: string;
  agent_id: string;
  session_id: string;
  status: string;
  description?: string;
  priority?: string;
  llm_model?: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  agent_name?: string;
  team_name?: string;
  emoji?: string;
}

export interface JobInfo {
  jobId: string;
  type: string;
  model?: string;
  priorityFile?: string;
  branchName?: string;
  status: string;
  startTime?: string;
  endTime?: string;
  pid?: number;
  exitCode?: number;
}

export interface DbAgent {
  id: string;
  team_id: string;
  name: string;
  role: string;
  emoji?: string;
  llm_preference?: string;
  is_active?: boolean;
  team_name?: string;
}

export interface DbTeam {
  id: string;
  name: string;
  domain: 'engineering' | 'marketing' | 'management';
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DbTeamWithDetails extends DbTeam {
  agents: DbAgent[];
  stats: {
    total_tasks: number;
    completed_tasks: number;
    failed_tasks: number;
    in_progress_tasks: number;
    avg_duration_seconds: number;
    success_rate: string;
  };
}

export interface DbCampaign {
  id: string;
  name: string;
  status?: string;
  [key: string]: unknown;
}

export interface DbLead {
  id: string;
  source?: string;
  [key: string]: unknown;
}

export interface DbIntegration {
  id: string;
  type: string;
  name?: string;
  [key: string]: unknown;
}

export interface DbExperiment {
  id: string;
  [key: string]: unknown;
}
