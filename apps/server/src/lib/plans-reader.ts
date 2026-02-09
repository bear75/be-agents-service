/**
 * Plans Reader
 *
 * Reads PRD/plan documents from the docs/ directory in the agent service.
 * Extracts metadata (priority, status, limitations) from frontmatter-like headers.
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'fs';
import { join, basename } from 'path';
import type { PlanDocument, SetupStatus } from '../types/index.js';

/**
 * Read all plan/PRD documents from docs/
 */
export function readPlans(serviceRoot: string): PlanDocument[] {
  const docsDir = join(serviceRoot, 'docs');
  if (!existsSync(docsDir)) return [];

  try {
    const files = readdirSync(docsDir)
      .filter((f) => f.startsWith('PRD-') && f.endsWith('.md'))
      .sort();

    return files.map((filename) => {
      const filePath = join(docsDir, filename);
      const content = readFileSync(filePath, 'utf8');
      const stats = statSync(filePath);
      const slug = basename(filename, '.md').toLowerCase();

      // Extract title from first # heading
      const titleMatch = content.match(/^#\s+(.+)/m);
      const title = titleMatch ? titleMatch[1].replace(/^PRD:\s*/i, '').trim() : slug;

      // Extract priority from content
      const priorityMatch = content.match(/\*\*Priority:\*\*\s*(\d+)/);
      const priority = priorityMatch ? parseInt(priorityMatch[1]) : undefined;

      // Extract status from content
      const statusMatch = content.match(/\*\*Status:\*\*\s*(.+)/);
      const statusRaw = statusMatch ? statusMatch[1].trim().toLowerCase() : 'planning';
      const status = parseStatus(statusRaw);

      // Extract summary (problem statement first paragraph)
      const summaryMatch = content.match(/## 1\. Problem Statement\n\n(.+?)(?:\n\n|$)/s);
      const summary = summaryMatch
        ? summaryMatch[1].split('\n')[0].replace(/\*\*/g, '').trim()
        : undefined;

      // Extract limitations from Non-Goals section
      const limitations = extractLimitations(content);

      return {
        slug,
        filename,
        title,
        priority,
        status,
        summary,
        limitations,
        content,
        lastModified: stats.mtime.toISOString(),
      };
    });
  } catch {
    return [];
  }
}

/**
 * Read a single plan document by slug
 */
export function readPlan(serviceRoot: string, slug: string): PlanDocument | null {
  const plans = readPlans(serviceRoot);
  return plans.find((p) => p.slug === slug) || null;
}

/**
 * Check setup readiness
 */
export function checkSetupStatus(
  serviceRoot: string,
  workspacePath?: string
): SetupStatus {
  const openclawConfigPath = join(serviceRoot, 'config', 'openclaw', 'openclaw.json');
  const openclawConfigExists = existsSync(openclawConfigPath);

  // Check if the openclaw config has real values (not just template)
  let openclawConfigured = false;
  if (openclawConfigExists) {
    try {
      const config = readFileSync(openclawConfigPath, 'utf8');
      openclawConfigured = !config.includes('YOUR_TELEGRAM_USER_ID');
    } catch {
      // ignore
    }
  }

  // Check Telegram env vars
  const telegramConfigured = !!(
    process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID
  );

  // Check launchd plists exist
  const morningBriefingPlist = existsSync(
    join(serviceRoot, 'launchd', 'com.appcaire.morning-briefing.plist')
  );
  const weeklyReviewPlist = existsSync(
    join(serviceRoot, 'launchd', 'com.appcaire.weekly-review.plist')
  );

  return {
    workspace: {
      configured: !!workspacePath,
      exists: !!workspacePath && existsSync(workspacePath),
      path: workspacePath,
    },
    openclaw: {
      configured: openclawConfigured,
      configPath: openclawConfigExists ? openclawConfigPath : undefined,
    },
    telegram: {
      configured: telegramConfigured,
    },
    launchd: {
      morningBriefing: morningBriefingPlist,
      weeklyReview: weeklyReviewPlist,
    },
  };
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function parseStatus(raw: string): PlanDocument['status'] {
  if (raw.includes('progress')) return 'in-progress';
  if (raw.includes('block')) return 'blocked';
  if (raw.includes('done') || raw.includes('complete')) return 'done';
  if (raw.includes('doc')) return 'docs-only';
  return 'planning';
}

function extractLimitations(content: string): string[] {
  const limitations: string[] = [];

  // Extract from "Non-Goals" section
  const nonGoalsMatch = content.match(/## \d+\. Non-Goals[^\n]*\n([\s\S]*?)(?=\n## |\n---|\n$)/);
  if (nonGoalsMatch) {
    const lines = nonGoalsMatch[1].split('\n');
    for (const line of lines) {
      const itemMatch = line.match(/^[-*]\s+❌\s+(.+)/);
      if (itemMatch) {
        limitations.push(itemMatch[1].trim());
      }
    }
  }

  // Extract from "Open Questions" section
  const questionsMatch = content.match(/## \d+\. Open Questions[^\n]*\n([\s\S]*?)(?=\n## |\n---|\n$)/);
  if (questionsMatch) {
    const lines = questionsMatch[1].split('\n');
    for (const line of lines) {
      const itemMatch = line.match(/^\d+\.\s+\*\*(.+?)\*\*/);
      if (itemMatch) {
        limitations.push(`Open: ${itemMatch[1].trim()}`);
      }
    }
  }

  // Check for specific blockers
  if (content.includes('not yet approved for implementation')) {
    limitations.push('Not yet approved for implementation');
  }
  if (content.includes('separate repository') || content.includes('separate repo')) {
    limitations.push('Requires separate repository setup');
  }
  if (content.includes('needs monorepo access') || content.includes('beta-appcaire')) {
    limitations.push('Needs access to beta-appcaire monorepo');
  }

  return limitations;
}
