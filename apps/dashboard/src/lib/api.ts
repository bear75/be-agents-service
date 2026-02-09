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
} from '../types';

const API_BASE = '/api';

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  const data: ApiResponse<T> = await response.json();

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

// ─── Sessions API (raw response) ─────────────────────────────────────────────

export async function getSessions(): Promise<DbSession[]> {
  return fetchRaw<DbSession[]>('/sessions');
}

export async function getSession(sessionId: string): Promise<DbSessionWithTasks> {
  return fetchRaw<DbSessionWithTasks>(`/sessions/${sessionId}`);
}

// ─── Tasks API (raw response) ────────────────────────────────────────────────

export interface GetTasksParams {
  team_id?: string;
  agent_id?: string;
  session_id?: string;
  status?: string;
}

export async function getTasks(params?: GetTasksParams): Promise<DbTask[]> {
  const q = new URLSearchParams(params as Record<string, string>).toString();
  return fetchRaw<DbTask[]>(`/tasks${q ? `?${q}` : ''}`);
}

// ─── Jobs API (raw response) ────────────────────────────────────────────────

export interface StartJobParams {
  team: 'engineering' | 'marketing';
  priorityFile: string;
  branchName: string;
  model?: string;
  baseBranch?: string;
  targetRepo?: string;
}

export async function getJobs(): Promise<JobInfo[]> {
  return fetchRaw<JobInfo[]>('/jobs');
}

export async function startJob(params: StartJobParams): Promise<JobInfo> {
  return fetchRaw<JobInfo>('/jobs/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function stopJob(jobId: string): Promise<{ success: boolean }> {
  return fetchRaw<{ success: boolean }>(`/jobs/${jobId}/stop`, {
    method: 'POST',
  });
}

export async function getJobStatus(jobId: string): Promise<JobInfo> {
  return fetchRaw<JobInfo>(`/jobs/${jobId}/status`);
}

export async function getJobLogs(jobId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/logs`);
  if (!res.ok) throw new Error('Failed to fetch logs');
  return res.text();
}

export async function triggerNightlyJob(): Promise<{ success: boolean }> {
  return fetchRaw<{ success: boolean }>('/jobs/nightly/trigger', {
    method: 'POST',
  });
}

// ─── HR Agents API (raw response) ────────────────────────────────────────────

export async function getHrAgents(): Promise<DbAgent[]> {
  return fetchRaw<DbAgent[]>('/agents');
}

export async function createAgent(params: {
  teamId: string;
  name: string;
  role: string;
  llmPreference?: string;
  emoji?: string;
}): Promise<{ success: boolean; agent: DbAgent }> {
  return fetchRaw('/agents/create', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function fireAgent(id: string): Promise<void> {
  await fetchRaw(`/agents/${id}/fire`, { method: 'POST' });
}

export async function rehireAgent(id: string): Promise<{ agent: DbAgent }> {
  return fetchRaw(`/agents/${id}/rehire`, { method: 'POST' });
}

// ─── Data API (campaigns, leads) ────────────────────────────────────────────

export async function getCampaigns(): Promise<DbCampaign[]> {
  return fetchRaw<DbCampaign[]>('/data/campaigns');
}

export async function getLeads(): Promise<DbLead[]> {
  return fetchRaw<DbLead[]>('/data/leads');
}

// ─── Integrations API ───────────────────────────────────────────────────────

export async function getIntegrations(): Promise<DbIntegration[]> {
  return fetchRaw<DbIntegration[]>('/integrations');
}

export async function updateIntegration(
  id: string,
  data: Partial<DbIntegration>
): Promise<void> {
  await fetchRaw(`/integrations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// ─── RL API ─────────────────────────────────────────────────────────────────

export async function getExperiments(): Promise<DbExperiment[]> {
  return fetchRaw<DbExperiment[]>('/rl/experiments');
}

export async function getPatterns(): Promise<unknown> {
  return fetchRaw('/rl/patterns');
}

// ─── Teams API ──────────────────────────────────────────────────────────────

export async function getTeams(): Promise<DbTeam[]> {
  return fetchRaw<DbTeam[]>('/teams');
}

export async function getTeam(id: string): Promise<DbTeamWithDetails> {
  return fetchRaw<DbTeamWithDetails>(`/teams/${id}`);
}

export async function createTeam(params: {
  id: string;
  name: string;
  domain: 'engineering' | 'marketing' | 'management';
  description?: string;
}): Promise<{ success: boolean; team: DbTeam }> {
  return fetchRaw('/teams', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function updateTeam(
  id: string,
  updates: { name?: string; description?: string }
): Promise<{ success: boolean; team: DbTeam }> {
  return fetchRaw(`/teams/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

// ─── Task Management API (Kanban) ───────────────────────────────────────────

export async function getTask(id: string): Promise<DbTask> {
  return fetchRaw<DbTask>(`/tasks/${id}`);
}

export async function createTask(params: {
  sessionId: string;
  agentId: string;
  description: string;
  priority?: 'low' | 'medium' | 'high';
}): Promise<{ success: boolean; task: DbTask }> {
  return fetchRaw('/tasks', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function updateTask(
  id: string,
  updates: { description?: string; priority?: string }
): Promise<{ success: boolean; task: DbTask }> {
  return fetchRaw(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function updateTaskStatus(
  id: string,
  status: 'pending' | 'in_progress' | 'completed' | 'failed',
  llmUsed?: string,
  errorMessage?: string
): Promise<{ success: boolean; task: DbTask }> {
  return fetchRaw(`/tasks/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, llmUsed, errorMessage }),
  });
}
