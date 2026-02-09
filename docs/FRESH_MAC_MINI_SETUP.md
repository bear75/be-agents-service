# Fresh Mac Mini Setup — From Unboxing to Running

**For a brand new, empty Mac mini. Everything from zero.**
**Time: ~90 minutes total.**

---

## Phase 1: Unbox and macOS Setup (10 min)

1. Connect Mac mini to monitor, keyboard, mouse, ethernet/WiFi
2. Power on → follow macOS setup wizard
3. **Sign in with your Apple ID** — this gives you iCloud (for shared workspace sync to iPhone/iPad) and App Store
4. Create your admin account
5. Complete setup, let macOS install updates if prompted

### System Settings (do this now):

Open **System Settings** (Apple menu → System Settings):

```
General → About → Name: "appcaire-mac-mini"

Privacy & Security → FileVault: Turn On (encrypts disk)

Energy:
  → Prevent automatic sleeping when display is off: ON
  → Wake for network access: ON

Sharing → Remote Login: ON (lets you SSH in later)

General → Software Update: Install any pending updates
```

**Restart if macOS updates require it.**

---

## Phase 2: Terminal + Homebrew + Dev Tools (25 min)

Open **Terminal** (Applications → Utilities → Terminal). Run everything below in Terminal.

### 2.1 Xcode Command Line Tools

```bash
xcode-select --install
```

Click **Install** in the popup. Wait 5-10 minutes.

Verify:
```bash
xcode-select -p
# Output: /Library/Developer/CommandLineTools
```

### 2.2 Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Follow the instructions it prints.** For Apple Silicon (M1/M2/M3/M4):
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Verify:
```bash
brew --version
```

### 2.3 Git

```bash
brew install git

git config --global user.name "Björn Evers"
git config --global user.email "your.email@example.com"

git --version
```

### 2.4 Node.js 22 + Yarn

```bash
brew install node@22

# Verify
node --version   # Should be v22.x.x
npm --version

# Install Yarn
npm install -g yarn
yarn --version   # Should be 1.22.x
```

### 2.5 GitHub CLI

```bash
brew install gh
gh --version

# Authenticate — this opens a browser
gh auth login
# Choose: GitHub.com → HTTPS → Yes → Login with browser
```

### 2.6 Other tools

```bash
brew install jq         # JSON parsing (used by agent scripts)
```

### 2.7 Claude Code CLI

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify
claude --version

# Authenticate with your Anthropic account
claude auth
```

### 2.8 Install Cursor (optional but recommended)

Download from https://cursor.com and install. This is your IDE for reviewing code.

---

## Phase 3: Clone Repositories (5 min)

```bash
# Create the main directory
mkdir -p ~/HomeCare
cd ~/HomeCare

# Clone the agent service
git clone https://github.com/bear75/be-agents-service.git
cd be-agents-service

# Switch to the branch with all new workspace features
git checkout cursor/shared-markdown-data-storage-d333

# Make all scripts executable
chmod -R +x scripts/ agents/ lib/ dashboard/

# Verify
ls scripts/workspace/
# Should see: init-workspace.sh, generate-checkin.sh, etc.
```

Now clone your main app (if the repo is accessible):
```bash
cd ~/HomeCare

# Clone beta-appcaire (your monorepo)
git clone https://github.com/bear75/beta-appcaire.git
# If this is private/different org, use the correct URL

# Install monorepo dependencies
cd beta-appcaire
yarn install
```

---

## Phase 4: Set Up API Keys and Env (3 min)

```bash
# Create secure config directory
mkdir -p ~/.config/caire

# Create the env file with your API keys
cat > ~/.config/caire/env << 'EOF'
# Anthropic (for Claude Code)
export ANTHROPIC_API_KEY="sk-ant-YOUR_KEY_HERE"

# GitHub (optional — gh auth handles this)
# export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
EOF

chmod 600 ~/.config/caire/env

# Add to shell profile so it loads on every terminal
echo 'source ~/.config/caire/env' >> ~/.zprofile
source ~/.config/caire/env
```

---

## Phase 5: Initialize Shared Workspace (2 min)

This creates your markdown workspace on iCloud — accessible from all your Apple devices.

```bash
cd ~/HomeCare/be-agents-service

# Create the workspace on iCloud
./scripts/workspace/init-workspace.sh beta-appcaire
```

This creates:
```
~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/
├── inbox.md              ← Drop ideas here (syncs to iPhone!)
├── priorities.md         ← Agent picks #1 nightly
├── tasks.md              ← Task tracking
├── follow-ups.md         ← Revisit later
├── check-ins/daily/      ← Daily notes
├── check-ins/weekly/     ← Weekly reviews
├── check-ins/monthly/    ← Monthly planning
├── memory/               ← Decisions, learnings, context
└── agent-reports/        ← Agent session summaries
```

**Edit your priorities now:**
```bash
open ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/priorities.md
```

**Add project context for agents:**
```bash
open ~/Library/Mobile\ Documents/com~apple~CloudDocs/AgentWorkspace/beta-appcaire/memory/context.md
```

---

## Phase 6: Build & Start Agent Server (3 min)

```bash
cd ~/HomeCare/be-agents-service

# Install all dependencies
yarn install

# Build the API server
cd apps/server
yarn build

# Test it works
node dist/index.js
# Should print: 🤖 Agent Service API running on http://localhost:4010
# Press Ctrl+C to stop (we'll run it via LaunchD later)
```

---

## Phase 7: Set Up Telegram Bot (5 min)

### 7a: Create the bot

1. Open **Telegram** on your phone
2. Search for **@BotFather**
3. Send `/newbot`
4. Name: `AppCaire Agent`
5. Username: `appcaire_agent_bot` (must end with `bot`, must be unique)
6. **Copy the bot token** it gives you

### 7b: Get your chat ID

1. Search for **@userinfobot** on Telegram
2. Send it any message
3. **Copy your numeric ID**

### 7c: Save credentials

```bash
cat >> ~/.config/caire/env << 'EOF'

# Telegram
export TELEGRAM_BOT_TOKEN="PASTE_YOUR_BOT_TOKEN_HERE"
export TELEGRAM_CHAT_ID="PASTE_YOUR_CHAT_ID_HERE"
EOF

source ~/.config/caire/env
```

### 7d: Test it

```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=🤖 Agent service connected!" \
  -d "parse_mode=Markdown"
```

✅ You should get a Telegram message!

---

## Phase 8: Install OpenClaw (5 min)

OpenClaw is the AI bot that connects Telegram to your workspace.

```bash
# Install
curl -fsSL https://openclaw.ai/install.sh | bash

# Onboard (sets up daemon)
openclaw onboard --install-daemon
```

### 8a: Build the MCP bridge

```bash
cd ~/HomeCare/be-agents-service/apps/openclaw-bridge
npm install
```

### 8b: Configure OpenClaw

```bash
mkdir -p ~/.openclaw
cp ~/HomeCare/be-agents-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json
```

Edit `~/.openclaw/openclaw.json` — replace:
- `${TELEGRAM_BOT_TOKEN}` → your actual bot token
- `YOUR_TELEGRAM_USER_ID` → your numeric Telegram ID
- `+46XXXXXXXXX` → your WhatsApp number (or delete the whatsapp section)
- Verify all file paths match your actual directories

### 8c: Start and test

```bash
openclaw start
```

Open Telegram → find your bot → send `status`. You should get a workspace overview!

---

## Phase 9: Load LaunchD Jobs (3 min)

These run everything automatically on schedule.

```bash
cd ~/HomeCare/be-agents-service

# First: update the username in all plist files
# Check your Mac username:
whoami

# Replace the placeholder with YOUR username:
sed -i '' "s/bjornevers_MacPro/$(whoami)/g" launchd/*.plist

# Copy to LaunchAgents
cp launchd/*.plist ~/Library/LaunchAgents/

# Load all jobs
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.morning-briefing.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.weekly-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.openclaw.plist

# Verify
launchctl list | grep appcaire
# Should see 7 jobs listed
```

---

## Phase 10: Verify Everything Works (5 min)

```bash
# API server running?
curl -s http://localhost:4010/health

# Workspace connected?
curl -s http://localhost:4010/api/workspace/beta-appcaire/status

# Plans readable?
curl -s http://localhost:4010/api/plans | python3 -m json.tool

# Setup status?
curl -s http://localhost:4010/api/plans/setup-status?repo=beta-appcaire | python3 -m json.tool

# Dashboard loads?
open http://localhost:3010

# Telegram morning briefing works?
./scripts/notifications/morning-briefing.sh beta-appcaire

# LaunchD jobs loaded?
launchctl list | grep appcaire
```

---

## ✅ Done! What You Now Have

| What | Where | When |
|------|-------|------|
| Shared workspace | iCloud (syncs to all devices) | Always accessible |
| Telegram bot | Your phone | Text anytime |
| Morning briefing | Telegram | 8:00 AM daily |
| Weekly review | Telegram | Monday 8:00 AM |
| Agent learning extraction | Mac mini | 10:30 PM nightly |
| Agent implementation | Mac mini | 11:00 PM nightly |
| Dashboard | http://localhost:3010 | Always running |
| API | http://localhost:4010 | Always running |
| Mac stays awake | Caffeinate | Always |

---

## What Happens Next

**Tonight at 10:30 PM:** Agent reviews today's Claude sessions, extracts learnings

**Tonight at 11:00 PM:** Agent reads Priority #1 from your workspace, implements it, creates a PR

**Tomorrow at 8:00 AM:** You get a Telegram message summarizing what happened

**You:** Review the PR, merge if good, update priorities for tomorrow

---

## Daily Workflow

**Morning (2 min):** Read Telegram briefing → review PR → merge or comment

**Anytime:** Text the bot to add ideas, check status, review priorities

**Evening (1 min):** Update priorities.md if tomorrow's focus changes

That's it. The system runs itself.
