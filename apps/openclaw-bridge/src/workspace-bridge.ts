/**
 * Workspace Bridge
 *
 * Resolves workspace path from environment variables or config file.
 * Provides the connection between MCP tools and the markdown workspace.
 */

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface RepoConfig {
  path: string;
  workspace?: {
    path: string;
    enabled: boolean;
  };
  enabled: boolean;
}

interface ReposConfig {
  repos: Record<string, RepoConfig>;
}

/**
 * Resolve the workspace path from environment or config
 *
 * Priority:
 * 1. WORKSPACE_PATH env var (direct path)
 * 2. WORKSPACE_CONFIG + WORKSPACE_REPO env vars (from repos.yaml)
 * 3. Default config location (../../config/repos.yaml) + first enabled repo
 */
export function resolveWorkspacePath(): string | null {
  // 1. Direct path override
  const directPath = process.env.WORKSPACE_PATH;
  if (directPath) {
    const expanded = directPath.replace(/^~/, process.env.HOME || '~');
    if (existsSync(expanded)) return expanded;
    console.error(`[bridge] WORKSPACE_PATH does not exist: ${expanded}`);
    return null;
  }

  // 2. From config file
  const configPath = process.env.WORKSPACE_CONFIG
    ? resolve(process.env.WORKSPACE_CONFIG.replace(/^~/, process.env.HOME || '~'))
    : resolve(__dirname, '..', '..', '..', 'config', 'repos.yaml');

  if (!existsSync(configPath)) {
    console.error(`[bridge] Config not found: ${configPath}`);
    return null;
  }

  try {
    const content = readFileSync(configPath, 'utf8');
    const config = yaml.load(content) as ReposConfig;

    const targetRepo = process.env.WORKSPACE_REPO;

    if (targetRepo) {
      // Specific repo requested
      const repo = config.repos[targetRepo];
      if (!repo?.workspace?.enabled || !repo.workspace.path) {
        console.error(`[bridge] No workspace configured for repo: ${targetRepo}`);
        return null;
      }
      return repo.workspace.path.replace(/^~/, process.env.HOME || '~');
    }

    // Find first enabled repo with workspace
    for (const [name, repo] of Object.entries(config.repos)) {
      if (repo.enabled && repo.workspace?.enabled && repo.workspace.path) {
        console.error(`[bridge] Using workspace for repo: ${name}`);
        return repo.workspace.path.replace(/^~/, process.env.HOME || '~');
      }
    }

    console.error('[bridge] No repos with workspace found in config');
    return null;
  } catch (error) {
    console.error(`[bridge] Failed to parse config: ${error}`);
    return null;
  }
}

/**
 * Get the templates directory path
 */
export function getTemplatesDir(): string {
  // Resolve relative to service root
  const configPath = process.env.WORKSPACE_CONFIG
    ? resolve(process.env.WORKSPACE_CONFIG.replace(/^~/, process.env.HOME || '~'))
    : resolve(__dirname, '..', '..', '..', 'config', 'repos.yaml');

  const serviceRoot = resolve(dirname(configPath), '..');
  return resolve(serviceRoot, 'scripts', 'workspace', 'templates');
}
