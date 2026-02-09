-- Seed Data for Agent Service Database

-- Teams
INSERT INTO teams (id, name, domain, created_at) VALUES
('team-engineering', 'Engineering', 'engineering', CURRENT_TIMESTAMP),
('team-marketing', 'Marketing', 'marketing', CURRENT_TIMESTAMP);

-- Engineering Team Agents (Original 6)
INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active, created_at) VALUES
('agent-orchestrator', 'team-engineering', 'Orchestrator', 'Coordinates all engineering agents, delegates tasks, manages session workflow', '🎯', 'opus', TRUE, CURRENT_TIMESTAMP),
('agent-backend', 'team-engineering', 'Backend', 'API development, database design, server-side logic, authentication', '⚙️', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-frontend', 'team-engineering', 'Frontend', 'React components, UI implementation, state management, routing', '🎨', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-infrastructure', 'team-engineering', 'Infrastructure', 'Deployment, CI/CD, Docker, environment configuration', '🏗️', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-verification', 'team-engineering', 'Verification', 'Testing, quality assurance, bug detection, validation', '✅', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-senior-reviewer', 'team-engineering', 'Senior Reviewer', 'Code review, architecture validation, best practices enforcement', '👨‍💻', 'opus', TRUE, CURRENT_TIMESTAMP);

-- New Engineering Team Agents (3 new specialists)
INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active, created_at) VALUES
('agent-db-architect', 'team-engineering', 'DB Architect', 'Database design, Prisma schema, Apollo GraphQL, PostgreSQL optimization, query performance', '🗄️', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-ux-designer', 'team-engineering', 'UX Designer', 'Modern UX 2026, responsive design, PWA, React Native, brand guidelines, accessibility, mobile-first', '🎭', 'opus', TRUE, CURRENT_TIMESTAMP),
('agent-docs-expert', 'team-engineering', 'Documentation Expert', 'Keep docs updated, archive obsolete docs, verify with team, publish to docs page, maintain accuracy', '📚', 'sonnet', TRUE, CURRENT_TIMESTAMP);

-- Gamification Expert Agent (Agent Levelup)
INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active, created_at) VALUES
('agent-levelup', 'team-engineering', 'Agent Levelup', 'Gamification expert: XP systems, achievements, leaderboards, progression mechanics, engagement optimization', '🎮', 'sonnet', TRUE, CURRENT_TIMESTAMP);

-- Marketing Team Agents (10 Marvel characters)
INSERT INTO agents (id, team_id, name, role, emoji, llm_preference, is_active, created_at) VALUES
('agent-jarvis', 'team-marketing', 'Jarvis', 'Marketing Lead: Campaign orchestration, strategy coordination, team management', '🤵', 'opus', TRUE, CURRENT_TIMESTAMP),
('agent-shuri', 'team-marketing', 'Shuri', 'Content Innovation: Blog posts, technical content, thought leadership', '👩‍🔬', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-fury', 'team-marketing', 'Fury', 'Campaign Strategy: Multi-channel planning, competitive analysis, market intelligence', '👁️', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-vision', 'team-marketing', 'Vision', 'SEO Specialist: Keyword research, on-page optimization, technical SEO, analytics', '💎', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-loki', 'team-marketing', 'Loki', 'Content Strategist: Editorial calendar, content themes, storytelling, brand voice', '🎭', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-wanda', 'team-marketing', 'Wanda', 'Social Media Manager: Community engagement, content scheduling, trend monitoring', '✨', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-quill', 'team-marketing', 'Quill', 'Social Media Content: Post creation, hashtag strategy, platform optimization', '🎸', 'haiku', TRUE, CURRENT_TIMESTAMP),
('agent-pepper', 'team-marketing', 'Pepper', 'Email Marketing: Campaign design, segmentation, automation, deliverability', '💼', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-friday', 'team-marketing', 'Friday', 'Analytics & Reporting: Data analysis, performance tracking, insights generation', '📊', 'sonnet', TRUE, CURRENT_TIMESTAMP),
('agent-wong', 'team-marketing', 'Wong', 'Lead Management: Lead scoring, qualification, nurturing, CRM integration', '📖', 'sonnet', TRUE, CURRENT_TIMESTAMP);

-- Initialize some sample repositories
INSERT INTO repositories (id, name, path, github_url, team_id, is_active, created_at) VALUES
('repo-beta-appcaire', 'beta-appcaire', '/Users/bjornevers_MacPro/HomeCare/beta-appcaire', 'https://github.com/eirtech-ai/beta-appcaire', 'team-engineering', TRUE, CURRENT_TIMESTAMP),
('repo-agent-service', 'be-agent-service', '/Users/bjornevers_MacPro/HomeCare/be-agent-service', 'https://github.com/eirtech-ai/be-agent-service', 'team-engineering', TRUE, CURRENT_TIMESTAMP);
