-- Seed data: run on every server startup so existing DBs get new teams/agents (e.g. schedule-optimization).
-- INSERT OR IGNORE: safe to run repeatedly.

-- Teams
INSERT OR IGNORE INTO teams (id, name, domain, description) VALUES
    ('team-engineering', 'Engineering', 'engineering', '10 specialists + orchestrator + senior reviewer'),
    ('team-marketing', 'Marketing', 'marketing', '10 Marvel character agents led by Jarvis'),
    ('team-management', 'Management', 'management', 'Executive leadership: CEO, CPO/CTO, CMO/CSO, HR Agent Lead'),
    ('team-schedule-optimization', 'Schedule optimization', 'schedule-optimization', 'Timefold FSR pipeline: submit, monitor, cancel runs; propose strategies (spaghetti sort)');

-- Engineering agents
INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-orchestrator', 'team-engineering', 'Orchestrator', 'Scrum Master', '🎯', 'sonnet'),
    ('agent-backend', 'team-engineering', 'Backend', 'Database & GraphQL', '⚙️', 'sonnet'),
    ('agent-frontend', 'team-engineering', 'Frontend', 'React & UI', '🎨', 'sonnet'),
    ('agent-infrastructure', 'team-engineering', 'Infrastructure', 'DevOps & CI/CD', '🏗️', 'sonnet'),
    ('agent-verification', 'team-engineering', 'Verification', 'Testing & QA', '✅', 'haiku'),
    ('agent-senior-reviewer', 'team-engineering', 'Senior Reviewer', 'Code Review', '🔍', 'opus'),
    ('agent-db-architect', 'team-engineering', 'DB Architect', 'Database design, Prisma schema, Apollo GraphQL, PostgreSQL optimization, query performance', '🗄️', 'sonnet'),
    ('agent-ux-designer', 'team-engineering', 'UX Designer', 'Modern UX 2026, responsive design, PWA, React Native, brand guidelines, accessibility, mobile-first', '🎭', 'opus'),
    ('agent-docs-expert', 'team-engineering', 'Documentation Expert', 'Keep docs updated, archive obsolete docs, verify with team, publish to docs page, maintain accuracy', '📚', 'sonnet'),
    ('agent-levelup', 'team-engineering', 'Agent Levelup', 'Gamification expert: XP systems, achievements, leaderboards, progression mechanics, engagement optimization', '🎮', 'sonnet');

-- Marketing agents
INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-jarvis', 'team-marketing', 'Jarvis', 'Marketing Lead', '🤵', 'opus'),
    ('agent-shuri', 'team-marketing', 'Shuri', 'Product Marketing', '👩‍🔬', 'sonnet'),
    ('agent-fury', 'team-marketing', 'Fury', 'Market Research', '👁️', 'sonnet'),
    ('agent-vision', 'team-marketing', 'Vision', 'SEO Analyst', '💎', 'sonnet'),
    ('agent-loki', 'team-marketing', 'Loki', 'Content Writer', '✍️', 'sonnet'),
    ('agent-quill', 'team-marketing', 'Quill', 'Social Media', '🎸', 'haiku'),
    ('agent-wanda', 'team-marketing', 'Wanda', 'Design', '✨', 'sonnet'),
    ('agent-pepper', 'team-marketing', 'Pepper', 'Email Marketing', '💼', 'sonnet'),
    ('agent-friday', 'team-marketing', 'Friday', 'Marketing Dev', '💻', 'sonnet'),
    ('agent-wong', 'team-marketing', 'Wong', 'Notion Manager', '📚', 'haiku');

-- Schedule-optimization (Timefold / TF) agents
INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-timefold-specialist', 'team-schedule-optimization', 'Timefold Specialist', 'Submit/monitor/cancel FSR jobs, run metrics and continuity scripts, write results to Darwin DB', '🕐', 'sonnet'),
    ('agent-optimization-mathematician', 'team-schedule-optimization', 'Optimization Mathematician', 'Analyse completed runs, propose N strategies (exploitation + exploration), spaghetti sort cancellation heuristics', '📐', 'sonnet');

-- Management agents
INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-ceo', 'team-management', 'CEO', 'Strategic Direction', '👔', 'opus-4.6'),
    ('agent-cpo-cto', 'team-management', 'CPO/CTO', 'Engineering Lead', '🎯', 'opus'),
    ('agent-cmo-cso', 'team-management', 'CMO/CSO', 'Marketing Lead', '📊', 'opus'),
    ('agent-hr-lead', 'team-management', 'HR Agent Lead', 'Agent Development', '👥', 'sonnet'),
    ('agent-interface', 'team-management', 'Interface Agent', 'Human-Agent Interface via Telegram/Workspace', '🔗', 'sonnet');
