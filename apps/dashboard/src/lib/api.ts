import type {
  Repository,
  AgentStatus,
  Priority,
  LogEntry,
  ApiResponse,
  InboxItem,
  WorkspaceTask,
  CheckIn,
  MemoryEntry,
  FollowUp,
  WorkspaceOverview,
  PlanDocument,
  SetupStatus,
  Team,
  Agent,
  Session,
  DbTask,
  DashboardStats,
  JobInfo,
  DbIntegration,
  ScheduleRun,
  SystemHealth,
} from '../types';

const API_BASE =
  typeof window !== 'undefined' && window.location?.origin
    ? `${window.location.origin}/api`
    : '/api';

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  const text = await response.text();
  if (!text || !text.trim()) {
    throw new Error(
      response.ok
        ? 'Empty response from server'
        : `Server error ${response.status}: ${response.statusText}`
    );
  }

  let data: ApiResponse<T>;
  try {
    data = JSON.parse(text) as ApiResponse<T>;
  } catch {
    throw new Error(
      response.ok
        ? 'Invalid JSON response'
        : `Server error ${response.status}: ${response.statusText}`
    );
  }

  if (!data.success) {
    throw new Error(data.error || 'API request failed');
  }

  return data.data as T;
}

/** Fetch raw JSON from endpoints that don't use { success, data } wrapper */
async function fetchRaw<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error((err as { error?: string }).error || 'Request failed');
  }

  return response.json() as Promise<T>;
}

/** Fetch text from endpoints that return text/plain */
async function fetchText(url: string): Promise<string> {
  const response = await fetch(`${API_BASE}${url}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error((err as { error?: string }).error || 'Request failed');
  }
  return response.text();
}

// Repository API
export async function listRepositories(): Promise<Repository[]> {
  return fetchApi<Repository[]>('/repos');
}

export async function getRepository(name: string): Promise<Repository> {
  return fetchApi<Repository>(`/repos/${name}`);
}

export async function getRepositoryStatus(name: string): Promise<AgentStatus> {
  return fetchApi<AgentStatus>(`/repos/${name}/status`);
}

export async function getRepositoryPriorities(name: string): Promise<Priority[]> {
  return fetchApi<Priority[]>(`/repos/${name}/priorities`);
}

export async function getRepositoryLogs(
  name: string,
  limit: number = 100
): Promise<LogEntry[]> {
  return fetchApi<LogEntry[]>(`/repos/${name}/logs?limit=${limit}`);
}

// Agent Control API
export async function triggerAgent(
  name: string,
  workflow: 'compound' | 'review' = 'compound'
): Promise<void> {
  await fetchApi<void>(`/agents/trigger/${name}`, {
    method: 'POST',
    body: JSON.stringify({ workflow }),
  });
}

export async function cancelAgent(name: string): Promise<void> {
  await fetchApi<void>(`/agents/cancel/${name}`, {
    method: 'POST',
  });
}

export async function getRunningAgents(): Promise<
  Array<{ name: string; startTime: string; uptime: number }>
> {
  return fetchApi<Array<{ name: string; startTime: string; uptime: number }>>(
    '/agents/running'
  );
}

// ─── Workspace API ──────────────────────────────────────────────────────────

export async function getWorkspaceOverview(repo: string): Promise<WorkspaceOverview> {
  return fetchApi<WorkspaceOverview>(`/workspace/${repo}/overview`);
}

export async function getWorkspaceInbox(repo: string): Promise<InboxItem[]> {
  return fetchApi<InboxItem[]>(`/workspace/${repo}/inbox`);
}

export async function addToInbox(repo: string, text: string): Promise<void> {
  await fetchApi<void>(`/workspace/${repo}/inbox`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function getWorkspacePriorities(repo: string): Promise<Priority[]> {
  return fetchApi<Priority[]>(`/workspace/${repo}/priorities`);
}

export async function getWorkspaceTasks(repo: string): Promise<WorkspaceTask[]> {
  return fetchApi<WorkspaceTask[]>(`/workspace/${repo}/tasks`);
}

export async function getWorkspaceCheckIns(
  repo: string,
  type?: 'daily' | 'weekly' | 'monthly'
): Promise<CheckIn[]> {
  const query = type ? `?type=${type}` : '';
  return fetchApi<CheckIn[]>(`/workspace/${repo}/check-ins${query}`);
}

export async function getWorkspaceMemory(repo: string): Promise<MemoryEntry[]> {
  return fetchApi<MemoryEntry[]>(`/workspace/${repo}/memory`);
}

export async function getWorkspaceFollowUps(repo: string): Promise<FollowUp[]> {
  return fetchApi<FollowUp[]>(`/workspace/${repo}/follow-ups`);
}

export async function addFollowUp(
  repo: string,
  text: string,
  dueDate?: string
): Promise<void> {
  await fetchApi<void>(`/workspace/${repo}/follow-ups`, {
    method: 'POST',
    body: JSON.stringify({ text, dueDate }),
  });
}

// ─── Plans & Setup API ──────────────────────────────────────────────────────

export async function getPlans(): Promise<PlanDocument[]> {
  return fetchApi<PlanDocument[]>('/plans');
}

export async function getPlan(slug: string): Promise<PlanDocument> {
  return fetchApi<PlanDocument>(`/plans/${slug}`);
}

export async function getSetupStatus(repo: string): Promise<SetupStatus> {
  return fetchApi<SetupStatus>(`/plans/setup-status?repo=${repo}`);
}

// ─── SQLite-backed APIs ─────────────────────────────────────────────────────

// Teams & Agents
export async function getTeams(): Promise<Team[]> {
  return fetchApi<Team[]>('/teams');
}

export async function getTeam(teamId: string): Promise<Team> {
  return fetchApi<Team>(`/teams/${teamId}`);
}

/** Run seed data so missing teams (e.g. Schedule optimization) appear. */
export async function runTeamsSeed(): Promise<void> {
  const res = await fetch(`${API_BASE}/teams/seed`, { method: 'POST' });
  const json = await res.json();
  if (!json.success) throw new Error(json.error || 'Seed failed');
}

export async function getTeamAgents(teamId: string): Promise<Agent[]> {
  return fetchApi<Agent[]>(`/teams/${teamId}/agents`);
}

/** Create a new agent */
export async function createAgent(params: {
  teamId: string;
  name: string;
  role: string;
  llmPreference?: string;
  emoji?: string;
  id?: string;
}): Promise<Agent> {
  const id = params.id ?? `agent-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  const res = await fetchApi<Agent>('/teams/agents', {
    method: 'POST',
    body: JSON.stringify({
      id,
      teamId: params.teamId,
      name: params.name,
      role: params.role,
      llmPreference: params.llmPreference ?? 'sonnet',
      emoji: params.emoji ?? '🤖',
    }),
  });
  return res;
}

/** Deactivate (fire) an agent */
export async function fireAgent(agentId: string): Promise<void> {
  await fetchApi<{ success: boolean }>(`/teams/agents/${agentId}/deactivate`, {
    method: 'POST',
  });
}

/** Reactivate (rehire) an agent */
export async function rehireAgent(agentId: string): Promise<void> {
  await fetchApi<Agent>(`/teams/agents/${agentId}/reactivate`, {
    method: 'POST',
  });
}

export async function getAllAgentsFromDb(): Promise<Agent[]> {
  return fetchApi<Agent[]>('/teams/agents/all');
}

/** Alias for Engineering page - all agents from database */
export async function getHrAgents(): Promise<Agent[]> {
  return getAllAgentsFromDb();
}

// ─── Jobs (Engineering) ─────────────────────────────────────────────────────

/** Get all jobs from job executor */
export async function getJobs(): Promise<JobInfo[]> {
  const data = await fetchRaw<JobInfo[] | { jobs?: JobInfo[] }>('/jobs');
  return Array.isArray(data) ? data : (data.jobs ?? []);
}

/** Start a job (engineering or marketing). For engineering only team + targetRepo are required. Pass sessionId so the orchestrator uses the same session (Work view). */
export async function startJob(params: {
  team: string;
  model?: string;
  priorityFile?: string;
  branchName?: string;
  baseBranch?: string;
  targetRepo?: string;
  sessionId?: string;
}): Promise<JobInfo> {
  return fetchRaw<JobInfo>('/jobs/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/** Stop a job by ID */
export async function stopJob(jobId: string): Promise<void> {
  const data = await fetchRaw<{ success?: boolean; error?: string }>(
    `/jobs/${jobId}/stop`,
    { method: 'POST' }
  );
  if (data.success === false) {
    throw new Error(data.error || 'Failed to stop job');
  }
}

/** Get job logs as text */
export async function getJobLogs(jobId: string): Promise<string> {
  return fetchText(`/jobs/${jobId}/logs`);
}

/** Clear all jobs (memory + log/metadata files). Removes failed and stale entries. */
export async function clearAllJobs(): Promise<{ cleared: number; message: string }> {
  const data = await fetchRaw<{ success: boolean; cleared?: number; message?: string; error?: string }>(
    '/jobs/clear',
    { method: 'POST' }
  );
  if (data.success === false) {
    throw new Error(data.error ?? 'Failed to clear jobs');
  }
  return { cleared: data.cleared ?? 0, message: data.message ?? 'Cleared.' };
}

/** Get agent script content (agents/*.sh) */
export async function getAgentScript(agentId: string): Promise<string> {
  return fetchText(`/file/agent-script?agentId=${encodeURIComponent(agentId)}`);
}

/** Get agent prompt content (target repo .claude/prompts/*.md) */
export async function getAgentPrompt(agentId: string, repo = 'appcaire'): Promise<string> {
  return fetchText(
    `/file/agent-prompt?agentId=${encodeURIComponent(agentId)}&repo=${encodeURIComponent(repo)}`
  );
}

// Sessions
export async function getSessions(limit = 50): Promise<Session[]> {
  return fetchApi<Session[]>(`/sessions?limit=${limit}`);
}

export async function getActiveSessions(): Promise<Session[]> {
  return fetchApi<Session[]>('/sessions/active');
}

export async function getSessionDetail(sessionId: string): Promise<Session> {
  return fetchApi<Session>(`/sessions/${sessionId}`);
}

export async function createSession(params: {
  sessionId: string;
  teamId: string;
  targetRepo: string;
  priorityFile?: string;
  branchName?: string;
}): Promise<Session> {
  return fetchApi<Session>('/sessions', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

// Dashboard Stats
export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchApi<DashboardStats>('/metrics/stats');
}

// Tasks (Kanban)
export async function getAllDbTasks(): Promise<DbTask[]> {
  return fetchApi<DbTask[]>('/metrics/tasks');
}

/** Alias for Kanban - fetch all tasks */
export async function getTasks(): Promise<DbTask[]> {
  return getAllDbTasks();
}

/** Update task status (for Kanban drag & drop) */
export async function updateTaskStatus(
  taskId: string,
  status: string,
): Promise<void> {
  await fetchApi<void>(`/metrics/tasks/${taskId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

// Marketing
export async function getCampaigns(): Promise<unknown[]> {
  return fetchApi<unknown[]>('/marketing/campaigns');
}

export async function getLeads(): Promise<unknown[]> {
  return fetchApi<unknown[]>('/marketing/leads');
}

export async function getContent(): Promise<unknown[]> {
  return fetchApi<unknown[]>('/marketing/content');
}

// ─── Integrations (Settings) ────────────────────────────────────────────────

/** Get all integrations */
export async function getIntegrations(): Promise<DbIntegration[]> {
  const data = await fetchRaw<DbIntegration[] | { integrations?: DbIntegration[] }>(
    '/integrations'
  );
  return Array.isArray(data) ? data : (data.integrations ?? []);
}

/** Update an integration */
export async function updateIntegration(
  id: string,
  updates: Partial<DbIntegration>
): Promise<void> {
  await fetchRaw<{ success: boolean }>(`/integrations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

// ─── RL / Experiments & Patterns ────────────────────────────────────────────

/** Get active experiments */
export async function getExperiments(): Promise<unknown[]> {
  return fetchApi<unknown[]>('/metrics/experiments/active');
}

/** Get patterns */
export async function getPatterns(type?: string): Promise<unknown[]> {
  const query = type ? `?type=${type}` : '';
  return fetchApi<unknown[]>(`/metrics/patterns${query}`);
}

// ─── LLM Usage (Analytics) ───────────────────────────────────────────────────

export interface LLMUsageRecord {
  id: number;
  taskId: string | null;
  model: string;
  inputTokens: number;
  outputTokens: number;
  costUsd: number;
  durationMs: number | null;
  usedAt: string;
}

export interface LLMStatsByModel {
  model: string;
  usageCount: number;
  totalInputTokens: number;
  totalOutputTokens: number;
  totalCost: number;
  avgDuration: string;
  costPercentage: string;
}

export interface LLMStatsResponse {
  period: string;
  totalCost: string;
  byModel: LLMStatsByModel[];
}

/** Get LLM usage stats (aggregates by model) */
export async function getLLMStats(days = 7): Promise<LLMStatsResponse> {
  return fetchRaw<LLMStatsResponse>(`/rl/llm-stats?days=${days}`);
}

/** Get raw LLM usage records (for timeline) */
export async function getLLMUsage(days = 7, limit = 200): Promise<LLMUsageRecord[]> {
  return fetchRaw<LLMUsageRecord[]>(`/rl/llm-usage?days=${days}&limit=${limit}`);
}

// ─── Schedule optimization (Timefold FSR runs) ───────────────────────────────

export async function getScheduleRuns(dataset?: string): Promise<ScheduleRun[]> {
  const url = dataset ? `/schedule-runs?dataset=${encodeURIComponent(dataset)}` : '/schedule-runs';
  const data = await fetchApi<{ runs?: ScheduleRun[] } | ScheduleRun[]>(url);
  if (Array.isArray(data)) return data;
  return data?.runs ?? [];
}

export async function cancelScheduleRun(id: string, reason?: string): Promise<ScheduleRun> {
  const data = await fetchApi<ScheduleRun>(`/schedule-runs/${id}/cancel`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason ?? 'Cancelled by user' }),
  });
  return data;
}

/** Import schedule runs from shared huddinge-datasets; or seed sample runs if empty. */
export async function importScheduleRunsFromAppcaire(): Promise<{
  success: boolean;
  imported?: number;
  seeded?: number;
  appcairePath?: string;
  batchesScanned?: string[];
  message?: string;
  error?: string;
}> {
  return fetchApi('/schedule-runs/import-from-appcaire');
}

/** Get a single schedule run by id */
export async function getScheduleRun(id: string): Promise<ScheduleRun | null> {
  const data = await fetchApi<{ run: ScheduleRun }>(`/schedule-runs/${id}`);
  return data?.run ?? null;
}

/** Get run metrics JSON from shared folder (metrics/metrics_*.json) */
export async function getRunMetricsJson(id: string): Promise<Record<string, unknown> | null> {
  const res = await fetch(`${API_BASE}/schedule-runs/${id}/files/metrics-json`);
  if (!res.ok) return null;
  return res.json();
}

/** Get run metrics report text from shared folder */
export async function getRunMetricsReport(id: string): Promise<string | null> {
  const res = await fetch(`${API_BASE}/schedule-runs/${id}/files/metrics-report`);
  if (!res.ok) return null;
  return res.text();
}

/** Get run continuity CSV from shared folder */
export async function getRunContinuity(id: string): Promise<string | null> {
  const res = await fetch(`${API_BASE}/schedule-runs/${id}/files/continuity`);
  if (!res.ok) return null;
  return res.text();
}

/** URL to dataset-level asset (e.g. pilot report PDF) in shared folder */
export function getDatasetAssetUrl(filename: string): string {
  return `${API_BASE}/schedule-runs/dataset-assets/${encodeURIComponent(filename)}`;
}

// ─── System Health ───────────────────────────────────────────────────────────

export async function getSystemHealth(deep = false): Promise<SystemHealth> {
  const query = deep ? '?deep=1' : '';
  return fetchApi<SystemHealth>(`/system/health${query}`);
}
