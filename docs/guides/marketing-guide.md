# Marketing Commands & Guide

Complete reference for marketing team operations and commands.

---

## Table of Contents

1. [Marketing Agents](#marketing-agents)
2. [Running Campaigns](#running-campaigns)
3. [Common Commands](#common-commands)
4. [Campaign Types](#campaign-types)
5. [Agent Communication](#agent-communication)
6. [Best Practices](#best-practices)

---

## Marketing Agents

### The Marketing Avengers Squad

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

### Agent Personalities

Each agent has a Marvel character personality that influences their behavior:

- **Jarvis**: Sophisticated, analytical coordinator
- **Shuri**: Brilliant, innovative, data-driven
- **Fury**: Strategic, paranoid, thorough researcher
- **Vision**: Analytical, precise, pattern-focused
- **Loki**: Witty, creative, master storyteller
- **Quill**: Charismatic, spontaneous, trend-aware
- **Wanda**: Creative, emotional, beautiful designs
- **Pepper**: Organized, professional, on-time delivery
- **Friday**: Efficient, technical, automation-first
- **Wong**: Meticulous, organized, documentation guardian

---

## Running Campaigns

### Via Dashboard

**Go to**: http://localhost:3030/sales-marketing.html

**Steps:**
1. Select model (usually Sonnet for cost-effectiveness)
2. Enter campaign file: `reports/marketing-campaign-Q1.md`
3. Enter branch: `feature/q1-campaign`
4. Describe objectives (optional)
5. Click "Start Marketing Campaign"

**Monitor:**
- Active Campaigns section
- Recent Leads
- Social Posts
- Agent status indicators

### Via CLI

```bash
cd ~/HomeCare/be-agent-service

# Run Jarvis marketing orchestrator
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-blog-post.md \
  ~/HomeCare/beta-appcaire/tasks/marketing-prd.json \
  feature/blog-post-scheduling
```

### Run Individual Agent

```bash
cd ~/HomeCare/be-agent-service

# Run Vision (SEO analyst) only
./agents/marketing/vision-seo-analyst.sh \
  "session-seo-$(date +%s)" \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-priority.md

# View results
cat .compound-state/session-seo-*/vision.json | jq '.deliverables'
```

---

## Common Commands

### Campaign Creation

```bash
cd ~/HomeCare/beta-appcaire

# Create SEO blog post campaign
cat > reports/marketing-blog-post.md <<'EOF'
# Priority: SEO Blog Post

**Description:** Create SEO-optimized blog post about employee scheduling

**Expected outcome:**
- Keyword research (target keywords with volume/difficulty)
- Product positioning analysis
- Customer pain points identified
- Blog post written (1500+ words, SEO-optimized)
- Header image created
- Published to website
- Promoted on social media

**Complexity:** Medium
EOF

# Create social media campaign
cat > reports/marketing-social-campaign.md <<'EOF'
# Priority: Social Media Campaign

**Description:** Launch Q1 product awareness campaign

**Expected outcome:**
- Content calendar for 30 days
- 15 social posts created
- Images/graphics designed
- Scheduled across platforms
- Analytics tracking setup

**Complexity:** Medium
EOF

# Create email campaign
cat > reports/marketing-email-campaign.md <<'EOF'
# Priority: Email Nurture Campaign

**Description:** Create 5-part email nurture sequence

**Expected outcome:**
- Email sequence designed
- Copy written for all 5 emails
- Templates created
- Segmentation strategy defined
- Automation workflow setup

**Complexity:** Medium
EOF
```

### Session Management

```bash
cd ~/HomeCare/be-agent-service

# List marketing sessions
ls -la .compound-state/ | grep marketing

# View Jarvis orchestrator state
cat .compound-state/session-marketing-*/jarvis.json | jq '.'

# View specific agent state
cat .compound-state/session-marketing-*/vision.json | jq '.'
cat .compound-state/session-marketing-*/loki.json | jq '.'
cat .compound-state/session-marketing-*/wanda.json | jq '.'

# View agent messages
cat .compound-state/session-marketing-*/vision.json | jq '.messages'
```

### Monitoring Progress

```bash
# Check agent status
cat .compound-state/session-marketing-*/vision.json | jq '.status'

# View completed tasks
cat .compound-state/session-marketing-*/loki.json | jq '.completedTasks'

# View deliverables
cat .compound-state/session-marketing-*/vision.json | jq '.deliverables'

# Monitor in dashboard
open http://localhost:3030/sales-marketing.html
```

---

## Campaign Types

### 1. SEO Blog Post Campaign

**Agents involved:**
1. **Vision** - Keyword research (Phase 1)
2. **Shuri** - Product angle (Phase 1)
3. **Fury** - Customer pain points (Phase 1)
4. **Loki** - Write blog post (Phase 2)
5. **Wanda** - Header image (Phase 3)
6. **Friday** - Publish to site (Phase 3)
7. **Quill** - Social promotion (Phase 4)
8. **Wong** - Document process (Phase 4)

**Timeline:** ~45 minutes
**Deliverables:**
- Keyword research report
- 1500+ word blog post
- Header image
- Published page
- Social media posts
- Process documentation

### 2. Social Media Campaign

**Agents involved:**
1. **Fury** - Audience research (Phase 1)
2. **Loki** - Content ideas (Phase 2)
3. **Wanda** - Graphics creation (Phase 3)
4. **Quill** - Post scheduling (Phase 4)
5. **Wong** - Document strategy (Phase 4)

**Timeline:** ~30 minutes
**Deliverables:**
- Audience insights
- 30-day content calendar
- 15 social posts with graphics
- Scheduling setup
- Strategy documentation

### 3. Email Campaign

**Agents involved:**
1. **Fury** - Customer segments (Phase 1)
2. **Shuri** - Product positioning (Phase 1)
3. **Loki** - Email copy (Phase 2)
4. **Wanda** - Email templates (Phase 3)
5. **Pepper** - Campaign setup (Phase 4)
6. **Friday** - Automation (Phase 4)

**Timeline:** ~40 minutes
**Deliverables:**
- Segmentation strategy
- 5 emails written
- Email templates
- Campaign configured
- Automation workflows

### 4. Product Launch

**Agents involved:**
All 10 agents across all phases

**Timeline:** ~90 minutes
**Deliverables:**
- Market research
- Product positioning
- Launch plan
- Landing page
- Blog posts
- Email sequences
- Social campaigns
- PR strategy

---

## Agent Communication

### Inter-Agent Messaging

Agents communicate via JSON state files:

```json
{
  "agentName": "vision",
  "messages": [
    {
      "to": "loki",
      "content": "Target keyword: 'employee scheduling software' (volume: 5,400/mo, difficulty: 35)",
      "timestamp": "2026-02-08T14:30:00Z",
      "attachments": ["reports/keyword-research.xlsx"]
    }
  ]
}
```

### Task Handoffs

When one agent completes work that enables another:

```json
{
  "agentName": "shuri",
  "completedTasks": [
    {
      "id": "product-1",
      "description": "Product positioning complete"
    }
  ],
  "nextSteps": [
    {
      "agent": "loki",
      "action": "Write blog post using positioning: 'Fastest scheduler for care teams'",
      "priority": "required"
    }
  ]
}
```

### Workflow Phases

**Phase 1: Research (Parallel)**
```
Vision + Shuri + Fury run simultaneously
↓
All complete before Phase 2 starts
```

**Phase 2: Content Creation (Sequential)**
```
Loki waits for research
↓
Writes content using insights
↓
Pepper creates email campaigns
```

**Phase 3: Design & Technical (Parallel)**
```
Wanda + Friday run simultaneously
↓
Visual and technical implementation
```

**Phase 4: Distribution (Sequential)**
```
Quill promotes on social
↓
Wong documents process
```

---

## Best Practices

### Campaign Planning

**Do:**
- ✅ Be specific about target audience
- ✅ Define clear metrics for success
- ✅ Include brand guidelines
- ✅ Set realistic timelines
- ✅ Specify distribution channels

**Don't:**
- ❌ Be vague ("Create content")
- ❌ Skip audience definition
- ❌ Forget brand voice guidelines
- ❌ Combine multiple campaigns
- ❌ Ignore channel specifications

### Campaign File Format

```markdown
# Priority: [Campaign Name]

**Description:** [Clear campaign description]

**Target audience:**
- [Persona 1]
- [Persona 2]

**Expected outcome:**
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

**Brand voice:** [Professional/Casual/Technical]

**Channels:**
- [LinkedIn/Twitter/Email/Blog]

**Success metrics:**
- [Metric 1: Target]
- [Metric 2: Target]

**Complexity:** Low | Medium | High
```

### SEO Content Best Practices

**For Vision (SEO):**
- Research high-volume, low-difficulty keywords
- Analyze top-ranking content
- Identify content gaps
- Provide clear keyword targets

**For Loki (Content):**
- Use target keywords naturally
- Write 1500+ words for SEO
- Include internal links
- Optimize headings (H1, H2, H3)
- Add meta description

**For Friday (Dev):**
- Implement proper URL structure
- Add meta tags
- Setup schema markup
- Ensure fast load times

### Social Media Best Practices

**For Quill (Social):**
- Post at optimal times
- Use platform-specific formats
- Include hashtags (3-5 per post)
- Engage with comments
- Track analytics

**For Wanda (Design):**
- Follow platform dimensions
- Maintain brand consistency
- Use eye-catching visuals
- Include CTA in images

---

## Command Reference

### Campaign Management

```bash
# Create campaign file
vim ~/HomeCare/beta-appcaire/reports/marketing-campaign.md

# Run campaign
cd ~/HomeCare/be-agent-service
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  reports/marketing-campaign.md \
  tasks/marketing-prd.json \
  feature/campaign

# Monitor progress
cat .compound-state/session-marketing-*/jarvis.json | jq '.status'

# View results
cat .compound-state/session-marketing-*/jarvis.json | jq '.deliverables'
```

### Individual Agent Commands

```bash
cd ~/HomeCare/be-agent-service

# SEO analysis
./agents/marketing/vision-seo-analyst.sh "session-seo-$(date +%s)" \
  ~/HomeCare/beta-appcaire reports/marketing-blog.md

# Product analysis (when implemented)
./agents/marketing/shuri-product-analyst.sh "session-product-$(date +%s)" \
  ~/HomeCare/beta-appcaire reports/marketing-blog.md

# Customer research (when implemented)
./agents/marketing/fury-customer-researcher.sh "session-customer-$(date +%s)" \
  ~/HomeCare/beta-appcaire reports/marketing-blog.md
```

### Dashboard API

```bash
# Get marketing agents status
curl http://localhost:3030/api/agents?domain=marketing

# Get campaign status
curl http://localhost:3030/api/jobs?type=marketing

# Get recent leads
curl http://localhost:3030/api/leads

# Get social posts
curl http://localhost:3030/api/social-posts
```

---

## Workflow Example

### Creating an SEO Blog Post

**Step 1: Create Priority File**
```bash
cat > ~/HomeCare/beta-appcaire/reports/marketing-blog-scheduling.md <<'EOF'
# Priority: SEO Blog Post - Employee Scheduling

**Description:** Create comprehensive blog post about employee scheduling for care agencies

**Target audience:**
- Care agency owners
- HR managers
- Operations directors

**Expected outcome:**
- Keyword research targeting "employee scheduling for care agencies"
- Blog post 1500+ words
- Header image created
- Published to website
- Promoted on LinkedIn

**Brand voice:** Professional, helpful, authoritative

**Channels:**
- Blog
- LinkedIn
- Newsletter

**Success metrics:**
- 1000+ views in first month
- 50+ newsletter signups

**Complexity:** Medium
EOF
```

**Step 2: Run Campaign**
```bash
cd ~/HomeCare/be-agent-service
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  reports/marketing-blog-scheduling.md \
  tasks/marketing-prd.json \
  feature/blog-scheduling
```

**Step 3: Monitor Progress**
```bash
# In dashboard
open http://localhost:3030/sales-marketing.html

# Or via CLI
watch -n 3 'cat .compound-state/session-marketing-*/jarvis.json | jq ".status"'
```

**Step 4: Review Deliverables**
```bash
# View all deliverables
cat .compound-state/session-marketing-*/jarvis.json | jq '.deliverables'

# Check blog post
cat ~/HomeCare/beta-appcaire/marketing/blog/employee-scheduling.md

# Check keyword research
cat ~/HomeCare/beta-appcaire/marketing/research/keyword-analysis.xlsx
```

**Step 5: Review PR**
```bash
gh pr list
gh pr view [NUMBER]
gh pr merge [NUMBER] --squash
```

---

## Troubleshooting

### Campaign Stuck?

```bash
# Check Jarvis orchestrator state
cat .compound-state/session-marketing-*/jarvis.json | jq '.status'

# Check individual agent states
cat .compound-state/session-marketing-*/vision.json | jq '.status'
cat .compound-state/session-marketing-*/loki.json | jq '.status'

# Check for blockers
cat .compound-state/session-marketing-*/jarvis.json | jq '.blockers'
```

### Agent Failed?

```bash
# View agent logs
tail -50 logs/marketing-sessions/session-*/vision.log

# Check error messages
cat .compound-state/session-marketing-*/vision.json | jq '.errors'

# Re-run individual agent
./agents/marketing/vision-seo-analyst.sh "retry-$(date +%s)" \
  ~/HomeCare/beta-appcaire reports/marketing-blog.md
```

### Missing Deliverables?

```bash
# Check what was completed
cat .compound-state/session-marketing-*/jarvis.json | jq '.completedTasks'

# Check agent deliverables
cat .compound-state/session-marketing-*/loki.json | jq '.deliverables'

# Verify files created
ls -la ~/HomeCare/beta-appcaire/marketing/
```

---

For more details:
- [PO Workflow Guide](po-workflow.md)
- [Quick Start Guide](quick-start.md)
- [Agents Reference](../reference/agents.md)
