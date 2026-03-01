import { Router, type Request, type Response } from 'express';
import { existsSync, readFileSync } from 'fs';
import { resolve } from 'path';
import { homedir } from 'os';
import { spawnSync } from 'child_process';
import https from 'https';
import { getRepoConfig, getServiceRoot } from '../lib/config.js';
import type { SystemHealth } from '../types/index.js';

const router = Router();

const DEFAULT_REQUIRED_APPCAIRE_JOBS = [
  'com.appcaire.agent-server',
  'com.appcaire.auto-compound',
  'com.appcaire.daily-compound-review',
  'com.appcaire.morning-briefing',
  'com.appcaire.weekly-review',
] as const;

const REQUIRED_SCRIPTS = [
  'scripts/restart-darwin.sh',
  'scripts/start-all-services.sh',
  'scripts/verify-all-services.sh',
  'scripts/setup-telegram-openclaw.sh',
  'scripts/notifications/morning-briefing.sh',
  'scripts/notifications/weekly-review.sh',
  'scripts/notifications/session-complete.sh',
  'scripts/compound/auto-compound.sh',
  'scripts/compound/daily-compound-review.sh',
] as const;

function getRequiredLaunchdJobs(): string[] {
  const override = (process.env.APP_REQUIRED_LAUNCHD_JOBS || '').trim();
  if (!override) {
    return [...DEFAULT_REQUIRED_APPCAIRE_JOBS];
  }
  if (override.toLowerCase() === 'none') {
    return [];
  }
  return override
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
}

function expandHomePath(value: string): string {
  if (!value) return value;
  if (value.startsWith('~')) {
    return value.replace('~', homedir());
  }
  return value;
}

function resolveOpenClawConfigPath(): string {
  const override = expandHomePath((process.env.OPENCLAW_CONFIG_PATH || '').trim());
  if (!override) {
    return resolve(homedir(), '.openclaw', 'openclaw.json');
  }
  if (override.startsWith('/')) {
    return override;
  }
  return resolve(process.cwd(), override);
}

function getOpenClawGatewayLabels(): string[] {
  const configuredLabel = (process.env.OPENCLAW_LAUNCHD_LABEL || '').trim();
  if (configuredLabel) {
    return [configuredLabel];
  }
  return ['com.appcaire.openclaw-darwin', 'ai.openclaw.gateway'];
}

function commandExists(command: string): boolean {
  const out = spawnSync('which', [command], { stdio: 'ignore' });
  return out.status === 0;
}

function getLoadedLaunchdJobs(): Set<string> | null {
  if (process.platform !== 'darwin' || !commandExists('launchctl')) {
    return null;
  }
  const out = spawnSync('launchctl', ['list'], { encoding: 'utf8' });
  if (out.status !== 0 || !out.stdout) {
    return null;
  }
  const labels = new Set<string>();
  for (const line of out.stdout.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const parts = trimmed.split(/\s+/);
    const label = parts[parts.length - 1];
    if (label) labels.add(label);
  }
  return labels;
}

function telegramApiGet(token: string, methodAndQuery: string): Promise<{
  ok: boolean;
  description?: string;
}> {
  return new Promise((resolveRequest) => {
    const url = `https://api.telegram.org/bot${token}/${methodAndQuery}`;
    const req = https.get(url, { timeout: 5000 }, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk.toString();
      });
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body) as { ok?: boolean; description?: string };
          resolveRequest({
            ok: parsed.ok === true,
            description: parsed.description,
          });
        } catch {
          resolveRequest({
            ok: false,
            description: 'Invalid JSON from Telegram API',
          });
        }
      });
    });
    req.on('timeout', () => {
      req.destroy();
      resolveRequest({ ok: false, description: 'Telegram API timeout' });
    });
    req.on('error', (err) => {
      resolveRequest({ ok: false, description: err.message });
    });
  });
}

router.get('/health', async (req: Request, res: Response) => {
  try {
    const deep = String(req.query.deep ?? '').toLowerCase();
    const runDeepChecks = deep === '1' || deep === 'true' || deep === 'yes';
    const serviceRoot = getServiceRoot();
    const now = new Date().toISOString();

    // Workspace
    const darwinRepo = getRepoConfig('darwin');
    const workspacePath = darwinRepo?.workspace?.path ?? darwinRepo?.path ?? null;
    const workspaceExists = workspacePath ? existsSync(workspacePath) : false;
    const workspaceCheck = {
      ok: workspaceExists,
      path: workspacePath,
      exists: workspaceExists,
      details: workspaceExists
        ? undefined
        : 'darwin workspace path is missing or not found',
    };

    // OpenClaw
    const openclawConfigPath = resolveOpenClawConfigPath();
    const openclawConfigExists = existsSync(openclawConfigPath);
    let openclawPlaceholdersFound = false;
    if (openclawConfigExists) {
      try {
        const text = readFileSync(openclawConfigPath, 'utf8');
        openclawPlaceholdersFound =
          text.includes('YOUR_TELEGRAM_BOT_TOKEN') ||
          text.includes('YOUR_TELEGRAM_USER_ID');
      } catch {
        openclawPlaceholdersFound = true;
      }
    }
    const openclawCliInstalled = commandExists('openclaw');
    const loadedJobs = getLoadedLaunchdJobs();
    const openclawGatewayLabels = getOpenClawGatewayLabels();
    const openclawGatewayLoaded =
      loadedJobs == null ? null : openclawGatewayLabels.some((label) => loadedJobs.has(label));
    const openclawOk =
      openclawConfigExists &&
      !openclawPlaceholdersFound &&
      openclawCliInstalled &&
      (openclawGatewayLoaded !== false);
    const openclawCheck = {
      ok: openclawOk,
      configExists: openclawConfigExists,
      configPath: openclawConfigPath,
      placeholdersFound: openclawPlaceholdersFound,
      cliInstalled: openclawCliInstalled,
      gatewayLoaded: openclawGatewayLoaded,
      gatewayLabels: openclawGatewayLabels,
      details: openclawOk
        ? undefined
        : 'OpenClaw config/CLI/gateway is not fully configured',
    };

    // Telegram
    const telegramToken = process.env.TELEGRAM_BOT_TOKEN ?? '';
    const telegramChatId = process.env.TELEGRAM_CHAT_ID ?? '';
    const tokenPresent = telegramToken.length > 0;
    const chatIdPresent = telegramChatId.length > 0;
    let tokenValid: boolean | null = null;
    let chatIdValid: boolean | null = null;
    let telegramDetails = '';
    if (runDeepChecks && tokenPresent) {
      const me = await telegramApiGet(telegramToken, 'getMe');
      tokenValid = me.ok;
      if (!me.ok) {
        telegramDetails = me.description ?? 'Telegram getMe failed';
      }
      if (chatIdPresent) {
        const chat = await telegramApiGet(
          telegramToken,
          `getChat?chat_id=${encodeURIComponent(telegramChatId)}`,
        );
        chatIdValid = chat.ok;
        if (!chat.ok && !telegramDetails) {
          telegramDetails = chat.description ?? 'Telegram getChat failed';
        }
      }
    }
    const telegramOk = runDeepChecks
      ? tokenPresent && chatIdPresent && tokenValid === true && chatIdValid === true
      : tokenPresent && chatIdPresent;
    const telegramCheck = {
      ok: telegramOk,
      tokenPresent,
      chatIdPresent,
      tokenValid,
      chatIdValid,
      details: telegramOk
        ? undefined
        : telegramDetails || 'Telegram token/chat id is missing or invalid',
    };

    // launchd core jobs
    const requiredLaunchdJobs = getRequiredLaunchdJobs();
    const launchdSupported = process.platform === 'darwin' && commandExists('launchctl');
    const jobs: Record<string, boolean> = {};
    if (launchdSupported && loadedJobs) {
      for (const job of requiredLaunchdJobs) {
        jobs[job] = loadedJobs.has(job);
      }
    } else {
      for (const job of requiredLaunchdJobs) {
        jobs[job] = false;
      }
    }
    const launchdOk =
      !launchdSupported ||
      requiredLaunchdJobs.length === 0 ||
      Object.values(jobs).every((isLoaded) => isLoaded);
    const launchdCheck = {
      ok: launchdOk,
      supported: launchdSupported,
      requiredJobs: requiredLaunchdJobs,
      jobs,
      details: launchdOk
        ? undefined
        : 'One or more required launchd jobs are not loaded',
    };

    // Script presence
    const missingScripts = REQUIRED_SCRIPTS.filter((rel) => !existsSync(resolve(serviceRoot, rel)));
    const scriptsCheck = {
      ok: missingScripts.length === 0,
      missing: missingScripts,
      details:
        missingScripts.length === 0
          ? undefined
          : `Missing scripts: ${missingScripts.join(', ')}`,
    };

    const criticalFail =
      !workspaceCheck.ok ||
      !scriptsCheck.ok;
    const warningFail =
      !openclawCheck.ok ||
      !telegramCheck.ok ||
      !launchdCheck.ok;

    const overall: SystemHealth['overall'] = criticalFail
      ? 'unhealthy'
      : warningFail
        ? 'degraded'
        : 'healthy';

    const data: SystemHealth = {
      checkedAt: now,
      deep: runDeepChecks,
      overall,
      checks: {
        workspace: workspaceCheck,
        openclaw: openclawCheck,
        telegram: telegramCheck,
        launchd: launchdCheck,
        scripts: scriptsCheck,
      },
    };

    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to build system health',
    });
  }
});

export default router;
