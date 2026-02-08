# WHERE IS THE DATA? 📊

**Quick Answer:** There is NO database. All data is stored in **JSON files** on your Mac mini's file system.

---

## 🗂️ Data Storage Architecture

### File-Based Storage (What We Use)

```
~/HomeCare/be-agent-service/
│
├── .compound-state/                    ← SESSION STATE (JSON FILES)
│   ├── session-1707341234/
│   │   ├── orchestrator.json          ← Orchestrator status
│   │   ├── backend.json               ← Backend specialist work
│   │   ├── frontend.json              ← Frontend specialist work
│   │   ├── infrastructure.json        ← Infrastructure updates
│   │   └── verification.json          ← Quality checks
│   │
│   └── session-1707342567/
│       └── ... (another session)
│
├── logs/                               ← LOG FILES
│   ├── orchestrator-sessions/
│   │   └── session-1707341234/
│   │       ├── orchestrator.log
│   │       ├── backend.log
│   │       ├── frontend.log
│   │       └── verification.log
│   │
│   ├── auto-compound.log
│   └── compound-review.log
│
└── dashboard/
    └── server.js                       ← Reads JSON files and serves them as API
```

### OpenClaw & Marketing Data (API-ready)

OpenClaw lead scraper and sample marketing data use `.compound-state/data/`:

```
.compound-state/data/
├── leads.json              ← OpenClaw scraped leads (via /api/data/leads)
├── campaigns.json          ← Marketing campaigns (via /api/data/campaigns)
├── content.json            ← Content pieces (via /api/data/content)
└── social-posts.json       ← Social posts (via /api/data/social)
```

Dashboard serves these via `GET /api/data/leads`, `/api/data/campaigns`, etc.

### Marketing Agent Data (Jarvis/Manual Sessions)

```
~/HomeCare/be-agent-service/
│
├── .compound-state/                    ← MARKETING SESSION STATE
│   └── session-marketing-1707341234/
│       ├── jarvis.json                ← Squad lead coordination
│       ├── shuri.json                 ← Product analysis data
│       ├── fury.json                  ← Customer research data
│       ├── vision.json                ← SEO reports
│       ├── loki.json                  ← Content pieces
│       ├── quill.json                 ← Social media schedules
│       ├── wanda.json                 ← Design assets
│       ├── pepper.json                ← Email campaigns
│       ├── friday.json                ← Landing pages
│       └── wong.json                  ← Notion documentation
│
├── reports/                            ← MARKETING DELIVERABLES
│   ├── seo/
│   │   ├── keyword-research.xlsx
│   │   ├── content-gap-analysis.md
│   │   └── backlink-strategy.pdf
│   │
│   ├── content/
│   │   ├── blog-posts/
│   │   ├── case-studies/
│   │   └── landing-pages/
│   │
│   ├── campaigns/
│   │   ├── email-sequences/
│   │   └── social-calendars/
│   │
│   └── analytics/
│       ├── lead-tracking.json
│       └── campaign-performance.json
│
└── tasks/                              ← TASK TRACKING
    ├── marketing-prd.json
    └── marketing-tasks-{date}.json
```

---

## 💾 NO Database Setup Required

### What You DON'T Need:

- ❌ PostgreSQL installation
- ❌ Convex DB setup
- ❌ MongoDB
- ❌ Redis
- ❌ MySQL
- ❌ Any SQL database
- ❌ Database schema migrations
- ❌ Database backup scripts
- ❌ Database connection configuration

### What You DO Have:

- ✅ JSON files in `.compound-state/`
- ✅ Log files in `logs/`
- ✅ Report files in `reports/`
- ✅ That's it! Simple file system

---

## 🎯 How Dashboard Accesses Data

The dashboard is a **simple Node.js HTTP server** that reads JSON files:

```javascript
// dashboard/server.js

function getSessions() {
  // Read all session directories from disk
  const sessions = fs.readdirSync('.compound-state/')
    .filter(name => name.startsWith('session-'));
  
  return sessions.map(sessionId => {
    // Read each agent's JSON file
    const orchestrator = JSON.parse(
      fs.readFileSync(`.compound-state/${sessionId}/orchestrator.json`)
    );
    const backend = JSON.parse(
      fs.readFileSync(`.compound-state/${sessionId}/backend.json`)
    );
    // etc...
    
    return { sessionId, orchestrator, backend, ... };
  });
}

// Serve as API
app.get('/api/sessions', (req, res) => {
  res.json(getSessions());  // Returns JSON from files
});
```

**That's it!** No database queries, just file system reads.

---

## 📊 Marketing & Sales Data Structure

### Example: Vision (SEO Analyst) State File

**File:** `.compound-state/session-marketing-1707341234/vision.json`

```json
{
  "agentName": "vision",
  "character": "Vision (SEO Analyst)",
  "sessionKey": "agent:seo-analyst:main",
  "status": "completed",
  "sessionId": "session-marketing-1707341234",
  "startTime": "2026-02-07T14:00:00Z",
  "endTime": "2026-02-07T14:45:00Z",
  
  "deliverables": [
    {
      "type": "research",
      "title": "Keyword Research Report",
      "file": "reports/seo/keyword-research-2026-02-07.xlsx",
      "keywords": ["employee scheduling", "workforce management", "care scheduling"],
      "searchVolume": {
        "employee scheduling": 8100,
        "workforce management": 14800,
        "care scheduling": 1900
      },
      "difficulty": {
        "employee scheduling": 72,
        "workforce management": 85,
        "care scheduling": 45
      }
    },
    {
      "type": "analysis",
      "title": "Content Gap Analysis",
      "file": "reports/seo/content-gap-2026-02-07.md",
      "gaps": [
        "No comprehensive guide on scheduling algorithms",
        "Missing comparison pages vs competitors",
        "Lacking industry-specific case studies"
      ],
      "opportunities": [
        {
          "topic": "Scheduling optimization algorithms",
          "estimatedTraffic": 2400,
          "competitorsMissing": 8
        }
      ]
    }
  ],
  
  "metrics": {
    "keywordsResearched": 127,
    "contentGapsIdentified": 15,
    "opportunitiesFound": 23,
    "estimatedMonthlyTraffic": 45600
  },
  
  "nextSteps": [
    {
      "agent": "loki",
      "action": "Write comprehensive guide on scheduling algorithms",
      "priority": "high",
      "keywords": ["scheduling algorithms", "workforce optimization"]
    },
    {
      "agent": "friday",
      "action": "Create landing page for scheduling comparison",
      "priority": "medium"
    }
  ]
}
```

### Example: Pepper (Email Marketing) State File

**File:** `.compound-state/session-marketing-1707341234/pepper.json`

```json
{
  "agentName": "pepper",
  "character": "Pepper Potts (Email Marketing Specialist)",
  "sessionKey": "agent:email-marketing:main",
  "status": "completed",
  
  "campaigns": [
    {
      "name": "Product Launch - Advanced Scheduling",
      "type": "drip-sequence",
      "segments": ["enterprise-leads", "mid-market-trials"],
      "emails": [
        {
          "subject": "Introducing: AI-Powered Scheduling",
          "sendDay": 0,
          "file": "reports/campaigns/email-1-launch.html",
          "cta": "Book Demo"
        },
        {
          "subject": "See How Companies Save 15 Hours/Week",
          "sendDay": 3,
          "file": "reports/campaigns/email-2-case-study.html",
          "cta": "Read Case Study"
        },
        {
          "subject": "Your Exclusive Trial Invitation",
          "sendDay": 7,
          "file": "reports/campaigns/email-3-trial.html",
          "cta": "Start Free Trial"
        }
      ],
      "estimatedReach": 2500,
      "targetConversionRate": 0.15
    }
  ],
  
  "leads": {
    "total": 8742,
    "segments": {
      "enterprise-leads": 1250,
      "mid-market-trials": 3200,
      "small-business": 4292
    },
    "quality": {
      "hot": 350,
      "warm": 2100,
      "cold": 6292
    }
  },
  
  "metrics": {
    "campaignsCreated": 3,
    "emailsWritten": 9,
    "segmentsTargeted": 3,
    "estimatedROI": "320%"
  }
}
```

### Example: Quill (Social Media) State File

**File:** `.compound-state/session-marketing-1707341234/quill.json`

```json
{
  "agentName": "quill",
  "character": "Star-Lord / Peter Quill (Social Media Manager)",
  "sessionKey": "agent:social-media-manager:main",
  "status": "completed",
  
  "socialCalendar": {
    "platform": "LinkedIn + X",
    "startDate": "2026-02-08",
    "endDate": "2026-02-28",
    "posts": [
      {
        "date": "2026-02-08",
        "time": "09:00",
        "platform": "LinkedIn",
        "content": "🚀 Launching our AI-powered scheduling platform! See how care teams are saving 15+ hours per week...",
        "media": ["reports/social/launch-graphic.png"],
        "cta": "Learn More",
        "link": "https://caire.se/launch",
        "hashtags": ["#Healthcare", "#AI", "#Scheduling"]
      },
      {
        "date": "2026-02-10",
        "time": "14:00",
        "platform": "X",
        "content": "Just published: How to optimize employee schedules with AI 🤖\n\nFull guide 👉",
        "link": "https://blog.caire.se/scheduling-optimization",
        "hashtags": ["#WorkforceManagement"]
      }
    ]
  },
  
  "engagement": {
    "estimatedReach": 15000,
    "targetEngagementRate": 0.04,
    "plannedPosts": 21,
    "platforms": ["LinkedIn", "X"]
  }
}
```

---

## 📈 Marketing Dashboard Features

### How to View Marketing Data

**Currently:** Marketing agent state files are created in `.compound-state/session-marketing-*/`

**To view in dashboard:**

1. **Control Tower** → Select "Marketing" team
2. Dashboard reads marketing session files
3. Displays:
   - Active campaigns (Pepper)
   - Social calendar (Quill)
   - SEO opportunities (Vision)
   - Content pipeline (Loki)
   - Leads by segment
   - Campaign performance

### Marketing Data Flow

```
1. Product Owner creates marketing priority
   ↓
2. Jarvis (orchestrator) coordinates specialists
   ↓
3. Each specialist creates deliverables:
   - Vision → SEO reports (reports/seo/)
   - Loki → Blog posts (reports/content/)
   - Pepper → Email campaigns (reports/campaigns/)
   - Quill → Social calendar (reports/social/)
   ↓
4. All data stored in JSON state files
   ↓
5. Dashboard reads JSON files and displays
```

---

## 🔍 Finding Specific Data

### Q: Where are leads stored?

**A:** `.compound-state/session-marketing-*/pepper.json` → `leads` object

```bash
cat .compound-state/session-marketing-*/pepper.json | jq '.leads'
```

### Q: Where is the social media calendar?

**A:** `.compound-state/session-marketing-*/quill.json` → `socialCalendar` object

```bash
cat .compound-state/session-marketing-*/quill.json | jq '.socialCalendar'
```

### Q: Where are email campaigns?

**A:** `.compound-state/session-marketing-*/pepper.json` → `campaigns` array

```bash
cat .compound-state/session-marketing-*/pepper.json | jq '.campaigns'
```

### Q: Where is SEO research?

**A:** `.compound-state/session-marketing-*/vision.json` → `deliverables` array

```bash
cat .compound-state/session-marketing-*/vision.json | jq '.deliverables'
```

---

## 💡 Why File-Based vs Database?

### File-Based (What We Use) ✅

**Pros:**
- ✅ Zero setup (no database installation)
- ✅ Git-friendly (can commit state files)
- ✅ Easy backup (just copy directory)
- ✅ Simple debugging (just cat files)
- ✅ No connection issues
- ✅ Works offline
- ✅ Perfect for single-user automation

**Cons:**
- ❌ Not suitable for real-time collaboration
- ❌ No complex queries (but we don't need them)
- ❌ Limited to one orchestrator at a time

### Database (What Others Use) 

**Pros:**
- ✅ Multi-user collaboration
- ✅ Complex queries
- ✅ Real-time updates across users
- ✅ Transactions and ACID guarantees

**Cons:**
- ❌ Requires setup (PostgreSQL, Convex, etc.)
- ❌ Connection overhead
- ❌ Backup complexity
- ❌ Needs migrations
- ❌ Overkill for single-user automation

---

## 📝 Summary

### Your Questions Answered:

**Q: "where is the db for all the data?"**  
**A:** There is no database. All data is in JSON files in `.compound-state/` directory.

**Q: "how is marketing and sales showing leads and research?"**  
**A:** Each marketing agent writes JSON files with structured data:
- `pepper.json` has leads and campaigns
- `vision.json` has SEO research
- `quill.json` has social calendar
- `fury.json` has customer research

**Q: "where is the db?"**  
**A:** No database exists. Dashboard reads files from disk using Node.js `fs.readFileSync()`.

### Data Locations Quick Reference:

| Data Type | Location | Format |
|-----------|----------|--------|
| **Session State** | `.compound-state/session-*/` | JSON files |
| **OpenClaw Leads** | `.compound-state/data/leads.json` | JSON |
| **Marketing Data** | `.compound-state/data/{campaigns,content,social-posts}.json` | JSON |
| **Logs** | `logs/orchestrator-sessions/` | Plain text |
| **Marketing Leads (Jarvis)** | `.compound-state/session-marketing-*/pepper.json` | JSON |
| **Email Campaigns (Jarvis)** | `.compound-state/session-marketing-*/pepper.json` | JSON |
| **Social Calendar (Jarvis)** | `.compound-state/session-marketing-*/quill.json` | JSON |
| **SEO Reports** | `.compound-state/session-marketing-*/vision.json` + `reports/seo/` | JSON + Files |
| **Content** | `reports/content/` | Markdown/HTML files |
| **Analytics** | `reports/analytics/` | JSON files |

---

**TL;DR:** Everything is just files on disk. No database. Simple and works perfectly for overnight automation on Mac mini! 🎉
