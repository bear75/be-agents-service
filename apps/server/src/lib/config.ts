import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';
import type { ReposConfig, RepoConfig } from '../types/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Service root is three levels up from apps/server/src/lib
const SERVICE_ROOT = resolve(__dirname, '..', '..', '..', '..');

export function loadReposConfig(): ReposConfig {
  const configPath = resolve(SERVICE_ROOT, 'config', 'repos.yaml');

  if (!existsSync(configPath)) {
    throw new Error(`Config file not found: ${configPath}`);
  }

  const fileContents = readFileSync(configPath, 'utf8');
  const config = yaml.load(fileContents) as ReposConfig;

  // Expand ~ in paths
  Object.keys(config.repos).forEach((repoName) => {
    const repo = config.repos[repoName];
    if (repo.path.startsWith('~')) {
      repo.path = repo.path.replace('~', process.env.HOME || '~');
    }
    // Expand ~ in workspace path
    if (repo.workspace?.path?.startsWith('~')) {
      repo.workspace.path = repo.workspace.path.replace('~', process.env.HOME || '~');
    }
  });

  return config;
}

export function getRepoConfig(repoName: string): RepoConfig | null {
  const config = loadReposConfig();
  return config.repos[repoName] || null;
}

export function listRepos(): string[] {
  const config = loadReposConfig();
  return Object.keys(config.repos);
}

export function getServiceRoot(): string {
  return SERVICE_ROOT;
}
