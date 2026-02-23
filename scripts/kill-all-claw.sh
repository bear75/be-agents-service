#!/usr/bin/env bash
# Disable WhatsApp only on this machine. Telegram stays running.
# Removes WhatsApp from gateway config and restarts the gateway so it runs Telegram-only.
# Does NOT kill the gateway, uninstall packages, or delete config.
#
# Usage: ./scripts/kill-all-claw.sh

set -e

echo "=== Disabling WhatsApp only (Telegram will keep working) ==="

# Remove WhatsApp from OpenClaw config (~/.openclaw/openclaw.json)
if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
  BACKUP="$HOME/.openclaw/openclaw.json.bak.no-whatsapp"
  node -e "
    const fs = require('fs');
    const path = process.env.CONFIG;
    const backup = process.env.BACKUP;
    let data;
    try { data = JSON.parse(fs.readFileSync(path, 'utf8')); } catch (e) { process.exit(1); }
    if (!data.channels || !data.channels.whatsapp) { process.exit(2); }
    fs.writeFileSync(backup, fs.readFileSync(path));
    delete data.channels.whatsapp;
    fs.writeFileSync(path, JSON.stringify(data, null, 2));
    console.log('Removed WhatsApp from OpenClaw config. Backup: ' + backup);
  " CONFIG="$HOME/.openclaw/openclaw.json" BACKUP="$BACKUP" 2>/dev/null && echo "Updated ~/.openclaw/openclaw.json (WhatsApp removed)" || true
fi

# Remove WhatsApp from Clawdbot config (~/.clawdbot/clawdbot.json)
if [[ -f "$HOME/.clawdbot/clawdbot.json" ]]; then
  BACKUP="$HOME/.clawdbot/clawdbot.json.bak.no-whatsapp"
  node -e "
    const fs = require('fs');
    const path = process.env.CONFIG;
    const backup = process.env.BACKUP;
    let data;
    try { data = JSON.parse(fs.readFileSync(path, 'utf8')); } catch (e) { process.exit(1); }
    if (data.channels && data.channels.whatsapp) { fs.writeFileSync(backup, fs.readFileSync(path)); delete data.channels.whatsapp; fs.writeFileSync(path, JSON.stringify(data, null, 2)); }
    else if (data.whatsapp) { fs.writeFileSync(backup, fs.readFileSync(path)); delete data.whatsapp; fs.writeFileSync(path, JSON.stringify(data, null, 2)); }
    else { process.exit(2); }
  " CONFIG="$HOME/.clawdbot/clawdbot.json" BACKUP="$BACKUP" 2>/dev/null && echo "Updated ~/.clawdbot/clawdbot.json (WhatsApp removed)" || true
fi

# Restart gateway so it picks up config (Telegram keeps working)
if launchctl list 2>/dev/null | grep -q com.clawdbot.gateway; then
  echo "Restarting gateway (Telegram will stay up)..."
  launchctl kickstart -k "gui/$(id -u)/com.clawdbot.gateway" 2>/dev/null || true
fi
if launchctl list 2>/dev/null | grep -q ai.openclaw.gateway; then
  echo "Restarting OpenClaw gateway (Telegram will stay up)..."
  launchctl kickstart -k "gui/$(id -u)/ai.openclaw.gateway" 2>/dev/null || true
fi

echo ""
echo "Done. WhatsApp is disabled. Telegram is unchanged and keeps working."
echo "Run this script on every machine where the bot runs (e.g. Mac mini) if you use WhatsApp there too."
