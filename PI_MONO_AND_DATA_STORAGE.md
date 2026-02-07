# Pi-Mono & Data Storage Clarification

**Date:** 2026-02-07  
**Questions Answered:** What happened to pi-mono? Where is data stored?

---

## 📋 Quick Answers

### 1. Pi-Mono Status: PLANNED, NOT IMPLEMENTED

**What is pi-mono?**  
https://github.com/badlogic/pi-mono/ - A local LLM framework for running CodeLlama, DeepSeek Coder, and other open-source models locally.

**Status:** Documented in roadmap as "Future: Local LLM Specialist" but not yet implemented.

**Where documented:** `/Users/bjornevers_MacPro/HomeCare/be-agent-service/AGENTS.md` lines 635-682

### 2. Data Storage: FILE-BASED, NOT DATABASE

**Storage Method:** JSON files in `.compound-state/` directory  
**Database:** NONE - no Convex DB, no PostgreSQL, no local database

**Why file-based?** Single-user automation running on Mac mini overnight - no need for database complexity.

---

## Pi-Mono Deep Dive

### What Was Planned

From `AGENTS.md`:

```markdown
## Future: Local LLM Specialist (Simple Tasks)

**Location:** TBD (agents/local-llm-specialist.sh)
**Prompt:** TBD
**Model:** Local LLM via pi-mono or ollama (CodeLlama, DeepSeek Coder)

### Ideal Tasks For Local LLM

- ✅ Package updates (yarn workspace add)
- ✅ Documentation formatting
- ✅ Log summarization
- ✅ Error message parsing
- ✅ CLAUDE.md updates
- ✅ Simple config changes
- ✅ Test file generation (basic)

### NOT Suitable For Local LLM

- ❌ Database schema design
- ❌ Complex business logic
- ❌ Architecture decisions
- ❌ Security-critical code
- ❌ Complex GraphQL resolvers

### Benefits

- **Cost**: Free (local inference)
- **Speed**: No API latency (~500ms vs ~2s)
- **Privacy**: Documentation stays local
- **Availability**: Works offline

### Implementation Plan

1. Install pi-mono or ollama on Mac mini
2. Create local-llm-specialist.sh
3. Add hybrid decision to orchestrator:
   ```bash
   if [[ "$TASK_COMPLEXITY" == "low" ]]; then
     use local-llm-specialist
   else
     use infrastructure-specialist (Claude API)
   fi
   ```
```

### Why Not Implemented Yet

**Current Focus:** Getting the core multi-agent workflow working first (orchestrator, specialists, verification, Senior Code Reviewer) before optimizing with local LLMs.

**Priority:** Functionality > Cost optimization (for now)

**Roadmap Position:** Phase 4-5 (after Option 3 multi-evaluator system is complete)

### When It Should Be Implemented

**Best time:** After these are working:
1. ✅ Option 2: Senior Code Reviewer + iteration loops (DONE)
2. ⏳ Option 3: Multi-evaluator system (IN PROGRESS)
3. 🔮 Option 4: Local LLM for simple tasks (FUTURE)

**Estimated effort:** 1-2 weeks
- Install pi-mono or ollama
- Create local-llm-specialist.sh agent
- Update orchestrator to choose between local/cloud based on complexity
- Test and tune

---

## Data Storage Deep Dive

### Current Architecture

```
~/HomeCare/be-agent-service/
├── .compound-state/              # SESSION STATE (JSON files)
│   └── session-{timestamp}/
│       ├── orchestrator.json     # Orchestrator status, phase
│       ├── backend.json          # Backend specialist state
│       ├── frontend.json         # Frontend specialist state
│       ├── infrastructure.json   # Infrastructure specialist state
│       └── verification.json     # Verification results
│
├── logs/                         # LOG FILES
│   ├── orchestrator-sessions/
│   │   └── session-{timestamp}/
│   │       ├── orchestrator.log
│   │       ├── backend.log
│   │       ├── frontend.log
│   │       └── verification.log
│   ├── auto-compound.log
│   └── compound-review.log
│
└── dashboard/
    └── server.js                 # Reads JSON files from .compound-state/
```

### Why File-Based, Not Database?

**Comparison:**

| Feature | File-Based (Ours) | Database-Backed (Reference Tweet) |
|---------|-------------------|-----------------------------------|
| **Storage** | JSON files in `.compound-state/` | Convex DB |
| **Use case** | Single Mac mini, overnight automation | Multi-user collaboration platform |
| **Concurrency** | One orchestrator at a time | Multiple users/agents simultaneously |
| **Complexity** | Minimal (just read/write files) | Higher (DB setup, schema migrations) |
| **Cost** | Free | Convex DB has free tier, but limits |
| **Speed** | Fast (local disk) | Network latency (hosted DB) |
| **Backup** | Git repo + Time Machine | DB backups required |
| **Best for** | Automation | Collaboration |

**Our choice:** File-based storage is perfect for single-user automation on Mac mini.

### State File Example

```json
// .compound-state/session-1770451234/backend.json
{
  "agentName": "backend",
  "status": "completed",
  "sessionId": "session-1770451234",
  "targetRepo": "/Users/bjornevers_MacPro/HomeCare/beta-appcaire",
  "startTime": "2026-02-07T22:00:00Z",
  "endTime": "2026-02-07T22:15:00Z",
  "completedTasks": [
    {
      "description": "Update Prisma schema with certifications model",
      "file": "apps/dashboard-server/src/schema.prisma",
      "status": "completed"
    },
    {
      "description": "Generate migration",
      "file": "apps/dashboard-server/prisma/migrations/20260207_add_certifications",
      "status": "completed"
    }
  ],
  "artifacts": {
    "schemaUpdated": true,
    "migrationsCreated": ["20260207_add_certifications"],
    "resolversAdded": ["getCertifications", "createCertification"]
  },
  "nextSteps": [
    {
      "agent": "frontend",
      "action": "Run codegen to generate hooks from updated schema",
      "priority": "required",
      "dependencies": ["backend-completed"]
    }
  ]
}
```

### How Dashboard Reads State

**Dashboard Server (`dashboard/server.js`):**

```javascript
function getSessions() {
  // Read all session directories
  const sessionDirs = fs.readdirSync(STATE_DIR)
    .filter(name => name.startsWith('session-'));
  
  return sessionDirs.map(sessionId => {
    const sessionPath = path.join(STATE_DIR, sessionId);
    
    // Read each agent's JSON file
    const orchestrator = JSON.parse(
      fs.readFileSync(path.join(sessionPath, 'orchestrator.json'))
    );
    const backend = JSON.parse(
      fs.readFileSync(path.join(sessionPath, 'backend.json'))
    );
    // etc...
    
    return { sessionId, orchestrator, backend, frontend, verification };
  });
}
```

**Real-time updates:** Dashboard polls `/api/sessions` every 3 seconds to refresh.

### No Convex DB, No PostgreSQL

**What you DON'T need to set up:**
- ❌ Convex DB locally
- ❌ PostgreSQL for agent state
- ❌ Redis for caching
- ❌ MongoDB
- ❌ Any database server

**What you DO need:**
- ✅ File system (already have it!)
- ✅ Node.js (for dashboard server)
- ✅ That's it!

---

## Comparison to Reference Tweet System

**Their system (https://x.com/pbteja1998/status/2017662163540971756):**
- Convex DB for state storage
- Multiple users collaborating
- Real-time chat between agents
- Messages table, agents table, tasks table
- Built for collaboration platform

**Our system (be-agent-service):**
- File-based state storage
- Single user (Product Owner)
- Overnight automation
- State files, log files
- Built for autonomous development

**Key difference:** We don't need the collaboration features (multi-user, real-time chat), so we don't need the database complexity.

---

## Summary

### Pi-Mono
- **Status:** Planned for future (Phase 4-5)
- **Purpose:** Run simple tasks locally (package updates, docs) to reduce API costs
- **Implementation:** 1-2 weeks when we're ready

### Data Storage
- **Method:** File-based JSON storage
- **Location:** `.compound-state/` and `logs/` directories
- **No database:** Not Convex, not PostgreSQL, just files
- **Why:** Perfect for single-user automation on Mac mini

### When to Add Database?

**If you later want to:**
- Share sessions with team members
- Real-time collaboration
- Multi-user dashboard access
- Agent-to-agent real-time chat
- Historical analytics queries

**Then:** Consider adding Convex DB or PostgreSQL.

**For now:** File-based storage is simpler, faster, and sufficient.

---

**Questions?** See `MAC_MINI_SETUP.md` for complete setup guide (no database setup required!).
