# Email Lead Scraping Setup Guide

## Quick Start

OpenClaw can monitor your business emails to automatically capture leads from:
- Contact form submissions forwarded to email
- Direct inquiries (info@, contact@, hello@)
- Demo requests
- Pricing inquiries
- Support emails from prospects

## Recommended Email Setup

### Option 1: Single General Email (Recommended for Start)
Use your main business inbox that receives all inquiries:

```bash
cp .env.template .env
# Edit .env:
EMAIL_USER=info@caire.se
EMAIL_PASSWORD=your-app-specific-password
```

**Best for:**
- `info@caire.se` - Main AppCaire inquiries
- `contact@caire.se` - General contact form
- `hello@caire.se` - Friendly inquiry address

### Option 2: Multiple Domain Monitoring
Monitor leads from all your properties:

```bash
# In .env, configure all three:
EMAIL_USER=info@caire.se
EMAIL_PASSWORD=caire-app-password

EMAIL_USER_2=info@eirtech.ai
EMAIL_PASSWORD_2=eirtech-app-password

EMAIL_USER_3=info@nackahemtjanst.se
EMAIL_PASSWORD_3=nackahemtjanst-app-password
```

**Best for:**
- Each property gets its own lead source tracking
- SEO sites (eirtech.ai, nackahemtjanst.se) generate separate leads
- Better attribution per marketing channel

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

### Manual Test
```bash
cd ~/HomeCare/be-agent-service
./agents/marketing/openclaw-lead-scraper.sh
```

### Automatic (Every 15 Minutes)
OpenClaw runs automatically via launchd:

```bash
# Check if it's running
launchctl list | grep openclaw

# View logs
tail -f logs/openclaw.log
```

### Stop Automatic Scraping
```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

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
