/**
 * Workspace Markdown Writer
 *
 * Writes to markdown files in the shared workspace directory.
 * All writes are atomic (temp file + rename) to prevent corruption.
 *
 * Design principles:
 * - Atomic writes: temp file + rename prevents partial writes
 * - Append-safe: never overwrites human content
 * - Agent sections: clearly marked with --- separator
 * - Idempotent: safe to call multiple times
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync } from 'fs';
import { join, dirname } from 'path';
import { randomBytes } from 'crypto';
import type { Priority } from '../types/index.js';

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Atomically write a file using temp file + rename
 */
function atomicWrite(filePath: string, content: string): void {
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  const tmpPath = `${filePath}.${randomBytes(4).toString('hex')}.tmp`;

  try {
    writeFileSync(tmpPath, content, 'utf8');
    renameSync(tmpPath, filePath);
  } catch (error) {
    // Clean up temp file on failure
    try {
      if (existsSync(tmpPath)) {
        writeFileSync(tmpPath, ''); // Truncate
        renameSync(tmpPath, `${tmpPath}.failed`);
      }
    } catch {
      // Ignore cleanup errors
    }
    throw error;
  }
}

/**
 * Read a file or return empty string
 */
function safeRead(filePath: string): string {
  if (!existsSync(filePath)) return '';
  try {
    return readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

/**
 * Get today's date as YYYY-MM-DD
 */
function today(): string {
  return new Date().toISOString().split('T')[0];
}

/**
 * Get current time as HH:MM
 */
function nowTime(): string {
  return new Date().toTimeString().slice(0, 5);
}

// ─── Inbox Writer ───────────────────────────────────────────────────────────

/**
 * Append an item to inbox.md under today's date header
 *
 * Creates the date header if it doesn't exist.
 * Adds `- [ ] text` under the header.
 */
export function appendToInbox(workspacePath: string, text: string): void {
  const filePath = join(workspacePath, 'inbox.md');
  let content = safeRead(filePath);

  const dateHeader = `## ${today()}`;

  if (content.includes(dateHeader)) {
    // Add item after the date header
    const headerIndex = content.indexOf(dateHeader);
    const afterHeader = headerIndex + dateHeader.length;
    // Find the end of the header line
    const lineEnd = content.indexOf('\n', afterHeader);
    const insertAt = lineEnd === -1 ? content.length : lineEnd + 1;

    content =
      content.slice(0, insertAt) +
      `- [ ] ${text}\n` +
      content.slice(insertAt);
  } else {
    // Insert new date header after the file header (first blank line after # heading)
    const lines = content.split('\n');
    let insertIndex = 0;

    // Skip the title and description lines
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('## ')) {
        insertIndex = i;
        break;
      }
      if (i === lines.length - 1) {
        insertIndex = lines.length;
      }
    }

    // If no ## headers found, insert after last non-empty line of header section
    if (insertIndex === 0) {
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() === '' && i > 0) {
          insertIndex = i + 1;
          break;
        }
      }
      if (insertIndex === 0) insertIndex = lines.length;
    }

    lines.splice(insertIndex, 0, `${dateHeader}\n- [ ] ${text}`);
    content = lines.join('\n');
  }

  atomicWrite(filePath, content);
}

// ─── Follow-ups Writer ──────────────────────────────────────────────────────

/**
 * Append an item to follow-ups.md
 *
 * Optionally include a due date: appendToFollowUps(path, "text", "2026-02-15")
 */
export function appendToFollowUps(
  workspacePath: string,
  text: string,
  dueDate?: string
): void {
  const filePath = join(workspacePath, 'follow-ups.md');
  let content = safeRead(filePath);

  let item = `- [ ] ${text}`;
  if (dueDate) {
    item += ` (due: ${dueDate})`;
  }

  // Append at the end, ensuring a trailing newline
  if (content && !content.endsWith('\n')) {
    content += '\n';
  }
  content += item + '\n';

  atomicWrite(filePath, content);
}

// ─── Tasks Writer ───────────────────────────────────────────────────────────

/**
 * Update the status of a task in tasks.md
 *
 * Finds the task by title (case-insensitive) and updates its **Status:** field.
 * Also moves the task section to the appropriate status heading if needed.
 */
export function updateTaskStatus(
  workspacePath: string,
  taskTitle: string,
  newStatus: 'pending' | 'in-progress' | 'done' | 'blocked',
  extraFields?: Record<string, string>
): boolean {
  const filePath = join(workspacePath, 'tasks.md');
  let content = safeRead(filePath);
  if (!content) return false;

  const lines = content.split('\n');
  let taskStartLine = -1;
  let taskEndLine = -1;

  // Find the task by title (### Task Title)
  for (let i = 0; i < lines.length; i++) {
    const titleMatch = lines[i].match(/^###\s+(.+)/);
    if (titleMatch && titleMatch[1].trim().toLowerCase() === taskTitle.toLowerCase()) {
      taskStartLine = i;

      // Find the end of this task (next ### or ## or end of file)
      for (let j = i + 1; j < lines.length; j++) {
        if (/^#{2,3}\s/.test(lines[j])) {
          taskEndLine = j;
          break;
        }
      }
      if (taskEndLine === -1) taskEndLine = lines.length;
      break;
    }
  }

  if (taskStartLine === -1) return false;

  // Extract the task section
  const taskLines = lines.slice(taskStartLine, taskEndLine);

  // Update or add the Status field
  let statusUpdated = false;
  const statusDisplayMap: Record<string, string> = {
    'pending': 'Pending',
    'in-progress': 'In Progress',
    'done': 'Done',
    'blocked': 'Blocked',
  };

  for (let i = 0; i < taskLines.length; i++) {
    if (/^[-*]\s+\*\*Status:\*\*/.test(taskLines[i])) {
      taskLines[i] = `- **Status:** ${statusDisplayMap[newStatus]}`;
      statusUpdated = true;
      break;
    }
  }

  if (!statusUpdated) {
    // Insert Status after the title line
    taskLines.splice(1, 0, `- **Status:** ${statusDisplayMap[newStatus]}`);
  }

  // Add extra fields (e.g., Completed date, PR number)
  if (extraFields) {
    for (const [key, value] of Object.entries(extraFields)) {
      const fieldRegex = new RegExp(`^[-*]\\s+\\*\\*${key}:\\*\\*`, 'i');
      let fieldFound = false;

      for (let i = 0; i < taskLines.length; i++) {
        if (fieldRegex.test(taskLines[i])) {
          taskLines[i] = `- **${key}:** ${value}`;
          fieldFound = true;
          break;
        }
      }

      if (!fieldFound) {
        // Find last metadata line to insert after
        let lastMetaLine = 0;
        for (let i = 1; i < taskLines.length; i++) {
          if (/^[-*]\s+\*\*\w/.test(taskLines[i])) {
            lastMetaLine = i;
          }
        }
        taskLines.splice(lastMetaLine + 1, 0, `- **${key}:** ${value}`);
      }
    }
  }

  // Remove the old task section and determine where to insert in new section
  lines.splice(taskStartLine, taskEndLine - taskStartLine);

  // Find the target section header
  const sectionHeaderMap: Record<string, RegExp> = {
    'in-progress': /^##\s+in\s+progress/i,
    'pending': /^##\s+pending/i,
    'done': /^##\s+done/i,
    'blocked': /^##\s+blocked/i,
  };

  const targetRegex = sectionHeaderMap[newStatus];
  let targetInsertLine = -1;

  for (let i = 0; i < lines.length; i++) {
    if (targetRegex.test(lines[i])) {
      // Insert after the section header (and any blank line / comment after it)
      let insertAfter = i + 1;
      while (
        insertAfter < lines.length &&
        (lines[insertAfter].trim() === '' || lines[insertAfter].startsWith('<!--'))
      ) {
        insertAfter++;
      }
      targetInsertLine = insertAfter;
      break;
    }
  }

  if (targetInsertLine === -1) {
    // Section doesn't exist — append at end
    targetInsertLine = lines.length;
    lines.push('', `## ${statusDisplayMap[newStatus]}`, '');
    targetInsertLine = lines.length;
  }

  // Insert the task at the target location
  lines.splice(targetInsertLine, 0, ...taskLines, '');

  atomicWrite(filePath, lines.join('\n'));
  return true;
}

/**
 * Add a new task to tasks.md under the Pending section
 */
export function addTask(
  workspacePath: string,
  title: string,
  priority?: 'high' | 'medium' | 'low',
  notes?: string
): void {
  const filePath = join(workspacePath, 'tasks.md');
  let content = safeRead(filePath);

  const taskBlock = [
    `### ${title}`,
    `- **Status:** Pending`,
  ];

  if (priority) {
    const displayPriority = priority.charAt(0).toUpperCase() + priority.slice(1);
    taskBlock.push(`- **Priority:** ${displayPriority}`);
  }

  if (notes) {
    taskBlock.push('', notes);
  }

  taskBlock.push('');

  // Find the Pending section and insert after it
  const lines = content.split('\n');
  let insertLine = -1;

  for (let i = 0; i < lines.length; i++) {
    if (/^##\s+pending/i.test(lines[i])) {
      let insertAfter = i + 1;
      while (
        insertAfter < lines.length &&
        (lines[insertAfter].trim() === '' || lines[insertAfter].startsWith('<!--'))
      ) {
        insertAfter++;
      }
      insertLine = insertAfter;
      break;
    }
  }

  if (insertLine === -1) {
    // No Pending section — add it
    lines.push('', '## Pending', '', ...taskBlock);
  } else {
    lines.splice(insertLine, 0, ...taskBlock);
  }

  atomicWrite(filePath, lines.join('\n'));
}

// ─── Check-in Writer ────────────────────────────────────────────────────────

/**
 * Create a new check-in file from template
 *
 * Returns the path to the created file, or null if it already exists.
 */
export function createCheckIn(
  workspacePath: string,
  type: 'daily' | 'weekly' | 'monthly',
  templateDir: string,
  agentData?: string
): string | null {
  const now = new Date();
  let filename: string;
  let displayDate: string;
  let templateFile: string;

  switch (type) {
    case 'daily':
      filename = now.toISOString().split('T')[0] + '.md';
      displayDate = now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
      templateFile = 'daily-checkin.md';
      break;
    case 'weekly': {
      // ISO week number
      const d = new Date(now);
      d.setHours(0, 0, 0, 0);
      d.setDate(d.getDate() + 3 - ((d.getDay() + 6) % 7));
      const week = Math.ceil(
        ((d.getTime() - new Date(d.getFullYear(), 0, 4).getTime()) / 86400000 + 1) / 7
      );
      const weekStr = String(week).padStart(2, '0');
      filename = `${now.getFullYear()}-W${weekStr}.md`;

      const weekStart = new Date(now);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      displayDate = `Week ${week}, ${now.getFullYear()} (${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}-${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})`;
      templateFile = 'weekly-checkin.md';
      break;
    }
    case 'monthly':
      filename = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}.md`;
      displayDate = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
      });
      templateFile = 'monthly-checkin.md';
      break;
  }

  const filePath = join(workspacePath, 'check-ins', type, filename);

  // Don't overwrite existing check-ins
  if (existsSync(filePath)) return null;

  // Read template
  const templatePath = join(templateDir, templateFile);
  let content = safeRead(templatePath);

  if (!content) {
    // Fallback: generate minimal template
    content = `# ${type.charAt(0).toUpperCase() + type.slice(1)} Check-in — ${displayDate}\n\n## Notes\n- \n`;
  }

  // Replace placeholders
  content = content.replace('__DATE_DISPLAY__', displayDate);
  content = content.replace('__WEEK_DISPLAY__', displayDate);
  content = content.replace('__MONTH_DISPLAY__', displayDate);

  // Append agent data if provided
  if (agentData) {
    content += agentData + '\n';
  }

  // Ensure directory exists
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  atomicWrite(filePath, content);
  return filePath;
}

/**
 * Append agent activity to today's daily check-in
 *
 * Writes to the "Agent Activity" section (after the --- separator).
 * Creates the check-in file if it doesn't exist.
 */
export function appendAgentActivity(
  workspacePath: string,
  activity: string,
  templateDir: string
): void {
  const todayDate = today();
  const filePath = join(workspacePath, 'check-ins', 'daily', `${todayDate}.md`);

  if (!existsSync(filePath)) {
    // Create today's check-in first
    createCheckIn(workspacePath, 'daily', templateDir);
  }

  let content = safeRead(filePath);
  if (!content) return;

  const timestamp = nowTime();
  const activityLine = `- **${timestamp}** ${activity}`;

  // Append to the end (agent activity section is at the bottom)
  if (!content.endsWith('\n')) {
    content += '\n';
  }
  content += activityLine + '\n';

  atomicWrite(filePath, content);
}

// ─── Agent Report Writer ────────────────────────────────────────────────────

/**
 * Write a session summary to agent-reports/latest-session.md
 *
 * Also writes to agent-reports/session-{timestamp}.md for history.
 */
export function writeAgentReport(
  workspacePath: string,
  summary: string
): void {
  const reportsDir = join(workspacePath, 'agent-reports');
  if (!existsSync(reportsDir)) {
    mkdirSync(reportsDir, { recursive: true });
  }

  // Write latest
  atomicWrite(join(reportsDir, 'latest-session.md'), summary);

  // Write timestamped copy
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  atomicWrite(join(reportsDir, `session-${timestamp}.md`), summary);
}

// ─── Priorities Writer ──────────────────────────────────────────────────────

/**
 * Rewrite priorities.md with updated priority order
 *
 * Takes arrays for each priority level and rewrites the file.
 * Preserves the Parking Lot section.
 */
export function updatePriorities(
  workspacePath: string,
  high: Array<{ title: string; description?: string }>,
  medium: Array<{ title: string; description?: string }>,
  low: Array<{ title: string; description?: string }>,
  parkingLot?: string[]
): void {
  const filePath = join(workspacePath, 'priorities.md');

  // Preserve the existing parking lot if not provided
  if (!parkingLot) {
    const existingContent = safeRead(filePath);
    const parkingMatch = existingContent.match(/## Parking Lot\n([\s\S]*?)(?=\n## |$)/);
    if (parkingMatch) {
      parkingLot = parkingMatch[1]
        .split('\n')
        .filter((l) => l.match(/^[-*]\s+/))
        .map((l) => l.replace(/^[-*]\s+/, '').trim());
    }
  }

  const formatItem = (item: { title: string; description?: string }, idx: number): string => {
    if (item.description) {
      return `${idx + 1}. **${item.title}** — ${item.description}`;
    }
    return `${idx + 1}. **${item.title}**`;
  };

  let content = `# Current Priorities

The agent picks Priority #1 each night for implementation.
Edit this file to change what gets built next.

## High Priority

${high.map((item, i) => formatItem(item, i)).join('\n') || '_No high priority items_'}

## Medium Priority

${medium.map((item, i) => formatItem(item, i)).join('\n') || '_No medium priority items_'}

## Low Priority

${low.map((item, i) => formatItem(item, i)).join('\n') || '_No low priority items_'}
`;

  if (parkingLot && parkingLot.length > 0) {
    content += `\n## Parking Lot\n\n${parkingLot.map((item) => `- ${item}`).join('\n')}\n`;
  }

  atomicWrite(filePath, content);
}

// ─── Memory Writer ──────────────────────────────────────────────────────────

/**
 * Append a learning entry to memory/learnings.md
 */
export function appendLearning(workspacePath: string, learning: string): void {
  const filePath = join(workspacePath, 'memory', 'learnings.md');
  let content = safeRead(filePath);

  const entry = `\n## ${today()}\n\n${learning}\n`;

  if (!content.endsWith('\n')) {
    content += '\n';
  }
  content += entry;

  atomicWrite(filePath, content);
}

/**
 * Append a decision to memory/decisions.md
 */
export function appendDecision(
  workspacePath: string,
  title: string,
  context: string,
  decision: string,
  consequences: string
): void {
  const filePath = join(workspacePath, 'memory', 'decisions.md');
  let content = safeRead(filePath);

  const entry = `\n## ${today()}: ${title}

**Context:** ${context}
**Decision:** ${decision}
**Consequences:** ${consequences}
`;

  if (!content.endsWith('\n')) {
    content += '\n';
  }
  content += entry;

  atomicWrite(filePath, content);
}
