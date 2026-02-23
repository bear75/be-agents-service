# Email Lead Scraping Setup Guide

## Quick Start

OpenClaw can monitor your business emails to automatically capture leads from:
- Contact form submissions forwarded to email
- Direct inquiries (info@, contact@, hello@)
- Demo requests
- Pricing inquiries
- Support emails from prospects

## Recommended Email Setup

### Full Multi-Domain Configuration (Recommended)
Monitor all business emails across all properties:

```bash
cp .env.template .env
# Configure all 9 email addresses:

# CAIRE.SE (AppCaire main product)
EMAIL_1_USER=sales@caire.se
EMAIL_1_PASSWORD=app-password-1

EMAIL_2_USER=info@caire.se
EMAIL_2_PASSWORD=app-password-2

EMAIL_3_USER=bjorn@caire.se
EMAIL_3_PASSWORD=app-password-3

# EIRTECH.AI (Ireland/EU market)
EMAIL_4_USER=sales@eirtech.ai
EMAIL_4_PASSWORD=app-password-4

EMAIL_5_USER=info@eirtech.ai
EMAIL_5_PASSWORD=app-password-5

EMAIL_6_USER=bjorn@eirtech.ai
EMAIL_6_PASSWORD=app-password-6

# NACKAHEMTJANST.SE (Nacka local market)
EMAIL_7_USER=sales@nackahemtjanst.se
EMAIL_7_PASSWORD=app-password-7

EMAIL_8_USER=info@nackahemtjanst.se
EMAIL_8_PASSWORD=app-password-8

EMAIL_9_USER=bjorn@nackahemtjanst.se
EMAIL_9_PASSWORD=app-password-9
```

**Why monitor all addresses?**
- **sales@** - Direct sales inquiries (usually highest intent)
- **info@** - General inquiries (mix of leads and support)
- **bjorn@** - Personal inquiries (often high-value partnerships)

**Lead source attribution:**
- Each email tracked separately in dashboard
- See which domain generates most leads (caire.se vs eirtech.ai vs nackahemtjanst.se)
- Identify best-performing email address (sales@ vs info@)

## Gmail App Password Setup

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Mac"
3. Click "Generate"
4. Copy the 16-character password
5. Paste into `.env` file (no spaces)

### Step 3: Test Connection
```bash
# Test email access
curl -u "info@caire.se:your-app-password" \
  "imaps://imap.gmail.com:993/INBOX?UNSEEN"
```

## Microsoft 365 / Outlook Setup

For `@caire.se` if using Microsoft 365:

```bash
EMAIL_IMAP_HOST=outlook.office365.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_HOST=smtp.office365.com
EMAIL_SMTP_PORT=587
```

1. Go to https://account.microsoft.com/security
2. Enable "App passwords"
3. Generate password for "Mail app"

## Custom Domain Setup

If your emails are hosted elsewhere:

```bash
# Find your IMAP settings from your email provider
EMAIL_IMAP_HOST=mail.yourdomain.com
EMAIL_IMAP_PORT=993  # Usually 993 for SSL
```

Common providers:
- **Gmail (Google Workspace):** `imap.gmail.com:993`
- **Microsoft 365:** `outlook.office365.com:993`
- **Apple iCloud:** `imap.mail.me.com:993`
- **Proton Mail:** Not supported (no IMAP for free tier)

## Lead Detection Keywords

OpenClaw searches for these keywords to identify potential leads:

```bash
EMAIL_LEAD_KEYWORDS=demo,trial,pricing,contact,inquiry,interested,quote,schedule,partnership,integration
```

**High-value keywords (score boost):**
- "demo", "trial" → Qualified lead (score: 85+)
- "pricing", "quote" → Hot lead (score: 90+)
- "partnership", "integration" → Enterprise lead (score: 95+)

**Medium keywords:**
- "interested", "learn more" → Warm lead (score: 60-75)

**Low keywords:**
- "question", "help", "support" → General inquiry (score: 40-50)

## Running OpenClaw

### Prerequisites

OpenClaw requires `jq` for JSON processing:
```bash
# Check if jq is installed
which jq

# Install if needed
brew install jq
```

### Manual Test
```bash
cd ~/HomeCare/be-agents-service

# First-time setup: Copy and configure .env
cp .env.template .env
vim .env  # Add your email app passwords

# Run the scraper
./agents/marketing/openclaw-lead-scraper.sh
```

**Expected output:**
```
[2026-02-07 16:30:45] 📧 OpenClaw Lead Scraper Starting...
[2026-02-07 16:30:45] Checking sales@caire.se...
[2026-02-07 16:30:46]   No unread emails
[2026-02-07 16:30:46] Checking info@caire.se...
[2026-02-07 16:30:47]   Found unread emails: 1234 1235
[2026-02-07 16:30:48]     ✅ New lead: Sarah Johnson (sarah@sunrisehc.com) - Score: 85
[2026-02-07 16:30:49] 📊 Lead Statistics:
[2026-02-07 16:30:49] Total leads: 1
[2026-02-07 16:30:49] New leads this run: 1
[2026-02-07 16:30:49] ✅ Lead scraper completed
```

### Automatic (Every 15 Minutes)

**Install launchd job:**
```bash
cd ~/HomeCare/be-agents-service

# Copy plist to LaunchAgents
cp com.appcaire.openclaw.plist ~/Library/LaunchAgents/

# Load the job
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist

# Verify it's loaded
launchctl list | grep openclaw
```

**Monitor activity:**
```bash
# View logs
tail -f logs/openclaw.log

# View live lead count
watch -n 5 'cat .compound-state/data/leads.json | jq "length"'

# View latest leads
cat .compound-state/data/leads.json | jq '.[-5:] | .[] | {name, email, score, status}'
```

**Stop Automatic Scraping:**
```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

**Restart after .env changes:**
```bash
# Unload
launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist

# Reload
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

## How OpenClaw Works

OpenClaw uses IMAP (via curl) to monitor all 9 configured email accounts:

1. **Connect to IMAP** - Loops through EMAIL_1_USER through EMAIL_9_USER
2. **Search for unread emails** - Uses IMAP SEARCH UNSEEN command
3. **Keyword filtering** - Checks if email contains any lead keywords
4. **Extract contact info** - Parses sender name, email, company from domain
5. **Score the lead** - Calculates score based on keywords, domain, and content
6. **Save to leads.json** - Appends new lead with all extracted data
7. **Mark as read** - Sets IMAP \\Seen flag to avoid reprocessing

**IMAP Commands Used:**
```bash
# Search for unread emails
curl "imaps://imap.gmail.com:993/INBOX" \
  --user "info@caire.se:app-password" \
  -X "SEARCH UNSEEN"

# Fetch email content
curl "imaps://imap.gmail.com:993/INBOX;UID=1234" \
  --user "info@caire.se:app-password"

# Mark as read
curl "imaps://imap.gmail.com:993/INBOX;UID=1234" \
  --user "info@caire.se:app-password" \
  -X "STORE 1234 +FLAGS \\Seen"
```

**Lead Attribution:**
Each lead is tagged with its source email:
- `source: "email-sales@caire.se"` → Sales inquiry
- `source: "email-info@eirtech.ai"` → EU market inquiry
- `source: "email-bjorn@nackahemtjanst.se"` → Local/personal inquiry

This allows you to track which email address generates the most qualified leads.

## What Gets Extracted

For each email, OpenClaw extracts:

```json
{
  "id": "lead-1707331234",
  "source": "email-info@caire.se",
  "status": "new",
  "company": "Sunrise Home Care",
  "contactName": "Sarah Johnson",
  "email": "sarah@sunrisehc.com",
  "phone": "+1-555-0123",
  "createdAt": "2026-02-07T16:20:34Z",
  "assignedTo": "fury",
  "score": 85,
  "notes": "Interested in demo. Currently using Excel for scheduling. 15 employees.",
  "originalSubject": "Demo Request - Employee Scheduling"
}
```

## Lead Scoring Algorithm

OpenClaw automatically scores leads based on:

- **Email keywords** (demo, pricing, trial): +30 points
- **Company domain** (.com/.se/.ai vs gmail/yahoo): +20 points
- **Phone number provided**: +10 points
- **Mentioned employee count**: +15 points
- **Urgency keywords** (urgent, asap, soon): +10 points

**Score ranges:**
- 90-100: Hot (immediate follow-up)
- 70-89: Qualified (follow-up within 24h)
- 50-69: Warm (nurture sequence)
- 0-49: Cold (general inquiry)

## Viewing Scraped Leads

### In Dashboard
1. Go to http://localhost:3030
2. Click "Show Details" in Data Overview
3. View Top Leads (Score > 80)

### Via API
```bash
curl http://localhost:3030/api/data/leads | jq '.[] | {name, email, score, status}'
```

### Raw File
```bash
cat .compound-state/data/leads.json | jq '.'
```

## Privacy & Security

✅ **What OpenClaw does:**
- Reads email subject and sender info
- Extracts contact details from email body
- Stores locally in `.compound-state/data/leads.json`
- Never sends data externally

❌ **What OpenClaw doesn't do:**
- Doesn't delete or modify emails
- Doesn't send automated replies (unless AUTO_EMAIL_ENABLED=true)
- Doesn't store full email content
- Doesn't share data with third parties

## Troubleshooting

### "Invalid credentials" error
- Check email/password in `.env`
- For Gmail: Use app password, not regular password
- For Microsoft 365: Enable "IMAP access" in settings

### "Connection timeout" error
- Check firewall isn't blocking port 993
- Verify IMAP_HOST is correct
- Test with: `telnet imap.gmail.com 993`

### "No leads detected" but emails exist
- Check EMAIL_LEAD_KEYWORDS includes your keywords
- Verify emails aren't already marked as read
- Check `.env` file has correct EMAIL_USER

### Leads not appearing in dashboard
- Restart dashboard: `lsof -ti:3030 | xargs kill -9 && cd dashboard && node server.js &`
- Check file exists: `cat .compound-state/data/leads.json`
- Check API: `curl http://localhost:3030/api/data/leads`

## Support

Questions about email setup?
- Check logs: `tail -f logs/openclaw.log`
- Test manually: `./agents/marketing/openclaw-lead-scraper.sh`
- View current config: `cat .env | grep EMAIL`
