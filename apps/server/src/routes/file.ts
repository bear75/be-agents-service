import { Router, Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import { getServiceRoot, getRepoConfig } from '../lib/config.js';

const router = Router();

/** Map agent ID to script and prompt file base names (without extension) */
const AGENT_TO_FILES: Record<string, { script: string; prompt: string }> = {
  // Engineering
  'agent-backend': { script: 'backend-specialist', prompt: 'backend-specialist' },
  'agent-frontend': { script: 'frontend-specialist', prompt: 'frontend-specialist' },
  'agent-infrastructure': { script: 'infrastructure-specialist', prompt: 'infrastructure-specialist' },
  'agent-verification': { script: 'verification-specialist', prompt: 'verification-specialist' },
  'agent-senior-reviewer': { script: 'senior-code-reviewer', prompt: 'senior-code-reviewer' },
  'agent-db-architect': { script: 'db-architect-specialist', prompt: 'db-architect-specialist' },
  'agent-ux-designer': { script: 'ux-designer-specialist', prompt: 'ux-designer-specialist' },
  'agent-docs-expert': { script: 'documentation-expert', prompt: 'documentation-expert' },
  'agent-levelup': { script: 'levelup-specialist', prompt: 'levelup-specialist' },
  'agent-orchestrator': { script: 'orchestrator', prompt: 'orchestrator' },
  // Marketing
  'agent-jarvis': { script: 'marketing/jarvis-orchestrator', prompt: 'jarvis-orchestrator' },
  'agent-vision': { script: 'marketing/vision-seo-analyst', prompt: 'vision-seo-analyst' },
  'agent-loki': { script: 'marketing/loki-content-writer', prompt: 'loki-content-writer' },
  'agent-shuri': { script: 'marketing/shuri-product-analyst', prompt: 'shuri-product-analyst' },
  'agent-fury': { script: 'marketing/fury-customer-researcher', prompt: 'fury-customer-researcher' },
  'agent-wanda': { script: 'marketing/wanda-designer', prompt: 'wanda-designer' },
  'agent-quill': { script: 'marketing/quill-social-media', prompt: 'quill-social-media' },
  'agent-pepper': { script: 'marketing/pepper-email-marketing', prompt: 'pepper-email-marketing' },
  'agent-friday': { script: 'marketing/friday-developer', prompt: 'friday-developer' },
  'agent-wong': { script: 'marketing/wong-notion-agent', prompt: 'wong-notion-agent' },
  // Management
  'agent-ceo': { script: 'management/ceo', prompt: 'ceo' },
  'agent-cmo-cso': { script: 'management/cmo-cso', prompt: 'cmo-cso' },
  'agent-cpo-cto': { script: 'management/cpo-cto', prompt: 'cpo-cto' },
  'agent-hr-lead': { script: 'management/hr-agent-lead', prompt: 'hr-agent-lead' },
  'agent-interface': { script: 'management/interface-agent', prompt: 'interface-agent' },
  // Schedule optimization (Timefold FSR pipeline)
  'agent-timefold-specialist': { script: 'timefold-specialist', prompt: 'timefold-specialist' },
  'agent-optimization-mathematician': { script: 'optimization-mathematician', prompt: 'optimization-mathematician' },
};

/** Resolve any agent ID (incl. DB-generated) to canonical key for AGENT_TO_FILES */
function resolveCanonicalAgentId(agentId: string): string | null {
  if (AGENT_TO_FILES[agentId]) return agentId;
  const lower = agentId.toLowerCase();
  for (const key of Object.keys(AGENT_TO_FILES)) {
    const slug = key.replace(/^agent-/, '');
    if (lower.includes(slug)) return key;
  }
  return null;
}

function expandHome(filePath: string): string {
  return filePath.startsWith('~')
    ? filePath.replace('~', process.env.HOME || '~')
    : filePath;
}

function resolveAllowedBasePaths(): string[] {
  const raw = (process.env.FILE_ACCESS_ALLOWED_PATHS || '').trim();
  if (!raw) {
    return [getServiceRoot(), path.join(getServiceRoot(), '..', 'beta-appcaire')];
  }
  return raw
    .split(',')
    .map((entry) => expandHome(entry.trim()))
    .filter(Boolean)
    .map((entry) => (path.isAbsolute(entry) ? entry : path.resolve(getServiceRoot(), entry)));
}

function resolveDocsDir(): string {
  const planDocsRoot = (process.env.PLAN_DOCS_ROOT || '').trim();
  if (!planDocsRoot) {
    return path.join(getServiceRoot(), 'docs');
  }
  const expanded = expandHome(planDocsRoot);
  return path.isAbsolute(expanded)
    ? expanded
    : path.resolve(getServiceRoot(), expanded);
}

const ALLOWED_BASE_PATHS = resolveAllowedBasePaths();

/** Serve docs from docs/ dir - used by both direct route and router */
export function handleDocsRequest(req: Request, res: Response): void {
  const raw = (req.query.path as string) || '';
  const relativePath = raw.replace(/\.\./g, '').replace(/^\/+/, '').trim() || '';
  const docsDir = resolveDocsDir();
  const filePath = path.join(docsDir, relativePath);

  if (!path.resolve(filePath).startsWith(path.resolve(docsDir))) {
    res.status(403).json({ error: 'Access denied' });
    return;
  }

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.type('text/plain; charset=utf-8').send(data);
  });
}

/** GET /api/file/docs?path=guides/quick-start.md - Serve docs from docs/ dir */
router.get('/docs', handleDocsRequest);

/** GET /api/file/agent-script?agentId=agent-backend - Serve agent script content */
router.get('/agent-script', (req: Request, res: Response) => {
  const rawId = (req.query.agentId as string)?.trim();
  const agentId = rawId ? resolveCanonicalAgentId(rawId) : null;
  if (!agentId || !AGENT_TO_FILES[agentId]) {
    return res.status(400).json({ error: 'Unknown agent ID' });
  }
  const { script } = AGENT_TO_FILES[agentId];
  const scriptPath = path.join(getServiceRoot(), 'agents', `${script}.sh`);
  fs.readFile(scriptPath, 'utf8', (err, data) => {
    if (err) {
      return res.status(404).json({ error: 'Script not found', path: scriptPath });
    }
    res.type('text/plain; charset=utf-8').send(data);
  });
});

/** GET /api/file/agent-prompt?agentId=agent-backend&repo=beta-appcaire - Serve agent prompt (agents/prompts first, then target repo) */
router.get('/agent-prompt', (req: Request, res: Response) => {
  const rawId = (req.query.agentId as string)?.trim();
  const agentId = rawId ? resolveCanonicalAgentId(rawId) : null;
  const repoName =
    (req.query.repo as string)?.trim() ||
    process.env.DEFAULT_TARGET_REPO ||
    'appcaire';
  if (!agentId || !AGENT_TO_FILES[agentId]) {
    return res.status(400).json({ error: 'Unknown agent ID' });
  }
  const { prompt } = AGENT_TO_FILES[agentId];
  const localPromptPath = path.join(getServiceRoot(), 'agents', 'prompts', `${prompt}.md`);

  const trySend = (filePath: string, cb: () => void) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (!err) {
        res.type('text/plain; charset=utf-8').send(data);
        return;
      }
      cb();
    });
  };

  trySend(localPromptPath, () => {
    const repoConfig = getRepoConfig(repoName);
    if (!repoConfig?.path) {
      return res.status(404).json({ error: 'Prompt not found (no repo config)', repo: repoName });
    }
    const repoPromptPath = path.join(repoConfig.path, '.claude', 'prompts', `${prompt}.md`);
    trySend(repoPromptPath, () => {
      res.status(404).json({ error: 'Prompt not found', path: repoPromptPath });
    });
  });
});

router.get('/', (req: Request, res: Response) => {
  const filePath = req.query.path as string;

  if (!filePath) {
    return res.status(400).json({ error: 'Missing path parameter' });
  }

  const isAllowed = ALLOWED_BASE_PATHS.some((allowed) =>
    path.resolve(filePath).startsWith(path.resolve(allowed))
  );

  if (!isAllowed) {
    return res.status(403).json({ error: 'Access denied to this path' });
  }

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.type('text/plain; charset=utf-8').send(data);
  });
});

export default router;
