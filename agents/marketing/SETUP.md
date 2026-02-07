# Marketing Agents Setup Guide

## Overview
The marketing agent system automates lead generation, research, content creation, and social media management for AppCaire.

## Quick Start

### 1. Configure Environment Variables
```bash
cd ~/HomeCare/be-agent-service
cp .env.template .env
# Edit .env with your actual credentials
```

### 2. Install Dependencies (if needed)
```bash
# For email scraping (OpenClaw)
npm install openclaw

# For social media APIs
npm install twitter-api-v2 linkedin-api
```

### 3. Test Individual Agents
```bash
# Test lead scraper
./agents/marketing/openclaw-lead-scraper.sh

# Test researcher
./agents/marketing/fury-researcher.sh

# Test other agents
./agents/marketing/shuri-analyst.sh
./agents/marketing/pepper-email.sh
./agents/marketing/quill-social.sh
./agents/marketing/loki-content.sh
```

### 4. Enable Automated Wake-Up Schedule (Optional)
```bash
# Load launchd plist for 15-minute interval
cp launchd/com.appcaire.marketing-agents.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.appcaire.marketing-agents.plist

# Enable it (edit plist and set Disabled to false)
# Then reload
launchctl unload ~/Library/LaunchAgents/com.appcaire.marketing-agents.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.marketing-agents.plist
```

### 5. View in Command Center
```bash
# Start dashboard server
cd dashboard
node server.js

# Open in browser
open http://localhost:3030/command-center.html
```

## Agent Roles

### 🔍 OpenClaw Lead Scraper
**Purpose:** Scan email inbox for leads
**Triggers:** Keywords like "interested", "pricing", "demo", "trial"
**Output:** Writes to `.compound-state/data/leads.json`
**Status:** Template (needs OpenClaw integration)

### 👁️ Fury - Customer Researcher
**Purpose:** Research company details for new leads
**Actions:**
- Web search for company info
- Determine industry, size, location
- Calculate lead score
- Assign to campaigns

**Status:** Template (needs Claude API integration)

### 👩‍🔬 Shuri - Product Fit Analyst
**Purpose:** Analyze leads for product fit
**Actions:**
- Recommend product tier (Starter/Pro/Enterprise)
- Identify relevant features
- Generate sales talking points

**Status:** Template (needs implementation)

### 💼 Pepper - Email Marketing
**Purpose:** Generate personalized email drafts
**Actions:**
- Create subject line variants
- Personalize email content
- Add relevant CTAs
- Save drafts to content.json

**Status:** Template (needs implementation)

### 🎸 Quill - Social Media
**Purpose:** Monitor social channels and create posts
**Actions:**
- Track Twitter mentions
- Monitor LinkedIn engagement
- Generate response drafts
- Schedule posts

**Status:** Template (needs Twitter/LinkedIn API integration)

### ✍️ Loki - Content Writer
**Purpose:** Generate blog posts and long-form content
**Actions:**
- Extract pain points from leads
- Create SEO-optimized content
- Write case studies
- Draft thought leadership pieces

**Status:** Template (needs Claude API integration)

## Data Flow

```
Email Inbox
    ↓
[OpenClaw Scraper] → leads.json
    ↓
[Fury Research] → Enhanced lead data
    ↓
[Shuri Analysis] → Product fit recommendations
    ↓
[Pepper Email] → Email drafts in content.json
    ↓
[Quill Social] → Social posts in social-posts.json
    ↓
[Loki Content] → Blog posts in content.json
    ↓
Command Center UI
```

## Viewing Results

### Command Center Dashboard
1. Navigate to http://localhost:3030/command-center.html
2. Click **Data** tab
3. Click **Marketing** sub-tab
4. View:
   - Campaigns grid
   - Leads grid
   - Content grid
   - Social posts grid
5. Click any card to see details in modal

### Raw Data Files
- Campaigns: `.compound-state/data/campaigns.json`
- Leads: `.compound-state/data/leads.json`
- Content: `.compound-state/data/content.json`
- Social: `.compound-state/data/social-posts.json`

## Current Status

### ✅ Complete
- Directory structure
- Sample data (5 campaigns, 10 leads, 10 content pieces, 10 social posts)
- API endpoints in server.js
- UI integration in Command Center
- Agent script templates
- Launchd plist for scheduling
- .env template

### 🚧 To Implement
- OpenClaw email integration
- Claude API calls for research/analysis
- Twitter/LinkedIn API integration
- Notion API integration (Wong agent)
- Actual email sending capability

## Next Steps

1. **Set up credentials** in .env file
2. **Test individual agents** manually
3. **Implement OpenClaw** email scraping
4. **Add Claude API calls** for research agents
5. **Integrate social APIs** for Quill
6. **Enable launchd** for automatic running
7. **Monitor logs** in logs/marketing-agents.log

## Security Notes

- ⚠️ Never commit .env file to git
- ⚠️ Use app-specific passwords for email
- ⚠️ Read-only access for initial implementation
- ⚠️ Review all generated content before publishing

## Troubleshooting

### Agents not running
Check launchd status:
```bash
launchctl list | grep appcaire
```

### No leads appearing
- Check .env email credentials
- Verify OpenClaw is installed
- Check logs: `tail -f logs/marketing-agents.log`

### Command Center not showing data
- Verify server is running: http://localhost:3030
- Check data files exist in `.compound-state/data/`
- Check browser console for errors

## Support

For questions or issues:
1. Check logs in `logs/marketing-agents.log`
2. Review agent script output
3. Verify .env configuration
4. Test API endpoints directly
