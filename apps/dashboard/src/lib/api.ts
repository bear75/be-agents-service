import type {
  Repository,
  AgentStatus,
  Priority,
  LogEntry,
  ApiResponse,
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
