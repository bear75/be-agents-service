# Multi-Agent Dashboard

Real-time monitoring dashboard for the autonomous multi-agent orchestrator system.

## Quick Start

```bash
# Start dashboard
./start.sh

# Access dashboard
open http://localhost:3030
```

## Features

- **Real-time Updates**: Auto-refreshes every 3 seconds
- **System Stats**: Total, running, completed, failed, blocked sessions
- **Session List**: All orchestrator sessions sorted by time
- **Session Details**: Click any session to view:
  - Orchestrator status and phase
  - Backend, Frontend, Infrastructure specialist statuses
  - Verification results and blockers
  - Real-time logs from all agents
  - PR URLs
- **Beautiful UI**: Modern, responsive design with status colors

## API Endpoints

- `GET /api/sessions` - List all sessions
- `GET /api/sessions/:id` - Get session details
- `GET /api/logs/:id` - Get session logs
- `GET /api/stats` - Get system statistics

## Configuration

```bash
# Change port (default: 3030)
export DASHBOARD_PORT=8080
./start.sh
```

## Auto-Start with LaunchAgent

```bash
# Copy LaunchAgent plist
cp ../launchd/com.appcaire.dashboard.plist ~/Library/LaunchAgents/

# Load agent
launchctl load ~/Library/LaunchAgents/com.appcaire.dashboard.plist

# Dashboard will now start automatically on login
```

## Requirements

- Node.js 14+ (no additional dependencies needed - uses only Node.js built-in modules)

## Architecture

```
dashboard/
├── server.js           # Node.js HTTP server (no framework)
├── public/
│   ├── index.html      # Dashboard UI
│   ├── style.css       # Styling
│   └── app.js          # Frontend JavaScript
├── start.sh            # Start script
└── README.md           # This file
```

## Development

The dashboard is intentionally simple:
- **No frameworks**: Pure Node.js, HTML, CSS, JavaScript
- **No build step**: Runs directly
- **No dependencies**: Uses only Node.js built-in modules (`http`, `fs`, `path`, `url`)
- **Lightweight**: Fast startup, minimal resource usage

## Troubleshooting

### Dashboard Won't Start

```bash
# Check if Node.js is installed
node --version

# Check if port 3030 is in use
lsof -i :3030

# Check logs
tail -f ~/Library/Logs/appcaire-dashboard.log
```

### No Sessions Showing

```bash
# Check if .compound-state directory exists
ls -la ../.compound-state/

# Run a test session
cd ~/HomeCare/beta-appcaire
USE_ORCHESTRATOR=true ../be-agent-service/scripts/auto-compound.sh

# Dashboard will update automatically
```

### Dashboard Not Auto-Starting

```bash
# Check if LaunchAgent is loaded
launchctl list | grep dashboard

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.appcaire.dashboard.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.dashboard.plist
```

## Screenshots

### Main Dashboard
Shows system stats and recent sessions with real-time status indicators.

### Session Details Modal
Click any session to view detailed information about all specialists, logs, and verification results.

## Notes

- Dashboard is **read-only** - it monitors sessions but doesn't control them
- Updates automatically every 3 seconds
- Shows last 100 log lines per agent
- Sessions are sorted newest first
- Status colors: 🟢 Completed, 🟣 Running, 🔴 Failed, 🟡 Blocked

## Support

See parent directory's QUICK_START.md and MAC_MINI_SETUP.md for full documentation.
