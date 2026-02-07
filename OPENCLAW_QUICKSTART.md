# OpenClaw Email Lead Scraper - Quick Start

OpenClaw is now fully implemented and ready to monitor all 9 email addresses across your 3 domains for lead capture.

## What Was Implemented

✅ **Full IMAP Email Scraping** - Connects to Gmail/Outlook via IMAP
✅ **Multi-Domain Support** - Monitors 9 email addresses simultaneously
✅ **Intelligent Lead Scoring** - 50-100 point scoring algorithm
✅ **Contact Info Extraction** - Parses name, email, company, phone
✅ **Lead Attribution** - Tracks which email/domain generates leads
✅ **Auto-Marking as Read** - Prevents duplicate processing
✅ **Automated Scheduling** - launchd job runs every 15 minutes

## Email Accounts Configured

1. **caire.se** (AppCaire main product)
   - sales@caire.se
   - info@caire.se
   - bjorn@caire.se

2. **eirtech.ai** (Ireland/EU market)
   - sales@eirtech.ai
   - info@eirtech.ai
   - bjorn@eirtech.ai

3. **nackahemtjanst.se** (Nacka local market)
   - sales@nackahemtjanst.se
   - info@nackahemtjanst.se
   - bjorn@nackahemtjanst.se

## 3-Step Setup

### Step 1: Configure Email Credentials

```bash
cd ~/HomeCare/be-agent-service

# Copy template
cp .env.template .env

# Edit and add Gmail app passwords
vim .env
```

**Get Gmail App Passwords:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Mac"
5. Click "Generate"
6. Copy 16-character password (no spaces)
7. Paste into `.env` file

**Example .env configuration:**
```bash
EMAIL_1_USER=sales@caire.se
EMAIL_1_PASSWORD=abcdEFGHijklMNOP  # Your Gmail app password

EMAIL_2_USER=info@caire.se
EMAIL_2_PASSWORD=abcdEFGHijklMNOP

# ... repeat for all 9 emails
```

### Step 2: Test Manual Run

```bash
# Install jq if needed
brew install jq

# Run scraper once
./agents/marketing/openclaw-lead-scraper.sh
```

**Expected output:**
```
[2026-02-07 16:30:45] 📧 OpenClaw Lead Scraper Starting...
[2026-02-07 16:30:45] Checking sales@caire.se...
[2026-02-07 16:30:46]   No unread emails
[2026-02-07 16:30:46] Checking info@caire.se...
[2026-02-07 16:30:47]   Found unread emails: 1234
[2026-02-07 16:30:48]     ✅ New lead: Sarah Johnson (sarah@sunrisehc.com) - Score: 85
[2026-02-07 16:30:49] 📊 Lead Statistics:
[2026-02-07 16:30:49] Total leads: 1
[2026-02-07 16:30:49] ✅ Lead scraper completed
```

### Step 3: Enable Automatic Scraping (Every 15 Minutes)

```bash
# Copy launchd plist
cp com.appcaire.openclaw.plist ~/Library/LaunchAgents/

# Load the job
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist

# Verify it's running
launchctl list | grep openclaw
```

## Monitoring Leads

### View in Dashboard
```bash
# Start dashboard
cd dashboard
node server.js &

# Open browser
open http://localhost:3030
```

Click "Show Details" in Data Overview to see top leads.

### View via Command Line

```bash
# Total lead count
cat .compound-state/data/leads.json | jq 'length'

# Latest 5 leads
cat .compound-state/data/leads.json | jq '.[-5:] | .[] | {name, email, score, status}'

# Hot leads (90+)
cat .compound-state/data/leads.json | jq '[.[] | select(.score >= 90)] | .[] | {name, email, score, source}'

# Leads by source
cat .compound-state/data/leads.json | jq 'group_by(.source) | .[] | {source: .[0].source, count: length}'
```

### View Logs

```bash
# Live tail
tail -f logs/openclaw.log

# View last 50 lines
tail -50 logs/openclaw.log

# Search for errors
grep "Error" logs/openclaw.log
```

## Lead Scoring Explained

Each lead gets a score from 0-120+ based on:

| Factor | Points | Example |
|--------|--------|---------|
| **High-value keywords** | +30 | "demo", "trial", "pricing", "quote", "partnership" |
| **Medium keywords** | +15 | "interested", "inquiry", "contact", "boka", "offert" |
| **Business domain** | +20 | sarah@company.com (not @gmail.com) |
| **Phone provided** | +10 | "+46 70 123 4567" in email body |
| **Employee count** | +15 | "We have 50 employees" |
| **Urgency** | +10 | "urgent", "asap", "immediately" |

**Score ranges:**
- 90-100+: **Hot** (immediate follow-up required)
- 70-89: **Qualified** (follow-up within 24h)
- 50-69: **Warm** (nurture sequence)
- 0-49: **Cold** (general inquiry)

## Lead Attribution

Each lead is tagged with source email for performance tracking:

```json
{
  "source": "email-sales@caire.se",
  "score": 95,
  "status": "hot"
}
```

**Use this to:**
- Identify best-performing email address (sales@ vs info@)
- Track lead quality by domain (caire.se vs eirtech.ai vs nackahemtjanst.se)
- Optimize marketing spend based on lead source

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
- Check `EMAIL_LEAD_KEYWORDS` includes your keywords
- Verify emails aren't already marked as read
- Run with debugging: `bash -x agents/marketing/openclaw-lead-scraper.sh`

### Leads not appearing in dashboard
- Restart dashboard: `lsof -ti:3030 | xargs kill -9 && cd dashboard && node server.js &`
- Check file exists: `cat .compound-state/data/leads.json`
- Check API: `curl http://localhost:3030/api/data/leads`

## Next Steps

1. ✅ **You're done!** OpenClaw is fully implemented and ready to use
2. Configure your 9 Gmail app passwords in `.env`
3. Run manual test to verify connection
4. Enable launchd for automatic scraping
5. Monitor dashboard for incoming leads

## Advanced Configuration

### Add More Emails

Edit `.env.template` and add:
```bash
EMAIL_10_USER=sales@newdomain.com
EMAIL_10_PASSWORD=app-password
```

Update scraper loop in `openclaw-lead-scraper.sh`:
```bash
for i in {1..10}; do  # Changed from {1..9}
```

### Customize Lead Keywords

Edit `.env`:
```bash
EMAIL_LEAD_KEYWORDS=demo,trial,pricing,quote,partnership,interested,boka,offert,CUSTOM_KEYWORD
```

### Change Scraping Interval

Edit `com.appcaire.openclaw.plist`:
```xml
<key>StartInterval</key>
<integer>600</integer>  <!-- 10 minutes instead of 15 -->
```

Reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.appcaire.openclaw.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist
```

## Files Reference

- `agents/marketing/openclaw-lead-scraper.sh` - Main scraper script
- `com.appcaire.openclaw.plist` - launchd automation config
- `.env` - Email credentials (gitignored)
- `.env.template` - Configuration template
- `.compound-state/data/leads.json` - Lead database
- `logs/openclaw.log` - Scraper activity log
- `EMAIL_SETUP_GUIDE.md` - Comprehensive setup guide

## Support

Questions? Check:
1. `EMAIL_SETUP_GUIDE.md` - Full documentation
2. `logs/openclaw.log` - Recent activity
3. Test manually: `./agents/marketing/openclaw-lead-scraper.sh`
4. Check configuration: `cat .env | grep EMAIL`
