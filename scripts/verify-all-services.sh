#!/usr/bin/env bash
# End-to-end service verification for Darwin/OpenClaw/Telegram stack.
#
# Checks:
# - Dashboard/API health (3010/3030)
# - Workspace API endpoints
# - OpenClaw config + runtime status
# - Telegram token/chat/send
# - launchd jobs (macOS)
# - Notification/compound script syntax and executability
#
# Usage:
#   ./scripts/verify-all-services.sh
#   ./scripts/verify-all-services.sh --send-telegram-test
#   ./scripts/verify-all-services.sh --darwin-url http://localhost:3010 --strict

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESOLVER_SCRIPT="$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
CAIRE_ENV="$HOME/.config/caire/env"

REPO_NAME="appcaire"
DARWIN_URL=""
STRICT=false
SEND_TELEGRAM_TEST=false

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

ok() {
  echo "✅ $*"
  ((PASS_COUNT += 1))
}

warn() {
  echo "⚠️  $*"
  ((WARN_COUNT += 1))
}

fail() {
  echo "❌ $*"
  ((FAIL_COUNT += 1))
}

section() {
  echo ""
  echo "=== $* ==="
}

usage() {
  cat <<'EOF'
Usage: ./scripts/verify-all-services.sh [options]

Options:
  --repo <name>             Repo key for workspace checks (default: appcaire)
  --darwin-url <url>        Darwin base URL (default: auto-detect 3010 -> 3030)
  --send-telegram-test      Send a test Telegram message
  --strict                  Exit non-zero on warnings as well
  -h, --help                Show this help
EOF
}

expand_home_path() {
  local p="${1:-}"
  p="${p/#\~/$HOME}"
  p="${p%/}"
  echo "$p"
}

require_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "Command available: $cmd"
  else
    fail "Missing required command: $cmd"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_NAME="${2:-}"
      shift 2
      ;;
    --darwin-url)
      DARWIN_URL="${2:-}"
      shift 2
      ;;
    --send-telegram-test)
      SEND_TELEGRAM_TEST=true
      shift
      ;;
    --strict)
      STRICT=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

section "Prerequisites"
require_cmd "curl"
require_cmd "jq"
require_cmd "bash"

if [[ -f "$CAIRE_ENV" ]]; then
  # shellcheck source=/dev/null
  source "$CAIRE_ENV" || true
  ok "Loaded env file: $CAIRE_ENV"
else
  warn "Env file not found: $CAIRE_ENV"
fi

section "Dashboard and API"
ACTIVE_DARWIN_URL=""
if [[ -n "$DARWIN_URL" ]]; then
  CANDIDATES=("$DARWIN_URL")
else
  CANDIDATES=("http://localhost:3010" "http://localhost:3030")
fi

for candidate in "${CANDIDATES[@]}"; do
  health="$(curl -fsS "$candidate/health" 2>/dev/null || true)"
  if [[ -n "$health" ]] && echo "$health" | jq -e '.success == true' >/dev/null 2>&1; then
    ACTIVE_DARWIN_URL="$candidate"
    ok "Darwin health OK: $candidate/health"
    break
  fi
done

if [[ -z "$ACTIVE_DARWIN_URL" ]]; then
  fail "Darwin server is not healthy on tested URLs: ${CANDIDATES[*]}"
else
  if curl -fsS "$ACTIVE_DARWIN_URL/api/schedule-runs?dataset=huddinge-2w-expanded" \
    | jq -e '.success == true' >/dev/null 2>&1; then
    ok "Schedule runs API reachable"
  else
    fail "Schedule runs API failed: $ACTIVE_DARWIN_URL/api/schedule-runs"
  fi

  if curl -fsS "$ACTIVE_DARWIN_URL/api/workspace/darwin/status" \
    | jq -e '.success == true' >/dev/null 2>&1; then
    ok "Workspace status API reachable"
  else
    warn "Workspace status API failed for darwin"
  fi
fi

section "OpenClaw"
if [[ -f "$OPENCLAW_CONFIG" ]]; then
  ok "OpenClaw config exists: $OPENCLAW_CONFIG"
else
  fail "OpenClaw config missing: $OPENCLAW_CONFIG"
fi

if [[ -f "$OPENCLAW_CONFIG" ]]; then
  if grep -qE 'YOUR_TELEGRAM_USER_ID|YOUR_TELEGRAM_BOT_TOKEN' "$OPENCLAW_CONFIG"; then
    fail "OpenClaw config still has Telegram placeholders"
  else
    ok "OpenClaw config has no Telegram placeholders"
  fi

  openclaw_workspace="$(
    grep -Eo '"workspace"\s*:\s*"[^"]+"|workspace:\s*"[^"]+"' "$OPENCLAW_CONFIG" 2>/dev/null \
      | head -1 \
      | sed -E 's/.*"([^"]+)".*/\1/' \
      || true
  )"
  openclaw_workspace="$(expand_home_path "$openclaw_workspace")"
  if [[ -z "$openclaw_workspace" ]]; then
    warn "Could not parse OpenClaw workspace path from config"
  else
    ok "OpenClaw workspace parsed: $openclaw_workspace"
  fi

  if [[ -f "$RESOLVER_SCRIPT" ]]; then
    # shellcheck source=/dev/null
    source "$RESOLVER_SCRIPT"
    darwin_workspace="$(expand_home_path "$(get_workspace_path darwin 2>/dev/null || true)")"
    if [[ -n "$darwin_workspace" ]]; then
      if [[ "$darwin_workspace" == "$openclaw_workspace" ]]; then
        ok "OpenClaw workspace matches darwin workspace path"
      else
        fail "Workspace mismatch: openclaw='$openclaw_workspace' darwin='$darwin_workspace'"
      fi
    else
      warn "Could not resolve darwin workspace path from repos.yaml"
    fi
  fi
fi

if command -v openclaw >/dev/null 2>&1; then
  ok "OpenClaw CLI is installed"
else
  fail "OpenClaw CLI not found in PATH"
fi

if command -v launchctl >/dev/null 2>&1; then
  if launchctl list 2>/dev/null | grep -Eq 'ai\.openclaw\.gateway'; then
    ok "OpenClaw gateway launchd job is loaded"
  else
    warn "OpenClaw gateway launchd job not loaded (ai.openclaw.gateway)"
  fi
else
  warn "launchctl not found (non-macOS environment); skipping launchd checks"
fi

section "Telegram"
if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  ok "TELEGRAM_BOT_TOKEN is set"
else
  fail "TELEGRAM_BOT_TOKEN is not set"
fi

if [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  ok "TELEGRAM_CHAT_ID is set"
else
  fail "TELEGRAM_CHAT_ID is not set"
fi

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  get_me="$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" || echo '{"ok":false}')"
  if echo "$get_me" | jq -e '.ok == true' >/dev/null 2>&1; then
    ok "Telegram bot token is valid (getMe OK)"
  else
    desc="$(echo "$get_me" | jq -r '.description // "unknown error"' 2>/dev/null || echo "unknown error")"
    fail "Telegram getMe failed: $desc"
  fi
fi

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  get_chat="$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChat?chat_id=${TELEGRAM_CHAT_ID}" || echo '{"ok":false}')"
  if echo "$get_chat" | jq -e '.ok == true' >/dev/null 2>&1; then
    ok "Telegram chat ID is valid (getChat OK)"
  else
    desc="$(echo "$get_chat" | jq -r '.description // "unknown error"' 2>/dev/null || echo "unknown error")"
    fail "Telegram getChat failed: $desc"
  fi

  if [[ "$SEND_TELEGRAM_TEST" == "true" ]]; then
    test_msg="✅ Darwin service test $(date +'%Y-%m-%d %H:%M:%S')"
    send_resp="$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${test_msg}" \
      -d "disable_notification=true" \
      || echo '{"ok":false}')"
    if echo "$send_resp" | jq -e '.ok == true' >/dev/null 2>&1; then
      ok "Telegram sendMessage test succeeded"
    else
      desc="$(echo "$send_resp" | jq -r '.description // "unknown error"' 2>/dev/null || echo "unknown error")"
      fail "Telegram sendMessage test failed: $desc"
    fi
  else
    warn "Telegram send test skipped (use --send-telegram-test)"
  fi
fi

section "macOS launchd jobs"
if command -v launchctl >/dev/null 2>&1; then
  required_jobs=(
    "com.appcaire.agent-server"
    "com.appcaire.auto-compound"
    "com.appcaire.daily-compound-review"
    "com.appcaire.morning-briefing"
    "com.appcaire.weekly-review"
  )
  for label in "${required_jobs[@]}"; do
    if launchctl list 2>/dev/null | grep -Fq "$label"; then
      ok "launchd job loaded: $label"
    else
      if [[ "$label" == "com.appcaire.agent-server" ]]; then
        fail "Critical launchd job missing: $label"
      else
        warn "launchd job not loaded: $label"
      fi
    fi
  done
else
  warn "launchctl not available; skipping launchd checks"
fi

section "Script sanity"
critical_scripts=(
  "$SERVICE_ROOT/scripts/restart-darwin.sh"
  "$SERVICE_ROOT/scripts/setup-telegram-openclaw.sh"
  "$SERVICE_ROOT/scripts/notifications/morning-briefing.sh"
  "$SERVICE_ROOT/scripts/notifications/weekly-review.sh"
  "$SERVICE_ROOT/scripts/notifications/session-complete.sh"
  "$SERVICE_ROOT/scripts/compound/auto-compound.sh"
  "$SERVICE_ROOT/scripts/compound/daily-compound-review.sh"
)

for script in "${critical_scripts[@]}"; do
  if [[ -f "$script" ]]; then
    ok "Script exists: ${script#$SERVICE_ROOT/}"
    if [[ -x "$script" ]]; then
      ok "Executable: ${script#$SERVICE_ROOT/}"
    else
      warn "Not executable: ${script#$SERVICE_ROOT/}"
    fi
    if bash -n "$script" 2>/dev/null; then
      ok "Syntax OK: ${script#$SERVICE_ROOT/}"
    else
      fail "Syntax error: ${script#$SERVICE_ROOT/}"
    fi
  else
    fail "Missing script: ${script#$SERVICE_ROOT/}"
  fi
done

section "Summary"
echo "Passed:   $PASS_COUNT"
echo "Warnings: $WARN_COUNT"
echo "Failed:   $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo "Result: FAILED"
  exit 1
fi

if [[ "$STRICT" == "true" && "$WARN_COUNT" -gt 0 ]]; then
  echo "Result: FAILED (strict mode, warnings present)"
  exit 1
fi

echo "Result: OK"
exit 0
