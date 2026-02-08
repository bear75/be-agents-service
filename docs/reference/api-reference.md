# API Reference

Complete API documentation for the Agent Service Dashboard.

---

## Table of Contents

1. [Job Control APIs](#job-control-apis)
2. [HR Agent Management](#hr-agent-management)
3. [RL Dashboard APIs](#rl-dashboard-apis)
4. [Session APIs](#session-apis)
5. [File APIs](#file-apis)

---

## Job Control APIs

### Start Engineering Job

**Endpoint:** `POST /api/jobs/start`

**Request Body:**
```json
{
  "type": "engineering",
  "model": "sonnet" | "opus" | "haiku",
  "priorityFile": "reports/priorities-2026-02-08.md",
  "branch": "feature/new-feature"
}
```

**Response:**
```json
{
  "success": true,
  "jobId": "job-1234567890",
  "message": "Engineering job started",
  "branch": "feature/new-feature"
}
```

**Example:**
```bash
curl -X POST http://localhost:3030/api/jobs/start \
  -H "Content-Type: application/json" \
  -d '{
    "type": "engineering",
    "model": "sonnet",
    "priorityFile": "reports/priorities-2026-02-08.md",
    "branch": "feature/test"
  }'
```

---

### Start Marketing Campaign

**Endpoint:** `POST /api/jobs/start`

**Request Body:**
```json
{
  "type": "marketing",
  "model": "sonnet",
  "campaignFile": "reports/marketing-campaign-Q1.md",
  "branch": "feature/q1-campaign",
  "description": "Q1 product launch campaign"
}
```

**Response:**
```json
{
  "success": true,
  "jobId": "job-1234567891",
  "message": "Marketing campaign started",
  "branch": "feature/q1-campaign"
}
```

---

### Stop Job

**Endpoint:** `POST /api/jobs/:id/stop`

**Parameters:**
- `id` - Job ID to stop

**Response:**
```json
{
  "success": true,
  "message": "Job stopped successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:3030/api/jobs/job-1234567890/stop
```

---

### Get Job Logs

**Endpoint:** `GET /api/jobs/:id/logs`

**Parameters:**
- `id` - Job ID
- `tail` (optional) - Number of lines to return (default: 100)

**Response:**
```json
{
  "success": true,
  "logs": "Orchestrator started...\nBackend specialist spawned...\n...",
  "jobId": "job-1234567890"
}
```

**Example:**
```bash
curl http://localhost:3030/api/jobs/job-1234567890/logs?tail=50
```

---

### List Active Jobs

**Endpoint:** `GET /api/jobs/active`

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "id": "job-1234567890",
      "type": "engineering",
      "status": "running",
      "branch": "feature/test",
      "startedAt": "2026-02-08T10:00:00Z",
      "pid": 12345
    }
  ]
}
```

---

## HR Agent Management

### List All Agents

**Endpoint:** `GET /api/agents`

**Query Parameters:**
- `domain` (optional) - Filter by domain: "engineering" | "marketing"

**Response:**
```json
{
  "success": true,
  "agents": [
    {
      "id": "orchestrator",
      "name": "Orchestrator",
      "role": "Scrum Master",
      "domain": "engineering",
      "status": "active",
      "tasksCompleted": 42,
      "successRate": 0.95
    },
    {
      "id": "backend",
      "name": "Backend Specialist",
      "role": "Backend Developer",
      "domain": "engineering",
      "status": "active",
      "tasksCompleted": 38,
      "successRate": 0.92
    }
  ]
}
```

**Example:**
```bash
# Get all agents
curl http://localhost:3030/api/agents

# Get engineering agents only
curl http://localhost:3030/api/agents?domain=engineering

# Get marketing agents only
curl http://localhost:3030/api/agents?domain=marketing
```

---

### Hire New Agent

**Endpoint:** `POST /api/agents/create`

**Request Body:**
```json
{
  "name": "QA Specialist",
  "role": "Quality Assurance",
  "domain": "engineering",
  "specialties": ["testing", "automation", "quality-gates"],
  "model": "sonnet"
}
```

**Response:**
```json
{
  "success": true,
  "agent": {
    "id": "qa-specialist",
    "name": "QA Specialist",
    "role": "Quality Assurance",
    "domain": "engineering",
    "status": "active",
    "createdAt": "2026-02-08T10:00:00Z"
  },
  "message": "Agent hired successfully"
}
```

---

### Fire Agent

**Endpoint:** `POST /api/agents/:id/fire`

**Parameters:**
- `id` - Agent ID to fire

**Request Body:**
```json
{
  "reason": "Underperforming - 3 consecutive failures"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent fired successfully",
  "reason": "Underperforming - 3 consecutive failures"
}
```

---

### Get Agent Evaluation

**Endpoint:** `GET /api/agents/:id/evaluation`

**Parameters:**
- `id` - Agent ID

**Response:**
```json
{
  "success": true,
  "evaluation": {
    "agentId": "backend",
    "name": "Backend Specialist",
    "tasksCompleted": 38,
    "tasksTotal": 42,
    "successRate": 0.90,
    "avgCompletionTime": 720,
    "recentPerformance": [
      {"date": "2026-02-08", "success": true, "duration": 680},
      {"date": "2026-02-07", "success": true, "duration": 750},
      {"date": "2026-02-06", "success": false, "duration": 120}
    ],
    "recommendation": "Keep - High performer",
    "insights": [
      "Consistently completes tasks under 12 minutes",
      "90% success rate above threshold",
      "Recent failure was due to external dependency"
    ]
  }
}
```

---

## RL Dashboard APIs

### Get Experiments

**Endpoint:** `GET /api/rl/experiments`

**Response:**
```json
{
  "success": true,
  "experiments": [
    {
      "id": "exp-1",
      "name": "Parallel Backend + Infrastructure",
      "status": "active",
      "successCount": 45,
      "failureCount": 2,
      "successRate": 0.96,
      "recommendation": "Double down - Working well"
    },
    {
      "id": "exp-2",
      "name": "Frontend waits for Backend schema",
      "status": "active",
      "successCount": 42,
      "failureCount": 0,
      "successRate": 1.0,
      "recommendation": "Double down - Perfect success rate"
    }
  ]
}
```

---

### Evaluate Experiments

**Endpoint:** `POST /api/rl/experiments/evaluate`

**Description:** Evaluates all experiments and applies Keep/Kill/Double-down logic

**Response:**
```json
{
  "success": true,
  "evaluations": [
    {
      "experimentId": "exp-1",
      "decision": "double_down",
      "reason": "90%+ success rate, 5+ tasks"
    },
    {
      "experimentId": "exp-3",
      "decision": "kill",
      "reason": "3+ consecutive failures"
    }
  ]
}
```

---

### Get Detected Patterns

**Endpoint:** `GET /api/rl/patterns`

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "type": "success",
      "pattern": "Running codegen after GraphQL changes prevents type errors",
      "occurrences": 15,
      "confidence": 0.95
    },
    {
      "type": "failure",
      "pattern": "Missing organizationId filter causes security issues",
      "occurrences": 3,
      "confidence": 0.90,
      "recommendation": "Add to verification checks"
    }
  ]
}
```

---

### Get Agent Performance

**Endpoint:** `GET /api/rl/agent-performance`

**Response:**
```json
{
  "success": true,
  "insights": [
    {
      "agentId": "backend",
      "name": "Backend Specialist",
      "tasksTotal": 42,
      "successRate": 0.90,
      "avgDuration": 720,
      "trend": "improving",
      "recommendation": "Keep - High performer"
    },
    {
      "agentId": "infrastructure",
      "name": "Infrastructure Specialist",
      "tasksTotal": 12,
      "successRate": 0.67,
      "avgDuration": 300,
      "trend": "declining",
      "recommendation": "Monitor - Low success rate"
    }
  ]
}
```

---

### Get Automation Candidates

**Endpoint:** `GET /api/rl/automation-candidates`

**Response:**
```json
{
  "success": true,
  "candidates": [
    {
      "task": "Run codegen after GraphQL changes",
      "repetitions": 12,
      "lastOccurrence": "2026-02-08T10:00:00Z",
      "recommendation": "Automate - User repeats 3+ times",
      "proposedAgent": "Auto-Codegen Agent"
    },
    {
      "task": "Create priority file from verbal description",
      "repetitions": 8,
      "lastOccurrence": "2026-02-08T09:00:00Z",
      "recommendation": "Automate - High repetition",
      "proposedAgent": "Priority Generator Agent"
    }
  ]
}
```

---

## Session APIs

### Get Session Details

**Endpoint:** `GET /api/sessions/:id`

**Parameters:**
- `id` - Session ID

**Response:**
```json
{
  "success": true,
  "session": {
    "sessionId": "session-1234567890",
    "createdAt": "2026-02-08T10:00:00Z",
    "status": "completed",
    "agents": {
      "orchestrator": {
        "status": "completed",
        "phase": "pr_creation"
      },
      "backend": {
        "status": "completed",
        "completedTasks": 5,
        "duration": 900
      },
      "frontend": {
        "status": "completed",
        "completedTasks": 3,
        "duration": 600
      },
      "verification": {
        "status": "completed",
        "result": "pass"
      }
    },
    "prUrl": "https://github.com/org/repo/pull/123"
  }
}
```

---

### List Sessions

**Endpoint:** `GET /api/sessions`

**Query Parameters:**
- `limit` (optional) - Number of sessions to return (default: 10)
- `status` (optional) - Filter by status: "active" | "completed" | "blocked" | "failed"

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "sessionId": "session-1234567890",
      "createdAt": "2026-02-08T10:00:00Z",
      "status": "completed",
      "branch": "feature/test",
      "prUrl": "https://github.com/org/repo/pull/123"
    }
  ]
}
```

---

## File APIs

### Read File

**Endpoint:** `GET /api/file`

**Query Parameters:**
- `path` - Absolute path to file

**Response:**
```
Raw file contents
```

**Example:**
```bash
curl "http://localhost:3030/api/file?path=/Users/user/HomeCare/be-agent-service/AGENTS.md"
```

---

### List Priority Files

**Endpoint:** `GET /api/priorities`

**Response:**
```json
{
  "success": true,
  "priorities": [
    {
      "file": "priorities-2026-02-08.md",
      "path": "reports/priorities-2026-02-08.md",
      "modifiedAt": "2026-02-08T09:00:00Z"
    },
    {
      "file": "marketing-campaign-Q1.md",
      "path": "reports/marketing-campaign-Q1.md",
      "modifiedAt": "2026-02-07T15:00:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (job/agent/session not found)
- `500` - Internal Server Error

---

## WebSocket Events

The dashboard uses WebSocket for real-time updates:

**Connection:** `ws://localhost:3030`

**Events:**

### Job Status Update
```json
{
  "event": "job:status",
  "data": {
    "jobId": "job-1234567890",
    "status": "running",
    "progress": 0.45
  }
}
```

### Agent Status Update
```json
{
  "event": "agent:status",
  "data": {
    "agentId": "backend",
    "status": "active",
    "currentTask": "Updating schema.prisma"
  }
}
```

### Session Complete
```json
{
  "event": "session:complete",
  "data": {
    "sessionId": "session-1234567890",
    "status": "completed",
    "prUrl": "https://github.com/org/repo/pull/123"
  }
}
```

---

For implementation examples, see the dashboard source code in `/dashboard/server.js`.
