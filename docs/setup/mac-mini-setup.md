# Mac Mini Setup Guide - Multi-Agent Orchestrator

Complete setup guide for a **brand new Mac mini** to run the autonomous multi-agent development system with real-time dashboard.

---

## 📦 What You'll Have After Setup

- ✅ Multi-agent orchestrator running nightly (11 PM)
- ✅ Real-time dashboard at http://localhost:3030
- ✅ Automated PRs created from priority files
- ✅ Parallel specialist agents (backend, frontend, infrastructure)
- ✅ Verification layer preventing broken code
- ✅ Multi-repo support (beta-appcaire, cowork, marketing, etc.)

---

## 🖥️ Hardware Requirements

- **Mac Mini** (M1/M2/M3 or Intel)
- **Minimum**: 8GB RAM, 256GB SSD
- **Recommended**: 16GB RAM, 512GB SSD
- **Network**: Stable internet connection

---

## 📝 Setup Checklist

## Phase 1: Initial Mac Setup (30 minutes)

### 1.1 Unbox and Power On

1. Connect Mac mini to monitor, keyboard, mouse
2. Power on and follow macOS setup wizard
3. Create admin user account (your name)
4. Sign in with Apple ID (recommended for App Store)
5. Enable FileVault disk encryption (Security & Privacy)
6. Complete macOS setup

### 1.2 System Preferences

```bash
# Open System Preferences
# → Security & Privacy:
  - Enable FileVault ✅
  - Allow apps from App Store and identified developers ✅

# → Sharing:
  - Set Computer Name: "appcaire-mac-mini" ✅
  - Enable Remote Login (SSH) ✅ (optional, for remote access)

# → Energy Saver:
  - Prevent Mac from sleeping automatically ✅
  - Wake for network access ✅
```

### 1.3 Software Update

```bash
# System Preferences → Software Update
# Install all available updates
# Restart if required
```

---

## Phase 2: Command Line Tools (15 minutes)

### 2.1 Install Xcode Command Line Tools

```bash
# Open Terminal (Applications → Utilities → Terminal)
xcode-select --install

# Click "Install" in the popup
# Wait for download and installation (~5-10 minutes)

# Verify installation
xcode-select -p
# Should output: /Library/Developer/CommandLineTools
```

### 2.2 Install Homebrew (Package Manager)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow on-screen instructions
# Add Homebrew to PATH (commands will be shown after install)

# For Apple Silicon (M1/M2/M3):
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Intel Macs:
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"

# Verify installation
brew --version
# Should output: Homebrew 4.x.x
```

---

## Phase 3: Development Tools (20 minutes)

### 3.1 Install Git

```bash
brew install git

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git --version
# Should output: git version 2.x.x
```

### 3.2 Install Node.js and Yarn

```bash
# Install Node.js (LTS version)
brew install node

# Verify Node.js
node --version  # Should output: v20.x.x or v22.x.x
npm --version   # Should output: 10.x.x

# Install Yarn package manager
npm install -g yarn

# Verify Yarn
yarn --version  # Should output: 1.22.x
```

### 3.3 Install GitHub CLI

```bash
# Install GitHub CLI
brew install gh

# Verify
gh --version
# Should output: gh version 2.x.x

# Authenticate with GitHub
gh auth login
# → GitHub.com
# → HTTPS
# → Yes (authenticate Git)
# → Login with browser
```

### 3.4 Install Claude Code CLI

```bash
# Install Claude Code (Anthropic's CLI)
# Visit: https://claude.com/code
# Download and install Claude Code for macOS

# After installation, verify
claude --version

# Authenticate
claude auth
# Follow on-screen instructions to link your Anthropic account
```

---

## Phase 4: Repository Setup (15 minutes)

### 4.1 Create HomeCare Directory

```bash
# Create main directory for all repositories
mkdir -p ~/HomeCare
cd ~/HomeCare
```

### 4.2 Clone be-agent-service

```bash
# Clone the multi-agent orchestrator repository
git clone https://github.com/bear75/be-agent-service.git
cd be-agent-service

# Verify structure
ls -la
# Should see: agents/, dashboard/, launchd/, lib/, scripts/

# Make scripts executable
chmod +x scripts/*.sh
chmod +x agents/*.sh
chmod +x lib/*.sh
chmod +x dashboard/*.sh
```

### 4.3 Clone Target Repositories

```bash
cd ~/HomeCare

# Clone beta-appcaire (main app)
git clone https://github.com/[your-org]/beta-appcaire.git

# Future: Clone other repos as needed
# git clone https://github.com/[your-org]/cowork.git
# git clone https://github.com/[your-org]/marketing.git
```

### 4.4 Install Dependencies (beta-appcaire)

```bash
cd ~/HomeCare/beta-appcaire

# Install all monorepo dependencies
yarn install

# This will take 5-10 minutes on first install
# Grab a coffee ☕
```

---

## Phase 5: LaunchAgents Setup (10 minutes)

LaunchAgents run the automation scripts at scheduled times.

### 5.1 Copy LaunchAgent Files

```bash
cd ~/HomeCare/be-agent-service

# Copy all LaunchAgent plists to LaunchAgents directory
cp launchd/*.plist ~/Library/LaunchAgents/

# Verify
ls -la ~/Library/LaunchAgents/com.appcaire.*
# Should see:
# - com.appcaire.auto-compound.plist
# - com.appcaire.caffeinate.plist
# - com.appcaire.daily-compound-review.plist
# - com.appcaire.dashboard.plist
```

### 5.2 Load LaunchAgents

```bash
# Load all agents
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.dashboard.plist

# Verify agents are loaded
launchctl list | grep appcaire
# Should see all 4 agents listed
```

### 5.3 Schedule Overview

```
10:30 PM  - daily-compound-review   (Extract learnings from Claude threads)
11:00 PM  - auto-compound            (Auto-implement priority #1, create PR)
Always    - caffeinate               (Keep Mac awake for automation)
Always    - dashboard                (Real-time monitoring dashboard)
```

---

## Phase 6: Dashboard Setup (5 minutes)

The dashboard provides real-time monitoring of agent sessions.

### 6.1 Verify Dashboard is Running

```bash
# Check dashboard process
launchctl list | grep dashboard

# Check dashboard logs
tail -f ~/Library/Logs/appcaire-dashboard.log

# Should see:
# Multi-Agent Dashboard Server
# Server running at http://localhost:3030/
```

### 6.2 Access Dashboard

```bash
# Open in your default browser
open http://localhost:3030

# Or manually navigate to:
# http://localhost:3030
```

### 6.3 Dashboard Features

- **System Stats**: Total, running, completed, failed, blocked sessions
- **Session List**: All orchestrator sessions with real-time updates
- **Session Details**: Click any session to view:
  - Orchestrator status and phase
  - Backend, Frontend, Infrastructure specialist statuses
  - Verification results
  - Real-time logs
  - PR URLs

---

## Phase 7: Testing the System (15 minutes)

### 7.1 Create Test Priority

```bash
cd ~/HomeCare/beta-appcaire

# Create test priority file
cat > reports/priorities-$(date +%Y-%m-%d).md <<EOF
# Priority 1

**Description:** Test the multi-agent orchestrator system

**Expected outcome:**
- Verify orchestrator spawns specialists correctly
- Verify verification runs before PR
- Verify dashboard shows session in real-time

**Files:**
- Test file (this is just a test)

**Complexity:** Low
EOF

# Verify file created
cat reports/priorities-$(date +%Y-%m-%d).md
```

### 7.2 Manual Test Run

```bash
cd ~/HomeCare/beta-appcaire

# Ensure on main branch
git checkout main
git pull origin main

# Run auto-compound manually with orchestrator enabled
USE_ORCHESTRATOR=true ../be-agent-service/scripts/auto-compound.sh
```

### 7.3 Monitor Dashboard

1. **Open dashboard**: http://localhost:3030
2. **Watch real-time updates** as orchestrator runs
3. **Check session appears** with "running" status
4. **View specialist statuses** (backend, frontend, infrastructure)
5. **Click session** to see detailed logs

### 7.4 Verify Output

```bash
# Check orchestrator logs
ls -la ~/HomeCare/be-agent-service/logs/orchestrator-sessions/

# Check session state
ls -la ~/HomeCare/be-agent-service/.compound-state/

# Check if PR was created
gh pr list

# View PR
gh pr view [PR-NUMBER]
```

---

## Phase 8: Nightly Automation (Done!)

No action needed - the LaunchAgents are already configured.

### What Happens Automatically

**Every Night at 10:30 PM:**
- LaunchAgent triggers `daily-compound-review.sh`
- Scans Claude Code threads
- Extracts learnings
- Updates CLAUDE.md files
- Commits to main branch

**Every Night at 11:00 PM:**
- LaunchAgent triggers `auto-compound.sh`
- Reads latest priority from `reports/priorities-*.md`
- Creates PRD
- Creates feature branch
- **Runs orchestrator** (if `USE_ORCHESTRATOR=true`)
  - Spawns backend + infrastructure in parallel
  - Spawns frontend after backend completes
  - Runs verification
  - Creates PR (only if verification passes)
- Returns to main branch

**Every Morning:**
- **Check dashboard** at http://localhost:3030
- **Review PR** created overnight
- **Merge if good**, or provide feedback

---

## 📊 Dashboard Screenshots

### Main Dashboard
```
🤖 Multi-Agent Orchestrator
Real-time monitoring for autonomous agent workflows

┌─────────────────────────────────────────────────────┐
│  Total: 12  Running: 1  Completed: 9  Failed: 1  Blocked: 1  │
└─────────────────────────────────────────────────────┘

Recent Sessions:
┌──────────────────────────────────────────────┐
│ session-1770451234                  [RUNNING] │
│ 📁 beta-appcaire                             │
│ ⚡ Phase: phase2_frontend                    │
│ Backend: completed | Frontend: in_progress   │
└──────────────────────────────────────────────┘
```

### Session Details
```
Session Details: session-1770451234

🎯 Orchestrator
Status: in_progress
Phase: phase2_frontend
Repository: ~/HomeCare/beta-appcaire

⚙️ Backend Specialist
Status: completed
Tasks: 3 completed

🎨 Frontend Specialist
Status: in_progress
Waiting for: backend completion

✅ Verification Specialist
Status: pending
```

---

## 🔧 Configuration

### Enable Orchestrator for Nightly Runs

By default, nightly runs use the legacy `loop.sh`. To enable the orchestrator:

```bash
# Option 1: Environment variable (temporary)
export USE_ORCHESTRATOR=true

# Option 2: Edit LaunchAgent plist (permanent)
vim ~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Add to <dict>:
<key>EnvironmentVariables</key>
<dict>
    <key>USE_ORCHESTRATOR</key>
    <string>true</string>
</dict>

# Reload agent
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

### Dashboard Configuration

```bash
# Change dashboard port (default: 3030)
export DASHBOARD_PORT=8080

# Edit LaunchAgent to make permanent
vim ~/Library/LaunchAgents/com.appcaire.dashboard.plist
```

---

## 🐛 Troubleshooting

### Dashboard Not Accessible

```bash
# Check if dashboard is running
launchctl list | grep dashboard

# Check logs for errors
tail -50 ~/Library/Logs/appcaire-dashboard.log
tail -50 ~/Library/Logs/appcaire-dashboard-error.log

# Restart dashboard
launchctl unload ~/Library/LaunchAgents/com.appcaire.dashboard.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.dashboard.plist

# Access dashboard
open http://localhost:3030
```

### LaunchAgents Not Running

```bash
# Check if agents are loaded
launchctl list | grep appcaire

# If missing, load them
launchctl load ~/Library/LaunchAgents/com.appcaire.*.plist

# Check logs
tail -f ~/Library/Logs/appcaire-compound.log
tail -f ~/Library/Logs/appcaire-daily-review.log
```

### Mac Going to Sleep

```bash
# Check caffeinate agent
launchctl list | grep caffeinate

# Reload if needed
launchctl unload ~/Library/LaunchAgents/com.appcaire.caffeinate.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.caffeinate.plist

# Verify Mac stays awake
pmset -g assertions
```

### Nightly Run Didn't Execute

```bash
# Check LaunchAgent status
launchctl list | grep auto-compound

# View logs
tail -100 ~/Library/Logs/appcaire-compound.log

# Manually trigger to test
launchctl start com.appcaire.auto-compound
```

### Node.js Not Found

```bash
# Install Node.js
brew install node

# Verify installation
node --version
npm --version

# Restart dashboard
launchctl unload ~/Library/LaunchAgents/com.appcaire.dashboard.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.dashboard.plist
```

---

## 📚 Daily Workflow

### Morning Routine (5 minutes)

```bash
# 1. Open dashboard
open http://localhost:3030

# 2. Check overnight session
# - Look for latest session
# - Verify status: completed
# - Check PR was created

# 3. Review PR
gh pr list
gh pr view [NUMBER]

# 4. Merge or provide feedback
gh pr merge [NUMBER] --squash
```

### Evening Routine (5 minutes)

```bash
cd ~/HomeCare/beta-appcaire

# Create tomorrow's priority
cat > reports/priorities-$(date -v+1d +%Y-%m-%d).md <<EOF
# Priority 1

**Description:** [What to build]

**Expected outcome:**
- [Deliverable 1]
- [Deliverable 2]

**Files:**
- [Relevant files]
EOF

# That's it! System will run at 11 PM automatically
```

---

## 🎯 Next Steps

### Week 1: Familiarization
- Monitor dashboard daily
- Review automated PRs
- Get comfortable with the system

### Week 2: Optimization
- Adjust LaunchAgent schedules if needed
- Fine-tune priority file format
- Enable orchestrator for nightly runs

### Week 3: Multi-Repo
- Set up additional repos (cowork, marketing)
- Test orchestrator on different repos
- Expand automation coverage

---

## 🔐 Security Considerations

1. **Never commit .env files**: Use `.env.example` templates
2. **Rotate GitHub tokens**: Update `gh auth` periodically
3. **Review automated PRs**: Always review before merging
4. **Monitor dashboard**: Check for failed/blocked sessions
5. **Update regularly**: Keep Node.js, Claude Code, and dependencies updated

---

## 📖 Additional Resources

- **Dashboard**: http://localhost:3030
- **QUICK_START.md**: Daily reference guide
- **SETUP.md**: Detailed setup and workflows
- **GitHub Issues**: https://github.com/bear75/be-agent-service/issues

---

## ✅ Setup Complete!

You now have:
- ✅ Mac mini configured for autonomous development
- ✅ Multi-agent orchestrator running nightly
- ✅ Real-time dashboard at http://localhost:3030
- ✅ Automated PR creation with verification
- ✅ Multi-repo support ready

**Next**: Create your first priority file and let the system work overnight!

---

**Questions?** Check the dashboard logs or review QUICK_START.md for common commands.

**Enjoy autonomous development! 🚀**
