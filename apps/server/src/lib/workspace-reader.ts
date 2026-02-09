/**
 * Workspace Markdown Reader
 *
 * Reads and parses markdown files from the shared workspace directory.
 * Handles inbox, priorities, tasks, check-ins, memory, and follow-ups.
 *
 * Design principles:
 * - Tolerant parsing: handles format variations gracefully
 * - Empty-safe: returns empty arrays/objects for missing files
 * - iCloud-aware: handles .icloud placeholder files
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join, basename, extname } from 'path';
import { createHash } from 'crypto';
import type {
  InboxItem,
  Priority,
  WorkspaceTask,
  CheckIn,
  MemoryEntry,
  FollowUp,
  WorkspaceOverview,
} from '../types/index.js';

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Generate a stable ID from text content
 */
function hashId(text: string): string {
  return createHash('md5').update(text.trim()).digest('hex').slice(0, 8);
}

/**
 * Safely read a file, returning empty string if missing or iCloud placeholder
 */
function safeReadFile(filePath: string): string {
  if (!existsSync(filePath)) return '';

  // iCloud placeholder files start with a dot and end with .icloud
  const name = basename(filePath);
  if (name.startsWith('.') && name.endsWith('.icloud')) return '';

  try {
    return readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

/**
 * Extract #tags from text
 */
function extractTags(text: string): string[] {
  const matches = text.match(/#[\w-]+/g);
  return matches ? matches.map((t) => t.slice(1)) : [];
}

/**
 * Strip markdown bold markers from text
 */
function stripBold(text: string): string {
  return text.replace(/\*\*/g, '');
}

// ─── Inbox Parser ───────────────────────────────────────────────────────────

/**
 * Parse inbox.md into structured InboxItem[]
 *
 * Expected format:
 * ```
 * ## 2026-02-08
 * - [ ] Some task #tag
 * - [x] Done task → moved to priorities
 * ```
 */
export function readInbox(workspacePath: string): InboxItem[] {
  const content = safeReadFile(join(workspacePath, 'inbox.md'));
  if (!content) return [];

  const items: InboxItem[] = [];
  let currentDate: string | undefined;

  for (const line of content.split('\n')) {
    // Date header: ## 2026-02-08
    const dateMatch = line.match(/^##\s+(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
      currentDate = dateMatch[1];
      continue;
    }

    // Checkbox item: - [ ] text or - [x] text
    const checkboxMatch = line.match(/^[-*]\s+\[([ xX])\]\s+(.+)/);
    if (checkboxMatch) {
      const text = checkboxMatch[2].trim();
      const tags = extractTags(text);
      items.push({
        id: hashId(text),
        text: text.replace(/#[\w-]+/g, '').trim(),
        done: checkboxMatch[1].toLowerCase() === 'x',
        date: currentDate,
        tags: tags.length > 0 ? tags : undefined,
      });
    }
  }

  return items;
}

// ─── Priorities Parser ──────────────────────────────────────────────────────

/**
 * Parse priorities.md into structured Priority[]
 *
 * Expected format:
 * ```
 * ## High Priority
 * 1. **Title** — Description
 *
 * ## Medium Priority
 * 1. Description without bold
 * ```
 */
export function readPrioritiesFromWorkspace(workspacePath: string): Priority[] {
  const content = safeReadFile(join(workspacePath, 'priorities.md'));
  if (!content) return [];

  const priorities: Priority[] = [];
  let currentPriority: 'high' | 'medium' | 'low' = 'medium';
  let id = 1;
  let inParkingLot = false;

  for (const line of content.split('\n')) {
    // Priority section headers
    if (/^##\s+high\s+priority/i.test(line)) {
      currentPriority = 'high';
      inParkingLot = false;
      continue;
    }
    if (/^##\s+medium\s+priority/i.test(line)) {
      currentPriority = 'medium';
      inParkingLot = false;
      continue;
    }
    if (/^##\s+low\s+priority/i.test(line)) {
      currentPriority = 'low';
      inParkingLot = false;
      continue;
    }
    if (/^##\s+parking\s+lot/i.test(line)) {
      inParkingLot = true;
      continue;
    }
    // Skip any other ## header
    if (/^##\s/.test(line)) {
      continue;
    }

    if (inParkingLot) continue;

    // Numbered list item: 1. **Title** — Description OR 1. Description
    const numberedMatch = line.match(/^\d+\.\s+(.+)/);
    if (numberedMatch) {
      const fullText = numberedMatch[1].trim();

      // Try to extract bold title and description: **Title** — Description
      const boldMatch = fullText.match(/^\*\*(.+?)\*\*\s*[—–-]?\s*(.*)/);

      let title: string;
      let description: string;

      if (boldMatch) {
        title = boldMatch[1].trim();
        description = boldMatch[2].trim();
      } else {
        title = stripBold(fullText);
        description = '';
      }

      priorities.push({
        id: id++,
        title,
        description,
        status: 'pending',
        priority: currentPriority,
      });
    }
  }

  return priorities;
}

// ─── Tasks Parser ───────────────────────────────────────────────────────────

/**
 * Parse tasks.md into structured WorkspaceTask[]
 *
 * Expected format:
 * ```
 * ## In Progress
 * ### Task Title
 * - **Status:** In Progress
 * - **Priority:** High
 * - **Branch:** feature/something
 *
 * Free-form notes here.
 *
 * ## Pending
 * ### Another Task
 * ...
 * ```
 */
export function readTasks(workspacePath: string): WorkspaceTask[] {
  const content = safeReadFile(join(workspacePath, 'tasks.md'));
  if (!content) return [];

  const tasks: WorkspaceTask[] = [];
  let currentSection: 'in-progress' | 'pending' | 'done' | 'blocked' | null = null;
  let currentTask: Partial<WorkspaceTask> | null = null;
  let notesLines: string[] = [];

  const flushTask = () => {
    if (currentTask?.title) {
      const notes = notesLines.filter((l) => l.trim()).join('\n').trim();
      tasks.push({
        id: hashId(currentTask.title),
        title: currentTask.title,
        status: currentTask.status || currentSection || 'pending',
        priority: currentTask.priority,
        branch: currentTask.branch,
        agent: currentTask.agent,
        startedAt: currentTask.startedAt,
        completedAt: currentTask.completedAt,
        pr: currentTask.pr,
        notes: notes || undefined,
      } as WorkspaceTask);
    }
    currentTask = null;
    notesLines = [];
  };

  for (const line of content.split('\n')) {
    // Section headers: ## In Progress, ## Pending, ## Done, ## Blocked
    if (/^##\s+in\s+progress/i.test(line)) {
      flushTask();
      currentSection = 'in-progress';
      continue;
    }
    if (/^##\s+pending/i.test(line)) {
      flushTask();
      currentSection = 'pending';
      continue;
    }
    if (/^##\s+done/i.test(line)) {
      flushTask();
      currentSection = 'done';
      continue;
    }
    if (/^##\s+blocked/i.test(line)) {
      flushTask();
      currentSection = 'blocked';
      continue;
    }

    // Task title: ### Task Name
    const titleMatch = line.match(/^###\s+(.+)/);
    if (titleMatch) {
      flushTask();
      currentTask = { title: titleMatch[1].trim() };
      continue;
    }

    // Metadata: - **Key:** Value
    if (currentTask) {
      const metaMatch = line.match(/^[-*]\s+\*\*(\w[\w\s]*?):\*\*\s*(.*)/);
      if (metaMatch) {
        const key = metaMatch[1].trim().toLowerCase();
        const value = metaMatch[2].trim();

        switch (key) {
          case 'status':
            currentTask.status = value.toLowerCase().replace(/\s+/g, '-') as WorkspaceTask['status'];
            break;
          case 'priority':
            currentTask.priority = value.toLowerCase() as WorkspaceTask['priority'];
            break;
          case 'branch':
            currentTask.branch = value;
            break;
          case 'agent':
            currentTask.agent = value;
            break;
          case 'started':
            currentTask.startedAt = value;
            break;
          case 'completed':
            currentTask.completedAt = value;
            break;
          case 'pr':
            currentTask.pr = value;
            break;
        }
        continue;
      }

      // Collect free-form notes (non-metadata lines under a task)
      if (line.trim() && !line.startsWith('#') && !line.startsWith('<!--')) {
        notesLines.push(line);
      }
    }
  }

  // Flush the last task
  flushTask();

  return tasks;
}

// ─── Check-ins Parser ───────────────────────────────────────────────────────

/**
 * Parse a single check-in markdown file into sections
 */
function parseCheckInContent(content: string): Record<string, string> {
  const sections: Record<string, string> = {};
  let currentSection: string | null = null;
  let sectionLines: string[] = [];

  const flushSection = () => {
    if (currentSection) {
      sections[currentSection] = sectionLines.join('\n').trim();
    }
    sectionLines = [];
  };

  for (const line of content.split('\n')) {
    // Section header: ## Section Name
    const sectionMatch = line.match(/^##\s+(.+)/);
    if (sectionMatch) {
      flushSection();
      currentSection = sectionMatch[1].trim().toLowerCase();
      continue;
    }

    // Separator line — marks agent section boundary
    if (line.trim() === '---') {
      flushSection();
      currentSection = null;
      continue;
    }

    if (currentSection) {
      sectionLines.push(line);
    }
  }
  flushSection();

  return sections;
}

/**
 * List and read check-in files of a given type (daily, weekly, monthly)
 */
export function readCheckIns(
  workspacePath: string,
  type: 'daily' | 'weekly' | 'monthly'
): CheckIn[] {
  const dir = join(workspacePath, 'check-ins', type);
  if (!existsSync(dir)) return [];

  try {
    const files = readdirSync(dir)
      .filter((f) => f.endsWith('.md') && !f.startsWith('.'))
      .sort()
      .reverse(); // Most recent first

    return files.map((filename) => {
      const filePath = join(dir, filename);
      const content = safeReadFile(filePath);
      const date = basename(filename, '.md');

      return {
        date,
        type,
        filename,
        content,
        sections: parseCheckInContent(content),
      };
    });
  } catch {
    return [];
  }
}

/**
 * Read a specific check-in by date
 */
export function readCheckIn(
  workspacePath: string,
  type: 'daily' | 'weekly' | 'monthly',
  date: string
): CheckIn | null {
  const filename = `${date}.md`;
  const filePath = join(workspacePath, 'check-ins', type, filename);
  const content = safeReadFile(filePath);

  if (!content) return null;

  return {
    date,
    type,
    filename,
    content,
    sections: parseCheckInContent(content),
  };
}

// ─── Memory Parser ──────────────────────────────────────────────────────────

/**
 * Read all memory files (decisions.md, learnings.md, context.md, etc.)
 */
export function readMemory(workspacePath: string): MemoryEntry[] {
  const memDir = join(workspacePath, 'memory');
  if (!existsSync(memDir)) return [];

  try {
    const files = readdirSync(memDir)
      .filter((f) => f.endsWith('.md') && !f.startsWith('.'));

    return files.map((filename) => {
      const filePath = join(memDir, filename);
      const content = safeReadFile(filePath);
      const stats = statSync(filePath);

      // Extract title from first # heading
      const titleMatch = content.match(/^#\s+(.+)/m);
      const title = titleMatch ? titleMatch[1].trim() : basename(filename, '.md');

      return {
        filename,
        title,
        content,
        lastModified: stats.mtime.toISOString(),
      };
    });
  } catch {
    return [];
  }
}

/**
 * Read a specific memory file by name (without .md extension)
 */
export function readMemoryEntry(workspacePath: string, name: string): MemoryEntry | null {
  const filename = name.endsWith('.md') ? name : `${name}.md`;
  const filePath = join(workspacePath, 'memory', filename);
  const content = safeReadFile(filePath);

  if (!content) return null;

  const stats = statSync(filePath);
  const titleMatch = content.match(/^#\s+(.+)/m);
  const title = titleMatch ? titleMatch[1].trim() : basename(filename, '.md');

  return {
    filename,
    title,
    content,
    lastModified: stats.mtime.toISOString(),
  };
}

// ─── Follow-ups Parser ──────────────────────────────────────────────────────

/**
 * Parse follow-ups.md into structured FollowUp[]
 *
 * Expected format:
 * ```
 * - [ ] Review auth flow (due: 2026-02-15) #security
 * - [x] Check scheduler alternatives
 * ```
 */
export function readFollowUps(workspacePath: string): FollowUp[] {
  const content = safeReadFile(join(workspacePath, 'follow-ups.md'));
  if (!content) return [];

  const followUps: FollowUp[] = [];

  for (const line of content.split('\n')) {
    const checkboxMatch = line.match(/^[-*]\s+\[([ xX])\]\s+(.+)/);
    if (checkboxMatch) {
      let text = checkboxMatch[2].trim();
      const done = checkboxMatch[1].toLowerCase() === 'x';

      // Extract due date: (due: 2026-02-15)
      let dueDate: string | undefined;
      const dueMatch = text.match(/\(due:\s*(\d{4}-\d{2}-\d{2})\)/);
      if (dueMatch) {
        dueDate = dueMatch[1];
        text = text.replace(dueMatch[0], '').trim();
      }

      const tags = extractTags(text);
      text = text.replace(/#[\w-]+/g, '').trim();

      followUps.push({
        id: hashId(text),
        text,
        done,
        dueDate,
        tags: tags.length > 0 ? tags : undefined,
      });
    }
  }

  return followUps;
}

// ─── Agent Reports ──────────────────────────────────────────────────────────

/**
 * Read the latest agent report
 */
export function readLatestAgentReport(workspacePath: string): string | undefined {
  const filePath = join(workspacePath, 'agent-reports', 'latest-session.md');
  const content = safeReadFile(filePath);
  return content || undefined;
}

// ─── Workspace Overview ─────────────────────────────────────────────────────

/**
 * Get a combined overview of the entire workspace
 */
export function readWorkspaceOverview(workspacePath: string): WorkspaceOverview {
  const inbox = readInbox(workspacePath);
  const priorities = readPrioritiesFromWorkspace(workspacePath);
  const tasks = readTasks(workspacePath);
  const followUps = readFollowUps(workspacePath);
  const dailyCheckIns = readCheckIns(workspacePath, 'daily');
  const agentReport = readLatestAgentReport(workspacePath);

  return {
    inbox: {
      total: inbox.length,
      pending: inbox.filter((i) => !i.done).length,
      items: inbox,
    },
    priorities,
    tasks: {
      inProgress: tasks.filter((t) => t.status === 'in-progress'),
      pending: tasks.filter((t) => t.status === 'pending'),
      done: tasks.filter((t) => t.status === 'done'),
    },
    latestCheckIn: dailyCheckIns[0] || undefined,
    followUps: {
      total: followUps.length,
      pending: followUps.filter((f) => !f.done).length,
      items: followUps,
    },
    agentReport,
  };
}

// ─── Workspace Validation ───────────────────────────────────────────────────

/**
 * Check if a workspace path exists and has the expected structure
 */
export function isWorkspaceValid(workspacePath: string): boolean {
  if (!existsSync(workspacePath)) return false;

  // Check for at least one of the core files
  const coreFiles = ['inbox.md', 'priorities.md', 'tasks.md'];
  return coreFiles.some((f) => existsSync(join(workspacePath, f)));
}
