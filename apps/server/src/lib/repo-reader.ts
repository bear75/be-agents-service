import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { resolve, join } from 'path';
import type { RepoConfig, Priority, LogEntry } from '../types/index.js';

/**
 * Read priorities from a repository's reports directory
 */
export function readPriorities(repoConfig: RepoConfig): Priority[] {
  const prioritiesDir = resolve(repoConfig.path, repoConfig.priorities_dir);

  if (!existsSync(prioritiesDir)) {
    return [];
  }

  // Find the latest priorities file
  const files = readdirSync(prioritiesDir)
    .filter((f) => f.startsWith('priorities-') && f.endsWith('.md'))
    .sort()
    .reverse();

  if (files.length === 0) {
    return [];
  }

  const latestFile = files[0];
  const filePath = join(prioritiesDir, latestFile);
  const content = readFileSync(filePath, 'utf8');

  // Parse markdown priorities (simple parsing)
  const priorities: Priority[] = [];
  const lines = content.split('\n');
  let currentPriority: 'high' | 'medium' | 'low' = 'medium';
  let id = 1;

  for (const line of lines) {
    if (line.startsWith('## High Priority')) {
      currentPriority = 'high';
    } else if (line.startsWith('## Medium Priority')) {
      currentPriority = 'medium';
    } else if (line.startsWith('## Low Priority')) {
      currentPriority = 'low';
    } else if (line.match(/^\d+\.\s+/)) {
      // Priority item line
      const title = line.replace(/^\d+\.\s+/, '').trim();
      priorities.push({
        id: id++,
        title,
        description: '',
        status: 'pending',
        priority: currentPriority,
      });
    }
  }

  return priorities;
}

/**
 * Read logs from a repository's logs directory
 */
export function readLogs(
  repoConfig: RepoConfig,
  limit: number = 100
): LogEntry[] {
  const logsDir = resolve(repoConfig.path, repoConfig.logs_dir);

  if (!existsSync(logsDir)) {
    return [];
  }

  const logFiles = readdirSync(logsDir)
    .filter((f) => f.endsWith('.log'))
    .map((f) => ({
      name: f,
      path: join(logsDir, f),
      mtime: statSync(join(logsDir, f)).mtime,
    }))
    .sort((a, b) => b.mtime.getTime() - a.mtime.getTime());

  if (logFiles.length === 0) {
    return [];
  }

  // Read the most recent log file
  const latestLog = logFiles[0];
  const content = readFileSync(latestLog.path, 'utf8');
  const lines = content.split('\n').filter((l) => l.trim());

  // Take last N lines
  const recentLines = lines.slice(-limit);

  // Parse log lines (simple format)
  return recentLines.map((line, idx) => {
    const match = line.match(/^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+): (.*)$/);

    if (match) {
      return {
        timestamp: match[1],
        level: match[2].toLowerCase() as LogEntry['level'],
        message: match[3],
        source: latestLog.name,
      };
    }

    return {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: line,
      source: latestLog.name,
    };
  });
}

/**
 * Check if a repository path exists and is valid
 */
export function isRepoValid(repoConfig: RepoConfig): boolean {
  return existsSync(repoConfig.path) && existsSync(join(repoConfig.path, '.git'));
}
