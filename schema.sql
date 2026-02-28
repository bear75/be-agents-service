-- SQLite Database Schema for Self-Learning RL Agent Service
-- Version: 1.0.0
-- Purpose: Transform file-based state into queryable, relational database

-- ============================================
-- CORE ORGANIZATIONAL STRUCTURE
-- ============================================

-- Teams (Engineering, Marketing, Management)
CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    domain TEXT NOT NULL CHECK(domain IN ('engineering', 'marketing', 'management')),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agents (specialists within teams)
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL REFERENCES teams(id),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    emoji TEXT,
    llm_preference TEXT DEFAULT 'sonnet' CHECK(llm_preference IN ('opus-4.6', 'opus', 'sonnet', 'haiku', 'pi')),
    success_rate REAL DEFAULT 0.0 CHECK(success_rate BETWEEN 0 AND 1),
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_failed INTEGER DEFAULT 0,
    avg_duration_seconds REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name)
);

-- ============================================
-- SESSION & TASK TRACKING
-- ============================================

-- Sessions (orchestrator runs)
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL REFERENCES teams(id),
    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed', 'failed', 'blocked')),
    target_repo TEXT NOT NULL,
    priority_file TEXT,
    branch_name TEXT,
    pr_url TEXT,
    iteration_count INTEGER DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    duration_seconds INTEGER,
    exit_code INTEGER,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Tasks (individual agent work units)
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    agent_id TEXT NOT NULL REFERENCES agents(id),
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed', 'failed', 'blocked')),
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
    llm_used TEXT CHECK(llm_used IN ('opus-4.6', 'opus', 'sonnet', 'haiku', 'pi')),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    duration_seconds INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- ============================================
-- REINFORCEMENT LEARNING SYSTEM
-- ============================================

-- Experiments (hypotheses being tested)
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'successful', 'failed', 'killed')),
    success_metric TEXT NOT NULL,
    target_value REAL,
    current_value REAL,
    sample_size INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,
    decision TEXT CHECK(decision IN ('keep', 'kill', 'double_down', 'continue')),
    decision_reason TEXT,
    decided_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Metrics (quantitative measurements)
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('session', 'task', 'agent', 'experiment', 'pattern')),
    entity_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    context TEXT, -- JSON
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Patterns (detected behaviors - success/failure/user repetition)
CREATE TABLE IF NOT EXISTS patterns (
    id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN ('success', 'failure', 'user_repetition')),
    description TEXT NOT NULL,
    detection_count INTEGER DEFAULT 1,
    confidence_score REAL DEFAULT 0.5 CHECK(confidence_score BETWEEN 0 AND 1),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'verified', 'false_positive', 'actioned')),
    action_taken TEXT,
    first_detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    actioned_at DATETIME
);

-- Lessons Learned (accumulated knowledge)
CREATE TABLE IF NOT EXISTS lessons_learned (
    id TEXT PRIMARY KEY,
    category TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    source TEXT, -- which session/task revealed this
    times_encountered INTEGER DEFAULT 1,
    is_automated BOOLEAN DEFAULT FALSE,
    automated_via TEXT, -- agent ID or script name
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_encountered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Rewards (RL feedback signals)
CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK(entity_type IN ('task', 'session', 'experiment')),
    entity_id TEXT NOT NULL,
    reward_value INTEGER NOT NULL,
    reason TEXT NOT NULL,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- USER BEHAVIOR TRACKING (for automation)
-- ============================================

-- User Commands (track CEO inputs for pattern detection)
CREATE TABLE IF NOT EXISTS user_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_text TEXT NOT NULL,
    normalized_intent TEXT,
    team TEXT,
    model TEXT,
    priority_file TEXT,
    branch_name TEXT,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Automation Candidates (detected repetitive tasks)
CREATE TABLE IF NOT EXISTS automation_candidates (
    id TEXT PRIMARY KEY,
    pattern_description TEXT NOT NULL,
    occurrence_count INTEGER DEFAULT 1,
    sample_commands TEXT, -- JSON array of example commands
    confidence_score REAL DEFAULT 0.5 CHECK(confidence_score BETWEEN 0 AND 1),
    is_automated BOOLEAN DEFAULT FALSE,
    agent_id TEXT REFERENCES agents(id),
    approved_by_user BOOLEAN DEFAULT FALSE,
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_occurrence_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- MARKETING DATA
-- ============================================

-- Leads
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    company TEXT,
    status TEXT NOT NULL CHECK(status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    score INTEGER DEFAULT 50 CHECK(score BETWEEN 0 AND 100),
    assigned_to TEXT REFERENCES agents(id),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    owner TEXT REFERENCES agents(id),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'paused', 'completed')),
    channels TEXT, -- JSON array
    deliverables TEXT, -- JSON array
    metrics TEXT, -- JSON object
    start_date DATE,
    end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Content Pieces
CREATE TABLE IF NOT EXISTS content (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('blog', 'email', 'social', 'landing-page', 'docs')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'review', 'published')),
    author TEXT REFERENCES agents(id),
    campaign_id TEXT REFERENCES campaigns(id),
    word_count INTEGER,
    seo_score INTEGER CHECK(seo_score BETWEEN 0 AND 100),
    file_path TEXT,
    published_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    published_at DATETIME
);

-- ============================================
-- INTEGRATIONS & SETTINGS
-- ============================================

-- Integrations (messaging, email, social, API keys, tools)
CREATE TABLE IF NOT EXISTS integrations (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('messaging', 'email', 'social', 'api', 'tool')),
    platform TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    credentials TEXT, -- JSON (encrypted API keys, tokens)
    config TEXT, -- JSON (platform-specific config)
    managed_by TEXT REFERENCES agents(id),
    last_connected_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- REPOSITORY MANAGEMENT
-- ============================================

-- Repositories (multi-repo support)
CREATE TABLE IF NOT EXISTS repositories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    github_url TEXT,
    team_id TEXT REFERENCES teams(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SCHEDULE OPTIMIZATION (Timefold FSR runs)
-- ============================================

-- Schedule runs (pipeline: queued → running → completed/cancelled/failed)
CREATE TABLE IF NOT EXISTS schedule_runs (
    id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    batch TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    strategy TEXT NOT NULL,
    hypothesis TEXT,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK(status IN ('queued', 'running', 'completed', 'cancelled', 'failed')),
    decision TEXT
        CHECK(decision IN ('keep', 'kill', 'double_down', 'continue')),
    decision_reason TEXT,
    timefold_score TEXT,
    routing_efficiency_pct REAL,
    unassigned_visits INTEGER,
    total_visits INTEGER,
    unassigned_pct REAL,
    continuity_avg REAL,
    continuity_max INTEGER,
    continuity_over_target INTEGER,
    continuity_target INTEGER DEFAULT 11,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    cancelled_at DATETIME,
    duration_seconds INTEGER,
    output_path TEXT,
    notes TEXT,
    iteration INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_schedule_runs_dataset ON schedule_runs(dataset);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_status ON schedule_runs(status);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_submitted ON schedule_runs(submitted_at DESC);

-- ============================================
-- LLM COST TRACKING
-- ============================================

-- LLM Usage (cost optimization)
CREATE TABLE IF NOT EXISTS llm_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT REFERENCES tasks(id),
    model TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    duration_ms INTEGER,
    used_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SEED DATA
-- ============================================

-- Seed teams
INSERT OR IGNORE INTO teams (id, name, domain, description) VALUES
    ('team-engineering', 'Engineering', 'engineering', '10 specialists + orchestrator + senior reviewer'),
    ('team-marketing', 'Marketing', 'marketing', '10 Marvel character agents led by Jarvis'),
    ('team-management', 'Management', 'management', 'Executive leadership: CEO, CPO/CTO, CMO/CSO, HR Agent Lead');

-- Seed engineering agents
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

-- Seed marketing agents
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

-- Seed management agents
INSERT OR IGNORE INTO agents (id, team_id, name, role, emoji, llm_preference) VALUES
    ('agent-ceo', 'team-management', 'CEO', 'Strategic Direction', '👔', 'opus-4.6'),
    ('agent-cpo-cto', 'team-management', 'CPO/CTO', 'Engineering Lead', '🎯', 'opus'),
    ('agent-cmo-cso', 'team-management', 'CMO/CSO', 'Marketing Lead', '📊', 'opus'),
    ('agent-hr-lead', 'team-management', 'HR Agent Lead', 'Agent Development', '👥', 'sonnet'),
    ('agent-interface', 'team-management', 'Interface Agent', 'Human-Agent Interface via Telegram/Workspace', '🔗', 'sonnet');

-- Seed integrations — Messaging
INSERT OR IGNORE INTO integrations (id, type, platform, name, brand, is_active, config, managed_by) VALUES
    ('int-telegram', 'messaging', 'telegram', 'Telegram Bot (OpenClaw)', NULL, TRUE, '{"botToken":"configured","setupCmd":"openclaw channels add telegram --token YOUR_TOKEN"}', 'agent-interface');

-- Seed integrations — Email
INSERT OR IGNORE INTO integrations (id, type, platform, name, brand, is_active, config) VALUES
    ('int-email-sales-caire', 'email', 'gmail', 'Sales @ caire.se', 'CAIRE', FALSE, '{"email":"sales@caire.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_1_USER","envPass":"EMAIL_1_PASSWORD"}'),
    ('int-email-info-caire', 'email', 'gmail', 'Info @ caire.se', 'CAIRE', FALSE, '{"email":"info@caire.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_2_USER","envPass":"EMAIL_2_PASSWORD"}'),
    ('int-email-bjorn-caire', 'email', 'gmail', 'Bjorn @ caire.se', 'CAIRE', FALSE, '{"email":"bjorn@caire.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_3_USER","envPass":"EMAIL_3_PASSWORD"}'),
    ('int-email-sales-eirtech', 'email', 'gmail', 'Sales @ eirtech.ai', 'EIRTECH', FALSE, '{"email":"sales@eirtech.ai","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_4_USER","envPass":"EMAIL_4_PASSWORD"}'),
    ('int-email-info-eirtech', 'email', 'gmail', 'Info @ eirtech.ai', 'EIRTECH', FALSE, '{"email":"info@eirtech.ai","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_5_USER","envPass":"EMAIL_5_PASSWORD"}'),
    ('int-email-bjorn-eirtech', 'email', 'gmail', 'Bjorn @ eirtech.ai', 'EIRTECH', FALSE, '{"email":"bjorn@eirtech.ai","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_6_USER","envPass":"EMAIL_6_PASSWORD"}'),
    ('int-email-sales-nacka', 'email', 'gmail', 'Sales @ nackahemtjanst.se', 'NACKA', FALSE, '{"email":"sales@nackahemtjanst.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_7_USER","envPass":"EMAIL_7_PASSWORD"}'),
    ('int-email-info-nacka', 'email', 'gmail', 'Info @ nackahemtjanst.se', 'NACKA', FALSE, '{"email":"info@nackahemtjanst.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_8_USER","envPass":"EMAIL_8_PASSWORD"}'),
    ('int-email-bjorn-nacka', 'email', 'gmail', 'Bjorn @ nackahemtjanst.se', 'NACKA', FALSE, '{"email":"bjorn@nackahemtjanst.se","imapHost":"imap.gmail.com","imapPort":993,"envUser":"EMAIL_9_USER","envPass":"EMAIL_9_PASSWORD"}'),
    ('int-smtp', 'email', 'smtp', 'Email SMTP Server', NULL, FALSE, '{"host":"smtp.gmail.com","port":587}');

-- Seed integrations — Social Media
INSERT OR IGNORE INTO integrations (id, type, platform, name, brand, is_active, config, managed_by) VALUES
    ('int-fb-caire', 'social', 'facebook', 'Facebook Page - Caire', 'CAIRE', FALSE, '{"description":"Community engagement, events, customer testimonials"}', 'agent-quill'),
    ('int-ig-caire', 'social', 'instagram', 'Instagram - @caire.se', 'CAIRE', FALSE, '{"handle":"@caire.se","description":"Visual storytelling, customer success stories, behind-the-scenes"}', 'agent-wanda'),
    ('int-ig-eirtech', 'social', 'instagram', 'Instagram - @eirtech.ai', 'EIRTECH', FALSE, '{"handle":"@eirtech.ai","description":"EU customer stories, Dublin office culture, tech insights"}', 'agent-wanda'),
    ('int-ig-bjorn', 'social', 'instagram', 'Instagram - @bjornevers', 'BJORN EVERS', FALSE, '{"handle":"@bjornevers","description":"Personal life, work-life balance, travel, product screenshots"}', 'agent-wanda'),
    ('int-li-caire', 'social', 'linkedin', 'LinkedIn - Caire', 'CAIRE', FALSE, '{"page":"https://linkedin.com/company/caire","description":"B2B marketing, thought leadership, product updates"}', 'agent-vision'),
    ('int-li-eirtech', 'social', 'linkedin', 'LinkedIn - Eirtech.ai', 'EIRTECH', FALSE, '{"page":"https://linkedin.com/company/eirtech-ai","description":"EU market B2B, GDPR compliance messaging, partnerships"}', 'agent-vision'),
    ('int-li-bjorn', 'social', 'linkedin', 'LinkedIn - Bjorn Evers (Personal)', 'BJORN EVERS', FALSE, '{"page":"https://linkedin.com/in/bjornevers","description":"Thought leadership, founder journey, AI insights, hiring"}', 'agent-vision'),
    ('int-x-caire', 'social', 'twitter', 'X (Twitter) - @caire_se', 'CAIRE', FALSE, '{"handle":"@caire_se","description":"Product announcements, customer support, industry news"}', 'agent-quill'),
    ('int-x-eirtech', 'social', 'twitter', 'X (Twitter) - @eirtech_ai', 'EIRTECH', FALSE, '{"handle":"@eirtech_ai","description":"EU tech community, AI insights, product updates"}', 'agent-quill'),
    ('int-x-bjorn', 'social', 'twitter', 'X (Twitter) - @bjornevers', 'BJORN EVERS', FALSE, '{"handle":"@bjornevers","description":"Founder insights, tech commentary, product building, AI/startup thoughts"}', 'agent-quill');

-- Seed integrations — API Keys
INSERT OR IGNORE INTO integrations (id, type, platform, name, brand, is_active, config) VALUES
    ('int-anthropic', 'api', 'anthropic', 'Anthropic API', NULL, TRUE, '{"model":"claude-sonnet-4-5"}'),
    ('int-openai', 'api', 'openai', 'OpenAI API', NULL, FALSE, '{}');

-- Seed integrations — Tools & Platforms
INSERT OR IGNORE INTO integrations (id, type, platform, name, brand, is_active, config) VALUES
    ('int-confluence', 'tool', 'confluence', 'Confluence Documentation', NULL, FALSE, '{"baseUrl":"https://caire.atlassian.net/wiki","spaceKey":"TWC","parentPageId":"393372"}'),
    ('int-figma', 'tool', 'figma', 'Figma Design', NULL, FALSE, '{}'),
    ('int-github', 'tool', 'github', 'GitHub Organization', NULL, TRUE, '{}'),
    ('int-hubspot', 'tool', 'hubspot', 'HubSpot CRM', NULL, FALSE, '{}'),
    ('int-jira', 'tool', 'jira', 'Jira Project Management', NULL, FALSE, '{"baseUrl":"https://caire.atlassian.net","projectKey":"CAIRE"}'),
    ('int-miro', 'tool', 'miro', 'Miro Workshops', NULL, FALSE, '{}'),
    ('int-notion', 'tool', 'notion', 'Notion Workspace', NULL, FALSE, '{}');

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_session ON tasks(session_id);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_agents_team ON agents(team_id);
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active);

-- Additional indexes from table definitions
CREATE INDEX IF NOT EXISTS idx_metrics_entity ON metrics(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_status ON patterns(status);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons_learned(category);
CREATE INDEX IF NOT EXISTS idx_lessons_automated ON lessons_learned(is_automated);
CREATE INDEX IF NOT EXISTS idx_rewards_entity ON rewards(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_commands_intent ON user_commands(normalized_intent);
CREATE INDEX IF NOT EXISTS idx_commands_executed ON user_commands(executed_at);
CREATE INDEX IF NOT EXISTS idx_automation_status ON automation_candidates(is_automated);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_owner ON campaigns(owner);
CREATE INDEX IF NOT EXISTS idx_content_type ON content(type);
CREATE INDEX IF NOT EXISTS idx_content_status ON content(status);
CREATE INDEX IF NOT EXISTS idx_repos_active ON repositories(is_active);
CREATE INDEX IF NOT EXISTS idx_integrations_type ON integrations(type);
CREATE INDEX IF NOT EXISTS idx_integrations_platform ON integrations(platform);
CREATE INDEX IF NOT EXISTS idx_llm_model ON llm_usage(model);
CREATE INDEX IF NOT EXISTS idx_llm_task ON llm_usage(task_id);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Active sessions with agent count
CREATE VIEW IF NOT EXISTS v_active_sessions AS
SELECT
    s.id,
    s.team_id,
    t.name AS team_name,
    s.status,
    s.target_repo,
    s.branch_name,
    COUNT(DISTINCT tk.agent_id) AS agent_count,
    COUNT(tk.id) AS task_count,
    s.started_at
FROM sessions s
JOIN teams t ON s.team_id = t.id
LEFT JOIN tasks tk ON s.id = tk.session_id
WHERE s.status IN ('pending', 'in_progress')
GROUP BY s.id;

-- Agent performance summary
CREATE VIEW IF NOT EXISTS v_agent_performance AS
SELECT
    a.id,
    a.name,
    a.role,
    t.name AS team_name,
    a.total_tasks_completed,
    a.total_tasks_failed,
    ROUND(a.success_rate * 100, 2) AS success_rate_pct,
    ROUND(a.avg_duration_seconds / 60.0, 2) AS avg_duration_minutes
FROM agents a
JOIN teams t ON a.team_id = t.id
WHERE a.is_active = TRUE
ORDER BY a.success_rate DESC;

-- Experiment status summary
CREATE VIEW IF NOT EXISTS v_experiment_status AS
SELECT
    status,
    COUNT(*) AS count,
    AVG(consecutive_failures) AS avg_consecutive_failures,
    AVG(sample_size) AS avg_sample_size
FROM experiments
GROUP BY status;

-- User command patterns (for automation detection)
CREATE VIEW IF NOT EXISTS v_user_command_patterns AS
SELECT
    normalized_intent,
    COUNT(*) AS occurrence_count,
    MAX(executed_at) AS last_executed,
    GROUP_CONCAT(DISTINCT team) AS teams_used,
    GROUP_CONCAT(DISTINCT model) AS models_used
FROM user_commands
WHERE executed_at >= datetime('now', '-7 days')
GROUP BY normalized_intent
HAVING COUNT(*) >= 3
ORDER BY occurrence_count DESC;
