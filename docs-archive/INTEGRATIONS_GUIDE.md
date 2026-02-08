# Integrations Guide – Complete Setup for All Tools

## Overview

The Agent Service supports integrations with 14 platforms across 4 categories:
- **📧 Email** - Notifications and communications
- **📱 Social Media** - LinkedIn, Twitter, Instagram, Facebook
- **🔑 API Services** - OpenAI, Anthropic
- **🛠️ Tools & Platforms** - Notion, GitHub, Jira, Confluence, HubSpot, Miro, Figma

**Access Settings:** http://localhost:3030/settings.html

---

## Quick Start

### 1. Essential Integrations (Recommended First)

Configure these first for basic functionality:

1. **Email (SMTP)** - For agent notifications
2. **Confluence** - For documentation sync
3. **Jira** - For task tracking
4. **Anthropic API** - For LLM usage

### 2. Configuration Flow

For each integration:
1. Go to settings page
2. Toggle integration to "Active"
3. Fill in credentials and config
4. Click "💾 Save"
5. Test connection

---

## 📧 Email Configuration (SMTP)

### Purpose
Send notifications, reports, and alerts from agents.

### Setup Options

#### Option 1: Gmail (Development)
```
Host: smtp.gmail.com
Port: 587
Username: your-email@gmail.com
Password: [App Password from Google]
From: your-email@gmail.com
```

**Get App Password:**
1. Enable 2FA on Google Account
2. Visit: https://myaccount.google.com/apppasswords
3. Generate password for "Mail"

**Limits:** 500 emails/day

#### Option 2: SendGrid (Production - Recommended)
```
Host: smtp.sendgrid.net
Port: 587
Username: apikey
Password: [SendGrid API Key]
From: notifications@yourdomain.com
```

**Setup:**
1. Sign up at https://sendgrid.com
2. Create API Key with "Mail Send" permissions
3. Verify sender identity

**Free Tier:** 100 emails/day

#### Option 3: AWS SES (Production - Scalable)
```
Host: email-smtp.[region].amazonaws.com
Port: 587
Username: [AWS SMTP Username]
Password: [AWS SMTP Password]
From: notifications@yourdomain.com
```

**Setup:**
1. AWS Console → SES → Verified Identities
2. Verify domain
3. Create SMTP credentials

**Cost:** $0.10 per 1000 emails

### Configuration in Dashboard

1. Navigate to: http://localhost:3030/settings.html
2. Go to "📧 Email Configuration"
3. Toggle "Email SMTP Server" to active
4. Fill in fields:
   - SMTP Host
   - Port
   - From Email
   - Username
   - Password
5. Click "💾 Save"

### Testing Email

```bash
# Install nodemailer if not installed
npm install nodemailer

# Create test script
cat > test-email.js << 'EOF'
const nodemailer = require('nodemailer');
const db = require('./lib/database');

async function testEmail() {
  const integration = db.getIntegration('int-email-smtp');
  const config = JSON.parse(integration.config);
  const credentials = JSON.parse(integration.credentials);

  const transporter = nodemailer.createTransport({
    host: config.host,
    port: parseInt(config.port),
    secure: config.port === '465',
    auth: {
      user: credentials.username,
      pass: credentials.password
    }
  });

  const info = await transporter.sendMail({
    from: config.from,
    to: 'test@example.com',
    subject: '✅ Test Email',
    text: 'Email configuration working!'
  });

  console.log('✅ Test email sent:', info.messageId);
}

testEmail();
EOF

# Run test
node test-email.js
```

---

## 📄 Confluence Documentation Sync

### Purpose
Automatically sync documentation from markdown files to Confluence.

### Setup

**Based on your existing beta-appcaire configuration:**

```
Base URL: https://caire.atlassian.net/wiki
Email: your-email@caire.se
API Token: [Generate from Atlassian]
Space Key: TWC
Parent Page ID: 393372
```

### Get API Token

1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it "Agent Service Integration"
4. Copy the token

### Configuration

1. Settings → "🛠️ Tools & Platforms"
2. Find "Confluence Documentation"
3. Toggle to active
4. Fill in:
   - Base URL: `https://caire.atlassian.net/wiki`
   - Email: your Atlassian email
   - API Token: [paste token]
   - Space Key: `TWC` (for internal docs) or `CAIREHCDD` (for DPIA)
   - Parent Page ID: `393372` (TWC parent)
5. Click "💾 Save"

### Confluence Spaces

Your existing configuration:
- **TWC Space** - Internal documentation
  - Parent: 393372
  - Used for: Architecture, API docs, guides

- **CAIREHCDD Space** - Customer Due Diligence
  - DPIA Parent: 7274719
  - Attendo Pilot Parent: 21200897

### Sync Methods

#### Method 1: MCP in Cursor (Recommended ⭐)

Simply ask Cursor:
```
"Sync docs_refactor/01-architecture/VISUAL_GUIDE.md to Confluence"
"Update all DPIA documents in Confluence"
```

MCP handles OAuth and upload automatically.

#### Method 2: API Integration (Future)

The agent service can sync docs programmatically:

```javascript
const confluence = require('./lib/integrations/confluence');

await confluence.syncMarkdownToPage({
  filePath: 'docs/architecture.md',
  spaceKey: 'TWC',
  parentId: '393372',
  title: 'Architecture Overview'
});
```

### What Gets Synced

From your existing sync-config.yml:

**Auto-sync folders:**
- `01-architecture/` → TWC
- `02-api/` → TWC
- `03-data/` → TWC
- `04-migration/` → TWC
- `05-prd/` → TWC
- `06-compliance/DPIA/` → CAIREHCDD
- `07-guides/` → TWC
- `08-frontend/` → TWC
- `09-scheduling/` → TWC

**Manually managed:**
- Attendo Pilot docs → CAIREHCDD

---

## 📋 Jira Project Management

### Purpose
Create tasks, track sprints, sync agent work to Jira issues.

### Setup

```
Base URL: https://caire.atlassian.net
Email: your-email@caire.se
API Token: [Same as Confluence token]
Project Key: CAIRE (or your project key)
```

### Configuration

1. Settings → "🛠️ Tools & Platforms"
2. Find "Jira Project Management"
3. Toggle to active
4. Fill in:
   - Base URL: `https://caire.atlassian.net`
   - Email: your Atlassian email
   - API Token: [same token as Confluence]
   - Project Key: `CAIRE` (check your Jira project)
5. Click "💾 Save"

### Usage

**Create Issue from Agent Task:**
```javascript
const jira = require('./lib/integrations/jira');

await jira.createIssue({
  project: 'CAIRE',
  summary: 'Backend: Update Prisma schema',
  description: 'Agent backend needs to update database schema',
  issueType: 'Task',
  assignee: 'bjorn@caire.se'
});
```

**Sync Agent Task to Jira:**
```javascript
await jira.syncTask({
  taskId: 'task-123',
  agentId: 'agent-backend',
  jiraIssueKey: 'CAIRE-456'
});
```

---

## 🔶 HubSpot CRM Integration

### Purpose
Sync leads, deals, and customer data from marketing campaigns.

### Setup

```
API Key: [HubSpot Private App Token]
Portal ID: 12345678 (optional)
```

### Get API Key

1. HubSpot Settings → Integrations → Private Apps
2. Create Private App
3. Select scopes: `crm.objects.contacts.read`, `crm.objects.deals.read`
4. Generate token

### Configuration

1. Settings → "🛠️ Tools & Platforms"
2. Find "HubSpot CRM"
3. Toggle to active
4. Fill in:
   - API Key: [private app token]
   - Portal ID: [your portal ID]
5. Click "💾 Save"

### Usage

**Sync Leads to Database:**
```javascript
const hubspot = require('./lib/integrations/hubspot');

// Fetch recent contacts
const contacts = await hubspot.getRecentContacts(100);

// Store in database
contacts.forEach(contact => {
  db.createLead({
    source: 'hubspot',
    contact_email: contact.email,
    contact_name: contact.name,
    status: 'new',
    assigned_to: 'agent-jarvis'
  });
});
```

---

## 📱 Social Media Integrations

### LinkedIn Company Page

```
Access Token: [OAuth token]
Account ID: [Company page ID]
Organization ID: [LinkedIn org ID]
```

**Get Token:**
1. LinkedIn Developers → My Apps
2. Create app with Marketing API access
3. OAuth 2.0 authorization flow
4. Copy access token

### X (Twitter)

```
Access Token: [OAuth 2.0 Bearer token]
Account ID: [@your_handle]
```

**Get Token:**
1. Twitter Developer Portal → Projects & Apps
2. Generate Bearer Token
3. Save token

### Instagram Business

```
Access Token: [Facebook Graph API token]
Account ID: [Instagram Business Account ID]
```

**Get Token:**
1. Facebook Developers → Graph API Explorer
2. Select Instagram Business Account permissions
3. Generate long-lived token

### Facebook Page

```
Access Token: [Page Access Token]
Page ID: [Facebook Page ID]
```

**Get Token:**
1. Facebook Developers → Access Token Tool
2. Select page
3. Generate page access token

---

## 🔑 AI API Services

### Anthropic Claude

```
API Key: sk-ant-api03-...
Model Preference: claude-sonnet-4-5-20250929
```

**Get API Key:**
1. Visit: https://console.anthropic.com/
2. Account → API Keys
3. Create key

### OpenAI GPT

```
API Key: sk-...
Organization ID: org-... (optional)
```

**Get API Key:**
1. Visit: https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key immediately

---

## 🛠️ Other Tools

### Notion Workspace

```
Integration Token: secret_...
Database ID: [Notion database ID]
```

**Setup:**
1. Notion Settings → Integrations → Develop your own integrations
2. Create integration
3. Share database with integration
4. Copy token

### GitHub Organization

```
Personal Access Token: ghp_...
Organization: your-org-name
```

**Setup:**
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`
4. Copy token

### Miro Workshops

```
API Token: [Miro access token]
```

**Setup:**
1. Miro Developer Portal
2. Create app
3. Get OAuth token

### Figma Design

```
API Token: [Figma personal access token]
```

**Setup:**
1. Figma Settings → Personal access tokens
2. Generate new token
3. Copy token

---

## Security Best Practices

### 1. Never Commit Credentials

```bash
# .gitignore
.env
credentials.json
smtp-config.json
atlassian-credentials.txt
```

### 2. Use Environment Variables

```bash
# .env
CONFLUENCE_API_TOKEN=your-token
JIRA_API_TOKEN=your-token
SMTP_PASSWORD=your-password
```

### 3. Rotate Tokens Regularly

- Atlassian tokens: Every 90 days
- API keys: Every 180 days
- OAuth tokens: Refresh before expiry

### 4. Principle of Least Privilege

Only grant necessary permissions:
- Confluence: Read + Write to specific spaces
- Jira: Create issues in specific projects
- APIs: Minimum required scopes

### 5. Audit Logging

Track all integration changes:
```sql
CREATE TABLE integration_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integration_id TEXT,
    action TEXT, -- 'activated', 'deactivated', 'config_changed'
    changed_by TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Testing Integrations

### Test Connection Script

```javascript
// test-integrations.js
const db = require('./lib/database');

async function testIntegration(integrationId) {
  const integration = db.getIntegration(integrationId);

  if (!integration.is_active) {
    console.log(`❌ ${integration.name} is not active`);
    return;
  }

  const config = JSON.parse(integration.config || '{}');
  const credentials = JSON.parse(integration.credentials || '{}');

  console.log(`🧪 Testing ${integration.name}...`);

  // Platform-specific tests
  switch (integration.platform) {
    case 'confluence':
      await testConfluence(config, credentials);
      break;
    case 'jira':
      await testJira(config, credentials);
      break;
    case 'smtp':
      await testEmail(config, credentials);
      break;
    // Add more cases...
  }
}

async function testConfluence(config, credentials) {
  const axios = require('axios');

  try {
    const response = await axios.get(
      `${config.base_url}/rest/api/space/${config.space_key}`,
      {
        auth: {
          username: credentials.email,
          password: credentials.token
        }
      }
    );

    console.log(`✅ Confluence connected: ${response.data.name}`);
  } catch (error) {
    console.log(`❌ Confluence error: ${error.message}`);
  }
}

// Run tests
testIntegration('int-tool-confluence');
testIntegration('int-tool-jira');
testIntegration('int-email-smtp');
```

---

## Troubleshooting

### Atlassian 401 Unauthorized

**Causes:**
- Wrong email
- Wrong API token
- Token expired
- Token doesn't have permissions

**Solution:**
1. Regenerate API token
2. Verify email matches Atlassian account
3. Check token hasn't expired

### Email "EAUTH - Authentication failed"

**Causes:**
- Wrong credentials
- App password not generated (Gmail)
- 2FA not enabled

**Solution:**
1. Generate new app password
2. Verify credentials are correct
3. Test with telnet: `telnet smtp.gmail.com 587`

### Rate Limiting

Most APIs have rate limits:
- Atlassian: 200 requests per minute
- HubSpot: 100 requests per 10 seconds
- Social APIs: Varies by platform

**Solution:**
- Implement exponential backoff
- Cache results when possible
- Batch requests

---

## Next Steps

1. ✅ Configure essential integrations (Email, Confluence, Jira)
2. ✅ Test connections
3. ✅ Implement sync logic in agents
4. ✅ Set up monitoring and alerts
5. ✅ Document team workflows

---

**Last Updated:** 2026-02-08
**Total Integrations:** 14
**Status:** Ready for Configuration

**Settings Page:** http://localhost:3030/settings.html
