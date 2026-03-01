# Marketing Agents - Marvel Squad

Multi-agent marketing orchestration system with Marvel character personalities.

---

## Quick Start

### Run Marketing Orchestrator

```bash
# Create marketing priority file
cat > ~/HomeCare/beta-appcaire/reports/marketing-blog-post.md <<EOF
# Priority: SEO Blog Post

**Description:** Create SEO-optimized blog post about employee scheduling

**Expected outcome:**
- Keyword research completed
- Blog post written (1500+ words)
- Header image created
- Published to website
- Promoted on social media

**Complexity:** Medium
EOF

# Run Jarvis orchestrator
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  reports/marketing-blog-post.md \
  tasks/marketing-prd.json \
  feature/blog-post-scheduling
```

---

## Available Agents

| Agent | Character | Role | Session Key |
|-------|-----------|------|-------------|
| **Jarvis** | J.A.R.V.I.S. | Squad Lead Orchestrator | `agent:main:main` |
| **Shuri** | Shuri | Product Analyst | `agent:product-analyst:main` |
| **Fury** | Nick Fury | Customer Researcher | `agent:customer-researcher:main` |
| **Vision** | Vision | SEO Analyst | `agent:seo-analyst:main` |
| **Loki** | Loki | Content Writer | `agent:content-writer:main` |
| **Quill** | Star-Lord | Social Media Manager | `agent:social-media-manager:main` |
| **Wanda** | Scarlet Witch | Designer | `agent:designer:main` |
| **Pepper** | Pepper Potts | Email Marketing | `agent:email-marketing:main` |
| **Friday** | F.R.I.D.A.Y. | Developer | `agent:developer:main` |
| **Wong** | Wong | Notion Agent | `agent:notion-agent:main` |

---

## Workflow Phases

### Phase 1: Research (Parallel)
Agents that can run simultaneously:
- **Shuri** - Product analysis
- **Fury** - Customer research
- **Vision** - SEO research

### Phase 2: Content Creation (Sequential)
Waits for research data:
- **Loki** - Content writing
- **Pepper** - Email campaigns

### Phase 3: Design & Technical (Parallel)
Visual and technical implementation:
- **Wanda** - Visual design
- **Friday** - Website implementation

### Phase 4: Distribution (Sequential)
Promotion and documentation:
- **Quill** - Social media promotion
- **Wong** - Process documentation

---

## State Management

Each agent writes state to `.compound-state/session-marketing-X/`:

```json
{
  "agentName": "vision",
  "character": "Vision (SEO Analyst)",
  "sessionKey": "agent:seo-analyst:main",
  "domain": "marketing",
  "role": "SEO Analyst",
  "status": "completed",
  "completedTasks": [...],
  "deliverables": [...],
  "messages": [
    {
      "to": "loki",
      "content": "Target keyword: 'employee scheduling software'",
      "timestamp": "2026-02-07T14:30:00Z"
    }
  ],
  "soul": {
    "personality": "Analytical, precise, pattern-focused",
    "learnings": [...]
  }
}
```

---

## Inter-Agent Communication

Agents communicate via JSON state files:

```json
{
  "messages": [
    {
      "to": "loki",
      "content": "Product positioning complete. Use message: 'Fastest scheduler for care teams'",
      "timestamp": "2026-02-07T14:30:00Z",
      "attachments": ["reports/positioning.md"]
    }
  ]
}
```

---

## Dashboard Integration

Marketing agents appear in dashboard at http://localhost:3010

**View session state:**
```bash
GET /api/sessions/session-marketing-123
```

**Response:**
```json
{
  "sessionId": "session-marketing-123",
  "agents": {
    "jarvis": {...},
    "vision": {...},
    "loki": {...},
    "wanda": {...}
  }
}
```

---

## Example: Blog Post Creation

**Priority:** Create SEO blog post

**Agents activated:**
1. **Vision** - Keyword research (Phase 1)
2. **Shuri** - Product angle (Phase 1)
3. **Fury** - Customer pain points (Phase 1)
4. **Loki** - Write blog post (Phase 2)
5. **Wanda** - Header image (Phase 3)
6. **Friday** - Publish to site (Phase 3)
7. **Quill** - Social promotion (Phase 4)
8. **Wong** - Document process (Phase 4)

**Timeline:**
- **0:00** - Jarvis analyzes priority
- **0:01** - Phase 1 starts (Vision, Shuri, Fury run in parallel)
- **0:10** - Phase 1 complete
- **0:11** - Phase 2 starts (Loki writes content)
- **0:25** - Phase 2 complete
- **0:26** - Phase 3 starts (Wanda + Friday run in parallel)
- **0:35** - Phase 3 complete
- **0:36** - Phase 4 starts (Quill, Wong run sequentially)
- **0:45** - All agents complete

**Total time:** 45 minutes
**PR created:** `feature/blog-post-scheduling` → main

---

## Extending the System

### Add New Marketing Agent

1. Create agent script in `agents/marketing/`
2. Create prompt in `agents/prompts/` (see `agents/prompts/README.md` for lookup order)
3. Add entry to `AGENT_TO_FILES` in `apps/server/src/routes/file.ts` and add agent to DB (e.g. `schema.sql`)
4. Update AGENTS_REGISTRY.md
5. Test individual agent and orchestrated workflow

### Add New Marketing Domain

Example: Add "webinars" domain

1. Create `agents/marketing/webinar-specialist.sh`
2. Add to Jarvis orchestrator
3. Create priority template for webinars
4. Test workflow

---

## Files

```
agents/marketing/
├── README.md                      # This file
├── AGENTS_REGISTRY.md             # Full agent details (all 10 agents)
├── jarvis-orchestrator.sh         # Squad lead orchestrator
├── vision-seo-analyst.sh          # SEO specialist
├── shuri-product-analyst.sh       # Product analyst
├── fury-customer-researcher.sh    # Customer researcher
├── loki-content-writer.sh         # Content writer
├── quill-social-media.sh         # Social media manager
├── wanda-designer.sh              # Designer
├── pepper-email-marketing.sh      # Email marketing
├── friday-developer.sh            # Developer
└── wong-notion-agent.sh           # Notion agent

agents/prompts/                   # System prompts (souls) for all agents
├── jarvis-orchestrator.md
├── vision-seo-analyst.md
├── shuri-product-analyst.md
├── fury-customer-researcher.md
├── loki-content-writer.md
├── quill-social-media.md
├── wanda-designer.md
├── pepper-email-marketing.md
├── friday-developer.md
└── wong-notion-agent.md
```

---

## Comparison to Engineering Agents

| Feature | Engineering Agents | Marketing Agents |
|---------|-------------------|------------------|
| **Domain** | Code, DB, Infrastructure | Content, SEO, Design |
| **Orchestrator** | orchestrator.sh | jarvis-orchestrator.sh |
| **Agents** | 10 (orchestrator + 9 specialists) | 10 (Jarvis + 9 specialists) |
| **Personalities** | Functional | Marvel characters |
| **Parallel execution** | ✅ Backend + Infra | ✅ Research agents |
| **Verification** | ✅ Type-check, build | TBD (content quality) |
| **Storage** | ✅ File-based JSON | ✅ File-based JSON |
| **Dashboard** | ✅ Shared | ✅ Shared |

---

## Next Steps

1. Test individual agents and full orchestration
2. Enhance dashboard for marketing-specific view
3. Add to nightly automation (optional)
4. Create marketing priority templates

---

See **AGENTS_REGISTRY.md** for full agent details. For repo-wide agent/team count (4 teams, 27 agents), see root **README.md** and **docs/AGENTS_AND_TEAMS_DATA.md**.
