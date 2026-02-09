# Simple OpenClaw Integration (2 Steps)

Since OpenClaw is already working on your Mac mini, you just need to connect it to the workspace.

## Step 1: Add Workspace Tools to OpenClaw

On the **Mac mini**, edit your OpenClaw config:

```bash
vim ~/.openclaw/openclaw.json
```

Add this `mcpServers` section (merge with existing config):

```json
{
  "mcpServers": {
    "agent-workspace": {
      "command": "npx",
      "args": [
        "tsx",
        "/Users/bjornevers_MacPro/HomeCare/be-agent-service/apps/openclaw-bridge/src/index.ts"
      ],
      "env": {
        "WORKSPACE_REPO": "beta-appcaire",
        "WORKSPACE_CONFIG": "/Users/bjornevers_MacPro/HomeCare/be-agent-service/config/repos.yaml"
      }
    }
  }
}
```

**Or copy our template:**
```bash
# Copy the full config
cp ~/HomeCare/be-agent-service/config/openclaw/openclaw.json ~/.openclaw/openclaw.json

# Edit to add your Telegram token/user ID
vim ~/.openclaw/openclaw.json
```

## Step 2: Restart OpenClaw

```bash
openclaw restart
```

## Test It!

Now try in Telegram:
- **"status"** → Should show workspace overview
- **"what's in my inbox?"** → Shows inbox items
- **"add to inbox: test idea"** → Adds to workspace
- **"run agent now"** → Triggers agent immediately

## The Loop is Closed!

```
You (Telegram) 
  ↓ "add priority: fix bug"
OpenClaw (writes to workspace)
  ↓
Agent Service (reads workspace, executes)
  ↓
Workspace (writes results)
  ↓
Morning Briefing (8 AM) → Telegram
  "✅ Agent completed! PR created"
```

Done! 🎉
