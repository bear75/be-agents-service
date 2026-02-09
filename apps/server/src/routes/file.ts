import { Router, Request, Response } from 'express';
import fs from 'fs';
import path from 'path';
import { getServiceRoot } from '../lib/config.js';

const router = Router();

const ALLOWED_BASE_PATHS = [
  getServiceRoot(),
  path.join(getServiceRoot(), '..', 'beta-appcaire'),
];

/** GET /api/file/docs?path=guides/quick-start.md - Serve docs from docs/ dir */
router.get('/docs', (req: Request, res: Response) => {
  const relativePath = (req.query.path as string)?.replace(/\.\./g, '') || '';
  const docsDir = path.join(getServiceRoot(), 'docs');
  const filePath = path.join(docsDir, relativePath);

  if (!path.resolve(filePath).startsWith(path.resolve(docsDir))) {
    return res.status(403).json({ error: 'Access denied' });
  }

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.type('text/plain; charset=utf-8').send(data);
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
