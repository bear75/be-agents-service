# API Endpoints Reference

Complete REST API documentation for the Agent Service.

**Base URL:** `http://localhost:3030`

---

## Table of Contents

1. [Health Check](#health-check)
2. [Teams API](#teams-api)
3. [Agents API](#agents-api)
4. [Tasks API](#tasks-api)
5. [Sessions API](#sessions-api)
6. [Jobs API](#jobs-api)
7. [Integrations API](#integrations-api)
8. [Data API](#data-api)
9. [RL API](#rl-api)
10. [File API](#file-api)

---

## Health Check

### GET /health

Check if the server is running.

**Response:**
```json
{
  "success": true,
  "service": "agent-service",
  "version": "1.0.0",
  "timestamp": "2025-02-09T18:00:00.000Z"
}
```

---

## Teams API

### GET /api/teams

List all teams.

**Response:**
```json
{
  "success": true,
  "teams": [
    {
      "id": "engineering",
      "name": "Engineering Team",
      "domain": "engineering",
      "description": "Software development and infrastructure",
      "created_at": "2025-01-01T00:00:00.000Z",
      "updated_at": "2025-01-01T00:00:00.000Z"
    }
  ],
  "count": 1
}
```

### GET /api/teams/:id

Get team by ID with agents and statistics.

**Parameters:**
- `id` (path) - Team ID (e.g., "engineering", "marketing", "management")

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "engineering",
    "name": "Engineering Team",
    "domain": "engineering",
    "description": "Software development and infrastructure",
    "agents": [
      {
        "id": "backend-specialist",
        "team_id": "engineering",
        "name": "Backend Specialist",
        "role": "Develop backend services",
        "emoji": "⚙️",
        "llm_preference": "sonnet",
        "is_active": true
      }
    ],
    "stats": {
      "total_tasks": 100,
      "completed_tasks": 85,
      "failed_tasks": 10,
      "in_progress_tasks": 5,
      "avg_duration_seconds": 120.5,
      "success_rate": "85.0%"
    }
  }
}
```

### POST /api/teams

Create a new team.

**Request Body:**
```json
{
  "id": "operations",
  "name": "Operations Team",
  "domain": "management",
  "description": "DevOps and infrastructure"
}
```

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "operations",
    "name": "Operations Team",
    "domain": "management",
    "description": "DevOps and infrastructure",
    "created_at": "2025-02-09T18:00:00.000Z"
  }
}
```

### PATCH /api/teams/:id

Update a team's name or description.

**Parameters:**
- `id` (path) - Team ID

**Request Body:**
```json
{
  "name": "Updated Team Name",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "success": true,
  "team": {
    "id": "operations",
    "name": "Updated Team Name",
    "domain": "management",
    "description": "Updated description",
    "updated_at": "2025-02-09T18:30:00.000Z"
  }
}
```

### DELETE /api/teams/:id

Soft delete a team (deactivates all agents).

**Parameters:**
- `id` (path) - Team ID

**Response:**
```json
{
  "success": true,
  "message": "Team Engineering Team deactivated. 5 agent(s) deactivated.",
  "deactivated_agents": 5
}
```

---

## Agents API

### GET /api/agents

List all active agents.

**Response:**
```json
[
  {
    "id": "backend-specialist",
    "team_id": "engineering",
    "name": "Backend Specialist",
    "role": "Develop backend services",
    "emoji": "⚙️",
    "llm_preference": "sonnet",
    "is_active": true,
    "team_name": "Engineering Team"
  }
]
```

### POST /api/agents/create

Create a new agent.

**Request Body:**
```json
{
  "teamId": "engineering",
  "name": "API Specialist",
  "role": "Develop REST APIs",
  "llmPreference": "sonnet",
  "emoji": "🔌"
}
```

**Response:**
```json
{
  "success": true,
  "agent": {
    "id": "api-specialist-abc123",
    "team_id": "engineering",
    "name": "API Specialist",
    "role": "Develop REST APIs",
    "emoji": "🔌",
    "llm_preference": "sonnet",
    "is_active": true
  }
}
```

### POST /api/agents/:id/fire

Deactivate an agent (soft delete).

**Parameters:**
- `id` (path) - Agent ID

**Response:**
```json
{
  "success": true,
  "agentId": "api-specialist-abc123"
}
```

### POST /api/agents/:id/rehire

Reactivate a previously deactivated agent.

**Parameters:**
- `id` (path) - Agent ID

**Response:**
```json
{
  "agent": {
    "id": "api-specialist-abc123",
    "is_active": true
  }
}
```

---

## Tasks API

### GET /api/tasks

List all tasks with optional filters.

**Query Parameters:**
- `team_id` (optional) - Filter by team ID
- `agent_id` (optional) - Filter by agent ID
- `session_id` (optional) - Filter by session ID
- `status` (optional) - Filter by status (pending, in_progress, completed, failed)

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-abc123",
      "agent_id": "backend-specialist",
      "session_id": "session-xyz789",
      "status": "in_progress",
      "description": "Implement user authentication",
      "priority": "high",
      "llm_model": "sonnet",
      "started_at": "2025-02-09T18:00:00.000Z",
      "agent_name": "Backend Specialist",
      "team_name": "Engineering Team",
      "emoji": "⚙️"
    }
  ],
  "count": 1
}
```

### GET /api/tasks/:id

Get a single task by ID.

**Parameters:**
- `id` (path) - Task ID

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-abc123",
    "agent_id": "backend-specialist",
    "session_id": "session-xyz789",
    "status": "in_progress",
    "description": "Implement user authentication",
    "priority": "high"
  }
}
```

### POST /api/tasks

Create a new task.

**Request Body:**
```json
{
  "sessionId": "session-xyz789",
  "agentId": "backend-specialist",
  "description": "Fix database connection pooling",
  "priority": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-def456",
    "session_id": "session-xyz789",
    "agent_id": "backend-specialist",
    "description": "Fix database connection pooling",
    "priority": "medium",
    "status": "pending"
  }
}
```

### PATCH /api/tasks/:id

Update a task's description or priority.

**Parameters:**
- `id` (path) - Task ID

**Request Body:**
```json
{
  "description": "Updated task description",
  "priority": "high"
}
```

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-abc123",
    "description": "Updated task description",
    "priority": "high"
  }
}
```

### PATCH /api/tasks/:id/status

Update a task's status (for Kanban drag & drop).

**Parameters:**
- `id` (path) - Task ID

**Request Body:**
```json
{
  "status": "in_progress",
  "llmUsed": "sonnet",
  "errorMessage": null
}
```

**Valid statuses:** `pending`, `in_progress`, `completed`, `failed`

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-abc123",
    "status": "in_progress",
    "llm_used": "sonnet"
  }
}
```

---

## Sessions API

### GET /api/sessions

List all sessions.

**Response:**
```json
[
  {
    "id": "session-xyz789",
    "team_id": "engineering",
    "status": "in_progress",
    "target_repo": "beta-appcaire",
    "branch_name": "feature/auth-system",
    "pr_url": null,
    "started_at": "2025-02-09T18:00:00.000Z",
    "team_name": "Engineering Team"
  }
]
```

### GET /api/sessions/:id

Get session by ID with tasks.

**Parameters:**
- `id` (path) - Session ID

**Response:**
```json
{
  "id": "session-xyz789",
  "team_id": "engineering",
  "status": "in_progress",
  "tasks": [
    {
      "id": "task-abc123",
      "description": "Implement user authentication",
      "status": "in_progress"
    }
  ]
}
```

---

## Jobs API

### GET /api/jobs

List all jobs.

**Response:**
```json
[
  {
    "jobId": "job-123",
    "type": "compound",
    "model": "sonnet",
    "priorityFile": "priorities-2025-02-09.md",
    "branchName": "feature/auth-system",
    "status": "running",
    "startTime": "2025-02-09T18:00:00.000Z",
    "pid": 12345
  }
]
```

### POST /api/jobs/start

Start a new job.

**Request Body:**
```json
{
  "team": "engineering",
  "priorityFile": "priorities-2025-02-09.md",
  "branchName": "feature/new-feature",
  "model": "sonnet",
  "baseBranch": "main",
  "targetRepo": "beta-appcaire"
}
```

**Response:**
```json
{
  "jobId": "job-124",
  "type": "compound",
  "status": "running",
  "startTime": "2025-02-09T18:05:00.000Z"
}
```

### POST /api/jobs/:id/stop

Stop a running job.

**Parameters:**
- `id` (path) - Job ID

**Response:**
```json
{
  "success": true
}
```

### GET /api/jobs/:id/status

Get job status.

**Parameters:**
- `id` (path) - Job ID

**Response:**
```json
{
  "jobId": "job-123",
  "status": "completed",
  "exitCode": 0,
  "endTime": "2025-02-09T18:30:00.000Z"
}
```

### GET /api/jobs/:id/logs

Get job logs.

**Parameters:**
- `id` (path) - Job ID

**Response:** Plain text log content

---

## Integrations API

### GET /api/integrations

List all integrations.

**Response:**
```json
[
  {
    "id": "telegram-bot",
    "type": "messaging",
    "platform": "telegram",
    "name": "Telegram Bot",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00.000Z"
  }
]
```

### PATCH /api/integrations/:id

Update integration.

**Parameters:**
- `id` (path) - Integration ID

**Request Body:**
```json
{
  "is_active": true,
  "config": {
    "webhookUrl": "https://example.com/webhook"
  }
}
```

**Response:**
```json
{
  "id": "telegram-bot",
  "is_active": true,
  "updated_at": "2025-02-09T18:00:00.000Z"
}
```

---

## Data API

### GET /api/data/campaigns

List all marketing campaigns.

**Response:**
```json
[
  {
    "id": "campaign-123",
    "name": "Q1 Product Launch",
    "status": "active",
    "owner": "marketing-specialist",
    "owner_name": "Marketing Specialist",
    "owner_emoji": "📢"
  }
]
```

### GET /api/data/leads

List all leads.

**Response:**
```json
[
  {
    "id": "lead-456",
    "source": "website",
    "status": "new",
    "assigned_to": "sales-specialist"
  }
]
```

---

## RL API

### GET /api/rl/experiments

List all RL experiments.

**Response:**
```json
[
  {
    "id": "exp-789",
    "name": "LLM Router Optimization",
    "status": "active",
    "success_metric": "task_completion_rate",
    "target_value": 0.9,
    "current_value": 0.85
  }
]
```

### GET /api/rl/patterns

List detected patterns.

**Response:**
```json
[
  {
    "id": "pattern-abc",
    "pattern_type": "success",
    "description": "Backend tasks complete faster with Sonnet",
    "detection_count": 15,
    "confidence_score": 0.85
  }
]
```

---

## File API

### GET /api/file/docs

Serve documentation files from `docs/` directory.

**Query Parameters:**
- `path` (required) - Relative path to doc file (e.g., "guides/quick-start.md")

**Example:**
```
GET /api/file/docs?path=guides/quick-start.md
```

**Response:** Plain text markdown content

**Security:** Only files within `docs/` directory are accessible. Path traversal (`../`) is blocked.

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message here",
  "message": "Detailed error information (optional)"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/invalid parameters)
- `403` - Forbidden (access denied)
- `404` - Not Found
- `409` - Conflict (e.g., already running)
- `500` - Internal Server Error

---

## Authentication

Currently, the API does not require authentication. All endpoints are accessible without tokens or API keys.

**Future:** Authentication will be added for production deployments.

---

## Rate Limiting

Currently, no rate limiting is enforced.

**Future:** Rate limiting will be added to prevent abuse.

---

## Related Documentation

- [docs-archive/DASHBOARD_MIGRATION.md](../docs-archive/DASHBOARD_MIGRATION.md) - Dashboard migration (archived)
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [README.md](./README.md) - Documentation index
