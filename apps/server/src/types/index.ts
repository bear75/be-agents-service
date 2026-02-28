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

/** A plan/PRD document from docs/ */
export interface PlanDocument {
  slug: string;
  filename: string;
  title: string;
  priority?: number;
  status: 'planning' | 'in-progress' | 'blocked' | 'done' | 'docs-only';
  summary?: string;
  limitations?: string[];
  content: string;
  lastModified: string;
}

/** Setup readiness status for the workspace */
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

// ─── SQLite Database Types ────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
  domain: 'engineering' | 'marketing' | 'management';
  description: string | null;
  created_at: string;
  updated_at: string;
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
  is_active: number;
  created_at: string;
  updated_at: string;
}

export interface Session {
  id: string;
  team_id: string;
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
}

export interface Task {
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
  retry_count: number;
}

export interface Experiment {
  id: string;
  name: string;
  description: string | null;
  status: 'active' | 'successful' | 'failed' | 'killed';
  success_metric: string;
  target_value: number | null;
  current_value: number | null;
  sample_size: number;
  consecutive_failures: number;
  decision: string | null;
  decision_reason: string | null;
  decided_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MetricRecord {
  id: number;
  entity_type: string;
  entity_id: string;
  metric_name: string;
  metric_value: number;
  context: string | null;
  recorded_at: string;
}

export interface Pattern {
  id: string;
  pattern_type: 'success' | 'failure' | 'user_repetition';
  description: string;
  detection_count: number;
  confidence_score: number;
  status: 'active' | 'verified' | 'false_positive' | 'actioned';
  action_taken: string | null;
  first_detected_at: string;
  last_detected_at: string;
  actioned_at: string | null;
}

export interface Reward {
  entityType: string;
  entityId: string;
  rewardValue: number;
  reason: string;
}

export interface UserCommand {
  normalized_intent: string;
  occurrence_count: number;
  last_executed: string;
  teams_used: string;
  models_used: string;
}

export interface AutomationCandidate {
  id: string;
  pattern_description: string;
  occurrence_count: number;
  sample_commands: string;
  confidence_score: number;
  is_automated: number;
  agent_id: string | null;
  approved_by_user: number;
  approved_at: string | null;
  created_at: string;
  last_occurrence_at: string;
}

export interface Campaign {
  id: string;
  name: string;
  type: string;
  owner: string | null;
  status: 'draft' | 'active' | 'paused' | 'completed';
  channels: string | null;
  deliverables: string | null;
  metrics: string | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  source: string;
  contact_name: string | null;
  contact_email: string | null;
  company: string | null;
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost';
  score: number;
  assigned_to: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentPiece {
  id: string;
  title: string;
  type: 'blog' | 'email' | 'social' | 'landing-page' | 'docs';
  status: 'draft' | 'review' | 'published';
  author: string | null;
  campaign_id: string | null;
  word_count: number | null;
  seo_score: number | null;
  file_path: string | null;
  published_url: string | null;
  created_at: string;
  published_at: string | null;
}

export interface LessonLearned {
  id: string;
  category: string | null;
  title: string;
  description: string;
  source: string | null;
  times_encountered: number;
  is_automated: number;
  automated_via: string | null;
  created_at: string;
  last_encountered_at: string;
}

export interface AgentPerformanceView {
  id: string;
  name: string;
  role: string;
  team_name: string;
  total_tasks_completed: number;
  total_tasks_failed: number;
  success_rate_pct: number;
  avg_duration_minutes: number;
}

export interface ActiveSessionView {
  id: string;
  team_id: string;
  team_name: string;
  status: string;
  target_repo: string;
  branch_name: string | null;
  agent_count: number;
  task_count: number;
  started_at: string;
}

// ─── Schedule Optimization (Timefold FSR runs) ─────────────────────────────

export interface ScheduleRun {
  id: string;
  dataset: string;
  batch: string;
  algorithm: string;
  strategy: string;
  hypothesis: string | null;
  status: 'queued' | 'running' | 'completed' | 'cancelled' | 'failed';
  decision: string | null;
  decision_reason: string | null;
  timefold_score: string | null;
  routing_efficiency_pct: number | null;
  unassigned_visits: number | null;
  total_visits: number | null;
  unassigned_pct: number | null;
  continuity_avg: number | null;
  continuity_median: number | null;
  continuity_visit_weighted_avg: number | null;
  continuity_max: number | null;
  continuity_over_target: number | null;
  continuity_target: number | null;
  input_shifts: number | null;
  input_shift_hours: number | null;
  output_shifts_trimmed: number | null;
  output_shift_hours_trimmed: number | null;
  shift_hours_total: number | null;
  shift_hours_idle: number | null;
  efficiency_total_pct: number | null;
  efficiency_trimmed_pct: number | null;
  eff_v1_pct: number | null;
  idle_shifts_v1: number | null;
  idle_shift_hours_v1: number | null;
  eff_v2_pct: number | null;
  idle_shifts_v2: number | null;
  idle_shift_hours_v2: number | null;
  submitted_at: string;
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  duration_seconds: number | null;
  output_path: string | null;
  notes: string | null;
  iteration: number;
}
