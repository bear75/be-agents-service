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

export async function getTeamAgents(teamId: string): Promise<Agent[]> {
  return fetchApi<Agent[]>(`/teams/${teamId}/agents`);
}

export async function getAllAgentsFromDb(): Promise<Agent[]> {
  return fetchApi<Agent[]>('/teams/agents/all');
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
