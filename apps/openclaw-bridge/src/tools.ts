/**
 * MCP Tool Definitions
 *
 * Registers all workspace tools with the MCP server.
 * Each tool reads from or writes to the shared markdown workspace.
 *
 * Tools are designed for natural language interaction via OpenClaw:
 * - Input: simple strings/enums (easy for AI to generate)
 * - Output: formatted text (easy for AI to display in Telegram/WhatsApp)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, basename } from 'path';
import { createHash } from 'crypto';
import { getTemplatesDir } from './workspace-bridge.js';

// ─── Shared Helpers (inline to avoid cross-package deps) ─────────────────────

function safeReadFile(filePath: string): string {
  if (!existsSync(filePath)) return '';
  const name = basename(filePath);
  if (name.startsWith('.') && name.endsWith('.icloud')) return '';
  try {
    return readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

function hashId(text: string): string {
  return createHash('md5').update(text.trim()).digest('hex').slice(0, 8);
}

function today(): string {
  return new Date().toISOString().split('T')[0];
}

function nowTime(): string {
  return new Date().toTimeString().slice(0, 5);
}

// ─── Inline parsers (lightweight versions for MCP bridge) ────────────────────

function parseInbox(content: string): Array<{ text: string; done: boolean; date?: string }> {
  const items: Array<{ text: string; done: boolean; date?: string }> = [];
  let currentDate: string | undefined;

  for (const line of content.split('\n')) {
    const dateMatch = line.match(/^##\s+(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) { currentDate = dateMatch[1]; continue; }

    const checkboxMatch = line.match(/^[-*]\s+\[([ xX])\]\s+(.+)/);
    if (checkboxMatch) {
      items.push({
        text: checkboxMatch[2].trim(),
        done: checkboxMatch[1].toLowerCase() === 'x',
        date: currentDate,
      });
    }
  }
  return items;
}

function parsePriorities(content: string): Array<{ title: string; description: string; level: string }> {
  const priorities: Array<{ title: string; description: string; level: string }> = [];
  let currentLevel = 'medium';

  for (const line of content.split('\n')) {
    if (/^##\s+high\s+priority/i.test(line)) { currentLevel = 'high'; continue; }
    if (/^##\s+medium\s+priority/i.test(line)) { currentLevel = 'medium'; continue; }
    if (/^##\s+low\s+priority/i.test(line)) { currentLevel = 'low'; continue; }
    if (/^##\s+parking\s+lot/i.test(line)) break;

    const numberedMatch = line.match(/^\d+\.\s+(.+)/);
    if (numberedMatch) {
      const fullText = numberedMatch[1].trim();
      const boldMatch = fullText.match(/^\*\*(.+?)\*\*\s*[—–-]?\s*(.*)/);
      if (boldMatch) {
        priorities.push({ title: boldMatch[1].trim(), description: boldMatch[2].trim(), level: currentLevel });
      } else {
        priorities.push({ title: fullText.replace(/\*\*/g, ''), description: '', level: currentLevel });
      }
    }
  }
  return priorities;
}

function parseTasks(content: string): Array<{ title: string; status: string; priority?: string; branch?: string; agent?: string; pr?: string }> {
  const tasks: Array<{ title: string; status: string; priority?: string; branch?: string; agent?: string; pr?: string }> = [];
  let currentSection = '';
  let currentTask: any = null;

  const flushTask = () => {
    if (currentTask?.title) {
      tasks.push({ ...currentTask, status: currentTask.status || currentSection });
      currentTask = null;
    }
  };

  for (const line of content.split('\n')) {
    if (/^##\s+in\s+progress/i.test(line)) { flushTask(); currentSection = 'in-progress'; continue; }
    if (/^##\s+pending/i.test(line)) { flushTask(); currentSection = 'pending'; continue; }
    if (/^##\s+done/i.test(line)) { flushTask(); currentSection = 'done'; continue; }
    if (/^##\s+blocked/i.test(line)) { flushTask(); currentSection = 'blocked'; continue; }

    const titleMatch = line.match(/^###\s+(.+)/);
    if (titleMatch) { flushTask(); currentTask = { title: titleMatch[1].trim() }; continue; }

    if (currentTask) {
      const metaMatch = line.match(/^[-*]\s+\*\*(\w[\w\s]*?):\*\*\s*(.*)/);
      if (metaMatch) {
        const key = metaMatch[1].trim().toLowerCase();
        const value = metaMatch[2].trim();
        if (key === 'status') currentTask.status = value.toLowerCase().replace(/\s+/g, '-');
        else if (key === 'priority') currentTask.priority = value.toLowerCase();
        else if (key === 'branch') currentTask.branch = value;
        else if (key === 'agent') currentTask.agent = value;
        else if (key === 'pr') currentTask.pr = value;
      }
    }
  }
  flushTask();
  return tasks;
}

function parseFollowUps(content: string): Array<{ text: string; done: boolean; dueDate?: string }> {
  const followUps: Array<{ text: string; done: boolean; dueDate?: string }> = [];

  for (const line of content.split('\n')) {
    const checkboxMatch = line.match(/^[-*]\s+\[([ xX])\]\s+(.+)/);
    if (checkboxMatch) {
      let text = checkboxMatch[2].trim();
      const done = checkboxMatch[1].toLowerCase() === 'x';
      let dueDate: string | undefined;
      const dueMatch = text.match(/\(due:\s*(\d{4}-\d{2}-\d{2})\)/);
      if (dueMatch) { dueDate = dueMatch[1]; text = text.replace(dueMatch[0], '').trim(); }
      followUps.push({ text, done, dueDate });
    }
  }
  return followUps;
}

// ─── Inline writers ──────────────────────────────────────────────────────────

import { writeFileSync, mkdirSync, renameSync } from 'fs';
import { dirname } from 'path';
import { randomBytes } from 'crypto';

function atomicWrite(filePath: string, content: string): void {
  const dir = dirname(filePath);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  const tmpPath = `${filePath}.${randomBytes(4).toString('hex')}.tmp`;
  try {
    writeFileSync(tmpPath, content, 'utf8');
    renameSync(tmpPath, filePath);
  } catch (error) {
    try { if (existsSync(tmpPath)) writeFileSync(tmpPath, ''); } catch { /* ignore */ }
    throw error;
  }
}

function appendInboxItem(workspacePath: string, text: string): void {
  const filePath = join(workspacePath, 'inbox.md');
  let content = safeReadFile(filePath);
  const dateHeader = `## ${today()}`;

  if (content.includes(dateHeader)) {
    const headerIndex = content.indexOf(dateHeader);
    const lineEnd = content.indexOf('\n', headerIndex + dateHeader.length);
    const insertAt = lineEnd === -1 ? content.length : lineEnd + 1;
    content = content.slice(0, insertAt) + `- [ ] ${text}\n` + content.slice(insertAt);
  } else {
    const lines = content.split('\n');
    let insertIndex = lines.length;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('## ')) { insertIndex = i; break; }
    }
    lines.splice(insertIndex, 0, `${dateHeader}\n- [ ] ${text}`);
    content = lines.join('\n');
  }
  atomicWrite(filePath, content);
}

function appendFollowUpItem(workspacePath: string, text: string, dueDate?: string): void {
  const filePath = join(workspacePath, 'follow-ups.md');
  let content = safeReadFile(filePath);
  let item = `- [ ] ${text}`;
  if (dueDate) item += ` (due: ${dueDate})`;
  if (content && !content.endsWith('\n')) content += '\n';
  content += item + '\n';
  atomicWrite(filePath, content);
}

// ─── Tool Registration ──────────────────────────────────────────────────────

/**
 * Register all workspace tools with the MCP server
 */
export function registerWorkspaceTools(server: McpServer, workspacePath: string): void {

  // ── get_overview ──────────────────────────────────────────────────────────

  server.tool(
    'get_overview',
    'Get a full overview of the workspace: inbox count, priorities, active tasks, follow-ups, and latest agent report.',
    {},
    async () => {
      const inbox = parseInbox(safeReadFile(join(workspacePath, 'inbox.md')));
      const priorities = parsePriorities(safeReadFile(join(workspacePath, 'priorities.md')));
      const tasks = parseTasks(safeReadFile(join(workspacePath, 'tasks.md')));
      const followUps = parseFollowUps(safeReadFile(join(workspacePath, 'follow-ups.md')));

      const pendingInbox = inbox.filter(i => !i.done);
      const highPriorities = priorities.filter(p => p.level === 'high');
      const activeTasks = tasks.filter(t => t.status === 'in-progress');
      const pendingFollowUps = followUps.filter(f => !f.done);

      // Latest agent report
      const reportPath = join(workspacePath, 'agent-reports', 'latest-session.md');
      const report = safeReadFile(reportPath);

      let text = `📊 **Workspace Overview**\n\n`;
      text += `📥 **Inbox:** ${pendingInbox.length} pending (${inbox.length} total)\n`;
      text += `🎯 **Priority #1:** ${highPriorities[0]?.title || 'None set'}\n`;
      text += `🔨 **Active tasks:** ${activeTasks.length}\n`;
      text += `📋 **Follow-ups:** ${pendingFollowUps.length} pending\n`;

      if (activeTasks.length > 0) {
        text += `\n**In Progress:**\n`;
        for (const task of activeTasks) {
          text += `• ${task.title}${task.branch ? ` (${task.branch})` : ''}${task.pr ? ` — PR: ${task.pr}` : ''}\n`;
        }
      }

      if (report) {
        text += `\n**Latest Agent Report:**\n${report.slice(0, 500)}`;
        if (report.length > 500) text += '\n...(truncated)';
      }

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_inbox ─────────────────────────────────────────────────────────────

  server.tool(
    'get_inbox',
    'Show all inbox items. Inbox is the quick-drop zone for ideas, tasks, and thoughts.',
    {},
    async () => {
      const items = parseInbox(safeReadFile(join(workspacePath, 'inbox.md')));
      if (items.length === 0) {
        return { content: [{ type: 'text' as const, text: '📥 Inbox is empty. Drop ideas here!' }] };
      }

      const pending = items.filter(i => !i.done);
      const done = items.filter(i => i.done);

      let text = `📥 **Inbox** (${pending.length} pending, ${done.length} done)\n\n`;
      for (const item of pending) {
        text += `• ${item.text}${item.date ? ` (${item.date})` : ''}\n`;
      }

      if (done.length > 0) {
        text += `\n✅ **Done:**\n`;
        for (const item of done.slice(0, 5)) {
          text += `• ~~${item.text}~~\n`;
        }
        if (done.length > 5) text += `• ...and ${done.length - 5} more\n`;
      }

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── add_to_inbox ──────────────────────────────────────────────────────────

  server.tool(
    'add_to_inbox',
    'Add an idea, task, or thought to the inbox. The item will appear under today\'s date.',
    { text: z.string().describe('The item to add to the inbox') },
    async ({ text }) => {
      appendInboxItem(workspacePath, text);
      return { content: [{ type: 'text' as const, text: `✅ Added to inbox: ${text}` }] };
    }
  );

  // ── get_priorities ────────────────────────────────────────────────────────

  server.tool(
    'get_priorities',
    'Show current priorities. The agent picks Priority #1 (High) each night for implementation.',
    {},
    async () => {
      const priorities = parsePriorities(safeReadFile(join(workspacePath, 'priorities.md')));
      if (priorities.length === 0) {
        return { content: [{ type: 'text' as const, text: '🎯 No priorities set. Edit priorities.md to add some!' }] };
      }

      let text = '🎯 **Current Priorities**\n\n';

      const high = priorities.filter(p => p.level === 'high');
      const medium = priorities.filter(p => p.level === 'medium');
      const low = priorities.filter(p => p.level === 'low');

      if (high.length > 0) {
        text += '**High:**\n';
        high.forEach((p, i) => {
          text += `${i + 1}. **${p.title}**${p.description ? ` — ${p.description}` : ''}\n`;
        });
        text += '\n';
      }

      if (medium.length > 0) {
        text += '**Medium:**\n';
        medium.forEach((p, i) => {
          text += `${i + 1}. ${p.title}${p.description ? ` — ${p.description}` : ''}\n`;
        });
        text += '\n';
      }

      if (low.length > 0) {
        text += '**Low:**\n';
        low.forEach((p, i) => {
          text += `${i + 1}. ${p.title}${p.description ? ` — ${p.description}` : ''}\n`;
        });
      }

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_tasks ─────────────────────────────────────────────────────────────

  server.tool(
    'get_tasks',
    'Show all tracked tasks with their status, priority, branch, and PR info.',
    {},
    async () => {
      const tasks = parseTasks(safeReadFile(join(workspacePath, 'tasks.md')));
      if (tasks.length === 0) {
        return { content: [{ type: 'text' as const, text: '📋 No tasks tracked yet.' }] };
      }

      let text = '📋 **Tasks**\n\n';

      const inProgress = tasks.filter(t => t.status === 'in-progress');
      const pending = tasks.filter(t => t.status === 'pending');
      const done = tasks.filter(t => t.status === 'done');
      const blocked = tasks.filter(t => t.status === 'blocked');

      if (inProgress.length > 0) {
        text += '🔨 **In Progress:**\n';
        for (const t of inProgress) {
          text += `• **${t.title}**`;
          if (t.branch) text += ` (${t.branch})`;
          if (t.pr) text += ` — PR: ${t.pr}`;
          if (t.agent) text += ` [${t.agent}]`;
          text += '\n';
        }
        text += '\n';
      }

      if (blocked.length > 0) {
        text += '🚫 **Blocked:**\n';
        for (const t of blocked) text += `• **${t.title}**\n`;
        text += '\n';
      }

      if (pending.length > 0) {
        text += '⏳ **Pending:**\n';
        for (const t of pending) text += `• ${t.title}\n`;
        text += '\n';
      }

      if (done.length > 0) {
        text += `✅ **Done:** ${done.length} task(s)\n`;
        for (const t of done.slice(0, 3)) text += `• ~~${t.title}~~${t.pr ? ` — PR: ${t.pr}` : ''}\n`;
        if (done.length > 3) text += `• ...and ${done.length - 3} more\n`;
      }

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_agent_status ──────────────────────────────────────────────────────

  server.tool(
    'get_agent_status',
    'Get the latest agent session activity. Shows what the agent did in its most recent run.',
    {},
    async () => {
      const reportPath = join(workspacePath, 'agent-reports', 'latest-session.md');
      const report = safeReadFile(reportPath);

      if (!report) {
        return { content: [{ type: 'text' as const, text: '🤖 No agent reports yet. The agent writes here after each session.' }] };
      }

      return { content: [{ type: 'text' as const, text: `🤖 **Latest Agent Report**\n\n${report}` }] };
    }
  );

  // ── get_checkin ───────────────────────────────────────────────────────────

  server.tool(
    'get_checkin',
    'Get a check-in file. Defaults to today\'s daily check-in. Can specify type (daily/weekly/monthly) and date.',
    {
      type: z.enum(['daily', 'weekly', 'monthly']).default('daily').describe('Check-in type'),
      date: z.string().optional().describe('Date string (e.g., 2026-02-08 for daily, 2026-W06 for weekly, 2026-02 for monthly). Defaults to current period.'),
    },
    async ({ type, date }) => {
      let targetDate = date;
      if (!targetDate) {
        const now = new Date();
        switch (type) {
          case 'daily':
            targetDate = now.toISOString().split('T')[0];
            break;
          case 'weekly': {
            const d = new Date(now);
            d.setHours(0, 0, 0, 0);
            d.setDate(d.getDate() + 3 - ((d.getDay() + 6) % 7));
            const week = Math.ceil(((d.getTime() - new Date(d.getFullYear(), 0, 4).getTime()) / 86400000 + 1) / 7);
            targetDate = `${now.getFullYear()}-W${String(week).padStart(2, '0')}`;
            break;
          }
          case 'monthly':
            targetDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
            break;
        }
      }

      const filePath = join(workspacePath, 'check-ins', type, `${targetDate}.md`);
      const content = safeReadFile(filePath);

      if (!content) {
        return { content: [{ type: 'text' as const, text: `📝 No ${type} check-in found for ${targetDate}. Use create_checkin to create one.` }] };
      }

      return { content: [{ type: 'text' as const, text: `📝 **${type.charAt(0).toUpperCase() + type.slice(1)} Check-in — ${targetDate}**\n\n${content}` }] };
    }
  );

  // ── add_checkin_notes ─────────────────────────────────────────────────────

  server.tool(
    'add_checkin_notes',
    'Add the user\'s notes to today\'s daily check-in. Writes to the "What happened today" section.',
    {
      notes: z.string().describe('The notes to add to the check-in'),
      section: z.string().default('what happened today').describe('Which section to add to (e.g., "what happened today", "what\'s next", "blockers", "notes")'),
    },
    async ({ notes, section }) => {
      const filePath = join(workspacePath, 'check-ins', 'daily', `${today()}.md`);
      let content = safeReadFile(filePath);

      if (!content) {
        // Create today's check-in first
        const templateDir = getTemplatesDir();
        const templatePath = join(templateDir, 'daily-checkin.md');
        const template = safeReadFile(templatePath);

        if (template) {
          const displayDate = new Date().toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'short', day: 'numeric',
          });
          content = template.replace('__DATE_DISPLAY__', displayDate);
        } else {
          content = `# Daily Check-in — ${today()}\n\n## What happened today\n- \n\n## What's next\n- \n\n## Blockers\n- None\n\n## Notes\n- \n`;
        }
      }

      // Find the target section and append notes
      const sectionHeader = `## ${section}`;
      const sectionRegex = new RegExp(`^##\\s+${section.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'im');
      const lines = content.split('\n');
      let sectionLine = -1;

      for (let i = 0; i < lines.length; i++) {
        if (sectionRegex.test(lines[i])) {
          sectionLine = i;
          break;
        }
      }

      if (sectionLine !== -1) {
        // Find the first content line after the section header (skip blanks and existing dash)
        let insertLine = sectionLine + 1;
        // If next line is just "- " (empty bullet), replace it
        if (insertLine < lines.length && lines[insertLine].trim() === '-') {
          lines[insertLine] = `- ${notes}`;
        } else {
          lines.splice(insertLine, 0, `- ${notes}`);
        }
        content = lines.join('\n');
      } else {
        // Section not found — append at end before agent section
        const separatorIndex = content.lastIndexOf('---');
        if (separatorIndex !== -1) {
          content = content.slice(0, separatorIndex) + `\n## ${section}\n- ${notes}\n\n` + content.slice(separatorIndex);
        } else {
          content += `\n## ${section}\n- ${notes}\n`;
        }
      }

      atomicWrite(filePath, content);
      return { content: [{ type: 'text' as const, text: `✅ Added to today's check-in (${section})` }] };
    }
  );

  // ── get_follow_ups ────────────────────────────────────────────────────────

  server.tool(
    'get_follow_ups',
    'Show all follow-up items. These are things to revisit later.',
    {},
    async () => {
      const followUps = parseFollowUps(safeReadFile(join(workspacePath, 'follow-ups.md')));
      if (followUps.length === 0) {
        return { content: [{ type: 'text' as const, text: '📋 No follow-ups tracked.' }] };
      }

      const pending = followUps.filter(f => !f.done);
      const done = followUps.filter(f => f.done);

      let text = `📋 **Follow-ups** (${pending.length} pending)\n\n`;
      for (const f of pending) {
        text += `• ${f.text}${f.dueDate ? ` (due: ${f.dueDate})` : ''}\n`;
      }

      if (done.length > 0) {
        text += `\n✅ **Done:** ${done.length} item(s)\n`;
      }

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── add_follow_up ─────────────────────────────────────────────────────────

  server.tool(
    'add_follow_up',
    'Add a follow-up item. Something to revisit later, optionally with a due date.',
    {
      text: z.string().describe('The follow-up item'),
      due_date: z.string().optional().describe('Optional due date (YYYY-MM-DD format)'),
    },
    async ({ text, due_date }) => {
      appendFollowUpItem(workspacePath, text, due_date);
      let msg = `✅ Follow-up added: ${text}`;
      if (due_date) msg += ` (due: ${due_date})`;
      return { content: [{ type: 'text' as const, text: msg }] };
    }
  );

  // ── get_memory ────────────────────────────────────────────────────────────

  server.tool(
    'get_memory',
    'Read a memory file (decisions, learnings, or context). These contain persistent project knowledge.',
    {
      name: z.enum(['decisions', 'learnings', 'context']).describe('Which memory file to read'),
    },
    async ({ name }) => {
      const filePath = join(workspacePath, 'memory', `${name}.md`);
      const content = safeReadFile(filePath);

      if (!content) {
        return { content: [{ type: 'text' as const, text: `📚 Memory file "${name}" is empty.` }] };
      }

      return { content: [{ type: 'text' as const, text: `📚 **${name.charAt(0).toUpperCase() + name.slice(1)}**\n\n${content}` }] };
    }
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // DB-BACKED TOOLS (via Agent Service API)
  // These route through http://localhost:4010 to read structured data from SQLite
  // ═══════════════════════════════════════════════════════════════════════════

  const API_BASE = process.env.AGENT_API_URL || 'http://localhost:4010';

  async function apiGet<T>(path: string): Promise<T | null> {
    try {
      const res = await fetch(`${API_BASE}${path}`);
      const data = await res.json() as { success: boolean; data?: T };
      return data.success ? (data.data ?? null) : null;
    } catch {
      return null;
    }
  }

  async function apiPost(path: string, body: Record<string, unknown>): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json() as { success: boolean };
      return data.success;
    } catch {
      return false;
    }
  }

  // ── get_teams ────────────────────────────────────────────────────────────

  server.tool(
    'get_teams',
    'List all teams and their agent counts. Shows Engineering, Marketing, and Management teams.',
    {},
    async () => {
      const teams = await apiGet<Array<{ id: string; name: string; domain: string; description: string }>>('/api/teams');
      if (!teams || teams.length === 0) {
        return { content: [{ type: 'text' as const, text: '⚠️ Could not fetch teams. Is the API server running?' }] };
      }

      let text = '👥 **Teams**\n\n';
      for (const t of teams) {
        text += `• **${t.name}** (${t.domain}) — ${t.description || 'No description'}\n`;
      }
      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_agents ───────────────────────────────────────────────────────────

  server.tool(
    'get_agents',
    'List agents for a specific team. Shows name, role, LLM preference, and performance stats.',
    {
      team_id: z.string().describe('Team ID (e.g. team-engineering, team-marketing, team-management)'),
    },
    async ({ team_id }) => {
      const team = await apiGet<{
        name: string;
        agents: Array<{ name: string; emoji: string; role: string; llm_preference: string; success_rate: number; total_tasks_completed: number }>;
      }>(`/api/teams/${team_id}`);
      if (!team) {
        return { content: [{ type: 'text' as const, text: `⚠️ Team "${team_id}" not found.` }] };
      }

      let text = `👥 **${team.name}** — ${team.agents?.length || 0} agents\n\n`;
      if (team.agents) {
        for (const a of team.agents) {
          text += `${a.emoji || '🤖'} **${a.name}** — ${a.role} (${a.llm_preference}, ${(a.success_rate * 100).toFixed(0)}% success, ${a.total_tasks_completed} tasks)\n`;
        }
      }
      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_sessions ─────────────────────────────────────────────────────────

  server.tool(
    'get_sessions',
    'Show recent agent sessions. Includes status, team, repo, branch, and duration.',
    {
      limit: z.number().optional().describe('Number of sessions to show (default 5)'),
    },
    async ({ limit }) => {
      const sessions = await apiGet<Array<{
        id: string;
        team_name: string;
        status: string;
        target_repo: string;
        branch_name: string;
        started_at: string;
        duration_seconds: number | null;
        pr_url: string | null;
      }>>(`/api/sessions?limit=${limit || 5}`);

      if (!sessions || sessions.length === 0) {
        return { content: [{ type: 'text' as const, text: '📋 No sessions found yet.' }] };
      }

      let text = '📋 **Recent Sessions**\n\n';
      for (const s of sessions) {
        const dur = s.duration_seconds ? `${Math.round(s.duration_seconds / 60)}min` : 'running';
        const pr = s.pr_url ? ` [PR](${s.pr_url})` : '';
        text += `• **${s.team_name}** → ${s.target_repo} [${s.status}] ${dur}${pr}\n`;
        if (s.branch_name) text += `  Branch: \`${s.branch_name}\`\n`;
      }
      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── get_stats ────────────────────────────────────────────────────────────

  server.tool(
    'get_stats',
    'Show dashboard statistics: sessions, tasks, agents, and experiments counts.',
    {},
    async () => {
      const stats = await apiGet<{
        totalSessions: number;
        activeSessions: number | null;
        totalTasks: number;
        completedTasks: number | null;
        failedTasks: number | null;
        totalAgents: number;
        activeAgents: number | null;
      }>('/api/metrics/stats');

      if (!stats) {
        return { content: [{ type: 'text' as const, text: '⚠️ Could not fetch stats.' }] };
      }

      const text = `📊 **Dashboard Stats**

• Sessions: ${stats.totalSessions} total, ${stats.activeSessions ?? 0} active
• Tasks: ${stats.totalTasks} total, ${stats.completedTasks ?? 0} completed, ${stats.failedTasks ?? 0} failed
• Agents: ${stats.totalAgents} total, ${stats.activeAgents ?? 0} active`;

      return { content: [{ type: 'text' as const, text }] };
    }
  );

  // ── start_session ────────────────────────────────────────────────────────

  server.tool(
    'start_session',
    'Start a new agent session for a team on a repository. Creates an entry in the database.',
    {
      team: z.enum(['team-engineering', 'team-marketing', 'team-management']).describe('Which team to assign'),
      repo: z.string().describe('Target repository name (e.g. beta-appcaire)'),
      branch: z.string().optional().describe('Optional branch name'),
    },
    async ({ team, repo, branch }) => {
      const sessionId = `session-${Date.now()}`;
      const ok = await apiPost('/api/sessions', {
        sessionId,
        teamId: team,
        targetRepo: repo,
        branchName: branch || undefined,
      });

      if (!ok) {
        return { content: [{ type: 'text' as const, text: '❌ Failed to create session. Is the API server running?' }] };
      }

      return { content: [{ type: 'text' as const, text: `🚀 Session started: ${sessionId}\nTeam: ${team}\nRepo: ${repo}${branch ? `\nBranch: ${branch}` : ''}` }] };
    }
  );

  // ── track_command ────────────────────────────────────────────────────────

  server.tool(
    'track_command',
    'Track a user command for automation pattern detection. Helps identify repetitive tasks that could be automated.',
    {
      command: z.string().describe('The command or request text'),
      intent: z.string().optional().describe('Normalized intent (e.g. "start_sprint", "check_status")'),
    },
    async ({ command, intent }) => {
      await apiPost('/api/commands', {
        commandText: command,
        normalizedIntent: intent || undefined,
      });
      return { content: [{ type: 'text' as const, text: `✅ Command tracked: "${command}"` }] };
    }
  );
}
