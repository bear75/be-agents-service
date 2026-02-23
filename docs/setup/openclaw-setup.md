# OpenClaw Setup Guide - Telegram Integration

## What is OpenClaw?

**OpenClaw** is your personal AI assistant that runs on your Mac Mini and connects to messaging platforms. This setup uses **Telegram only**. It allows you (as CEO/Product Owner) to:

- Chat with your agent service from anywhere via Telegram
- Wake up to completed PRs, finished tasks, and new leads
- Issue commands to start jobs, check status, approve tasks
- Receive real-time notifications about agent activities
- Access all agent features without opening the dashboard

**How it works:**
- OpenClaw runs as a background service (daemon) on your Mac Mini
- It connects to Telegram (WhatsApp is not used — see below)
- You chat with it like texting an assistant
- It communicates with your be-agents-service via API calls

**Why Telegram only:** WhatsApp is disabled. Using WhatsApp with a personal number sends bot/pairing messages to everyone who messages you. The config templates ship without WhatsApp; use Telegram only.

---

## Prerequisites

- Mac Mini running macOS (Intel or Apple Silicon)
- Node.js 22 or higher
- Telegram account (for Telegram integration)
- Internet connection

---

## Installation on Mac Mini

### Step 1: Install Node.js 22

```bash
# Install Node.js via Homebrew
brew install node@22

# Verify installation
node --version  # Should show v22.x.x
```

### Step 2: Install OpenClaw

```bash
# Install OpenClaw globally
npm install -g openclaw@latest

# Verify installation
openclaw --version
```

### Step 3: Run Onboarding Wizard

```bash
# This configures Gateway and installs as macOS daemon
openclaw onboard --install-daemon
```

**During onboarding you'll configure:**
- AI Provider (Anthropic API with your Claude API key)
- Model preferences (opus-4.6 for brain, sonnet for execution)
- Gateway port (default: 18789)
- Auto-start on boot (via launchd)

### Step 4: Verify Installation

```bash
# Check Gateway status
openclaw gateway status

# Access Dashboard
open http://localhost:18789/
```

You should see the OpenClaw dashboard running. This is your AI assistant's control center.

---

## Telegram Integration

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send the command: `/newbot`
3. Follow prompts:
   - **Bot name**: "AppCaire Agent Service" (display name)
   - **Bot username**: "appcaire_agent_bot" (must end in 'bot')
4. Copy the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Add Telegram Channel to OpenClaw

```bash
# Add Telegram with your bot token
openclaw channels add telegram --token YOUR_BOT_TOKEN
```

Replace `YOUR_BOT_TOKEN` with the token from BotFather.

### Step 3: Pair Your Account

1. Open Telegram
2. Search for your bot (@appcaire_agent_bot)
3. Send: `/start`

You'll receive a **pairing code** (e.g., `ABC123`).

Back in terminal, approve the pairing:
```bash
openclaw pairing approve telegram ABC123
```

### Step 4: Test the Bot

Send a message to your Telegram bot:
```
Status check
```

The bot should respond with agent service status.

---

## Connecting OpenClaw to Agent Service

OpenClaw needs to communicate with your be-agents-service API. Configure the integration:

### Step 1: Edit OpenClaw Configuration

Edit `~/.openclaw/openclaw.json`:

```json
{
  "llm": {
    "provider": "anthropic",
    "apiKey": "your-anthropic-api-key",
    "model": "claude-opus-4-5"
  },
  "integrations": {
    "agentService": {
      "enabled": true,
      "apiUrl": "http://localhost:3030/api",
      "webhookUrl": "http://localhost:18789/webhooks/agent-service"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN"
    }
  }
}
```

### Step 2: Create Webhook Endpoint in Agent Service

Add this to `dashboard/server.js`:

```javascript
// OpenClaw Webhook - Receive notifications from agent service
if (pathname === '/webhooks/openclaw' && req.method === 'POST') {
  let body = '';
  req.on('data', chunk => { body += chunk.toString(); });
  req.on('end', () => {
    try {
      const event = JSON.parse(body);

      // Forward to OpenClaw
      const openclawUrl = 'http://localhost:18789/api/send-message';
      const payload = {
        channel: 'telegram',
        userId: process.env.CEO_TELEGRAM_ID,
        message: formatNotification(event)
      };

      // Send notification
      fetch(openclawUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true }));
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
  });
  return;
}
```

### Step 3: Add CEO Contact Info to .env

Add your Telegram info to `.env`:

```bash
# CEO Contact for OpenClaw Notifications (Telegram only)
CEO_TELEGRAM_ID="@bjornevers"     # Your Telegram username
OPENCLAW_WEBHOOK_SECRET="generate-a-secure-random-string"
```

### Step 4: Enable Notifications

Configure which events trigger Telegram notifications:

```bash
# In agent service .env
OPENCLAW_NOTIFY_EVENTS=job_completed,job_failed,pr_created,new_lead,agent_blocked
```

---

## Usage Examples

### Via Telegram

```
You: Show me top 5 leads
Bot: 📊 Top 5 Leads (Score > 80):

     1. Sarah Johnson - Sunrise Home Care (Score: 95)
        sales@sunrisehc.com | Demo requested

     2. Michael Chen - Nordic Care AB (Score: 88)
        info@nordiccare.se | Pricing inquiry

     [...]

     View all: http://localhost:3030/sales-marketing.html
```

---

## Automatic Startup (Mac Mini)

OpenClaw is installed as a launchd daemon and starts automatically on boot.

**Manual controls:**

```bash
# Start OpenClaw
openclaw gateway start

# Stop OpenClaw
openclaw gateway stop

# Restart OpenClaw
openclaw gateway restart

# Check status
openclaw gateway status

# View logs
openclaw gateway logs
```

---

## Telegram Benefits

Once configured, you can:

1. **Message from anywhere** - Use Telegram on phone or laptop
2. **Shared context** - OpenClaw remembers the conversation
3. **Always connected** - Mac Mini runs 24/7, you can message anytime
4. **Proactive notifications** - Get alerts when jobs complete, leads arrive, agents need approval

---

## Security Best Practices

1. **API Keys**: Store in `~/.openclaw/openclaw.json` with restricted permissions:
   ```bash
   chmod 600 ~/.openclaw/openclaw.json
   ```

2. **Pairing**: Always approve pairing requests manually (don't auto-approve)

3. **WhatsApp**: WhatsApp is not used. Do not add a WhatsApp channel with a personal number (everyone who messages you would get bot/pairing messages).

4. **Webhook Secret**: Use strong random string for webhook authentication

5. **Firewall**: Keep ports 18789 (OpenClaw) and 3030 (Agent Service) local-only unless needed externally

6. **Backup Config**:
   ```bash
   cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
   ```

---

## Troubleshooting

### Telegram Bot Not Responding
- Verify bot token: `openclaw channels list`
- Check pairing status: `openclaw pairing list`
- Restart gateway: `openclaw gateway restart`

### No Notifications Received
- Check .env has correct `CEO_TELEGRAM_ID`
- Verify webhook is configured in agent-service
- Check OpenClaw logs: `openclaw gateway logs`

### OpenClaw Won't Start
- Check Node.js version: `node --version` (needs 22+)
- View error logs: `tail -f ~/.openclaw/logs/gateway.log`
- Reinstall: `npm uninstall -g openclaw && npm install -g openclaw@latest`

---

## Integration with Agent Service Features

OpenClaw can control all agent service features via chat:

| Command | Action |
|---------|--------|
| `Start engineering job` | Launches orchestrator.sh |
| `Start marketing job` | Launches jarvis-orchestrator.sh |
| `Show active jobs` | Lists running jobs |
| `Stop job [id]` | Kills running job |
| `Show top leads` | Lists high-score leads |
| `Show agent performance` | Agent stats and success rates |
| `Approve automation [id]` | Approve RL automation candidate |
| `Show experiments` | RL experiment status |
| `Create agent [role]` | HR agent creation |
| `Fire agent [name]` | Deactivate agent |

All commands work from Telegram.

---

## Next Steps

1. ✅ Install OpenClaw on Mac Mini
2. ✅ Connect Telegram bot
3. ✅ Configure agent service webhook
4. ✅ Test with simple commands
5. ✅ Enable auto-notifications
6. 🎉 Wake up to completed PRs and new leads!

---

## Resources

- [OpenClaw Official Website](https://openclaw.ai/)
- [OpenClaw Documentation](https://docs.openclaw.ai/)
- [OpenClaw Integrations](https://openclaw.ai/integrations)
- [Telegram Setup Guide](https://docs.openclaw.ai/channels/telegram)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Installation Tutorial](https://www.aifreeapi.com/en/posts/openclaw-installation-guide)

---

**Questions?** Check the logs first:
```bash
openclaw gateway logs
tail -f ~/.openclaw/logs/gateway.log
tail -f ~/HomeCare/be-agents-service/logs/openclaw.log
```

Happy chatting with your AI assistant! 🦞
