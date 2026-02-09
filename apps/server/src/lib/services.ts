/**
 * Load CommonJS lib modules from monorepo root.
 * Used by consolidated server routes.
 */
import { createRequire } from 'module';
import path from 'path';
import fs from 'fs';
import { getServiceRoot } from './config.js';

const require = createRequire(import.meta.url);
const ROOT = getServiceRoot();

export const db = require(path.join(ROOT, 'lib/database'));
export const jobExecutor = require(path.join(ROOT, 'lib/job-executor'));
export const learningController = require(path.join(ROOT, 'lib/learning-controller'));
export const patternDetector = require(path.join(ROOT, 'lib/pattern-detector'));
export const llmRouter = require(path.join(ROOT, 'lib/llm-router'));
export const repositoryManager = require(path.join(ROOT, 'lib/repository-manager'));
export const gamification = require(path.join(ROOT, 'lib/gamification'));

const LOGS_DIR = path.join(ROOT, 'logs/orchestrator-sessions');

export function getSessionLogs(sessionId: string): Record<string, string> {
  try {
    if (!fs.existsSync(LOGS_DIR)) return {};
    const logPath = path.join(LOGS_DIR, sessionId);
    if (!fs.existsSync(logPath)) return {};
    const logs: Record<string, string> = {};
    const files = fs.readdirSync(logPath);
    for (const file of files) {
      if (file.endsWith('.log')) {
        const logName = file.replace('.log', '');
        const content = fs.readFileSync(path.join(logPath, file), 'utf8');
        const lines = content.split('\n');
        logs[logName] = lines.slice(-100).join('\n');
      }
    }
    return logs;
  } catch {
    return {};
  }
}
