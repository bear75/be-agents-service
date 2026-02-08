#!/bin/bash
#
# Initialize Shared Markdown Workspace
# Creates the directory structure and template files for a repo's workspace.
#
# Usage:
#   ./scripts/workspace/init-workspace.sh <repo-name>
#   ./scripts/workspace/init-workspace.sh beta-appcaire
#
# The workspace path is read from config/repos.yaml.
# If no workspace is configured, you can pass a path as the second argument:
#   ./scripts/workspace/init-workspace.sh beta-appcaire ~/path/to/workspace
#
# This script is idempotent — it will NOT overwrite existing files.
#

set -euo pipefail

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"
CONFIG_FILE="$SERVICE_ROOT/config/repos.yaml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[workspace]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[workspace]${NC} $1"; }
log_step()  { echo -e "${BLUE}[workspace]${NC} $1"; }

# ─── Parse arguments ──────────────────────────────────────────────────────────

REPO_NAME="${1:-}"
WORKSPACE_OVERRIDE="${2:-}"

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name> [workspace-path]"
  echo ""
  echo "Examples:"
  echo "  $0 beta-appcaire"
  echo "  $0 beta-appcaire ~/iCloud/AgentWorkspace/beta-appcaire"
  exit 1
fi

# ─── Resolve workspace path ──────────────────────────────────────────────────

if [[ -n "$WORKSPACE_OVERRIDE" ]]; then
  # Use override path
  WORKSPACE_PATH="${WORKSPACE_OVERRIDE/#\~/$HOME}"
elif [[ -f "$CONFIG_FILE" ]]; then
  # Read from config
  WORKSPACE_PATH=$(grep -A 20 "^  $REPO_NAME:" "$CONFIG_FILE" \
    | grep -A 5 "workspace:" \
    | grep "path:" \
    | head -1 \
    | sed 's/.*path: *//' \
    | sed "s|~|$HOME|")
fi

if [[ -z "${WORKSPACE_PATH:-}" ]]; then
  echo "❌ No workspace path found for '$REPO_NAME'"
  echo ""
  echo "Either:"
  echo "  1. Add workspace config to config/repos.yaml:"
  echo "     workspace:"
  echo "       path: ~/path/to/workspace"
  echo "       enabled: true"
  echo ""
  echo "  2. Pass path as second argument:"
  echo "     $0 $REPO_NAME ~/path/to/workspace"
  exit 1
fi

log_info "Initializing workspace for: $REPO_NAME"
log_info "Path: $WORKSPACE_PATH"
echo ""

# ─── Create directory structure ──────────────────────────────────────────────

log_step "Creating directory structure..."

DIRS=(
  "$WORKSPACE_PATH"
  "$WORKSPACE_PATH/check-ins"
  "$WORKSPACE_PATH/check-ins/daily"
  "$WORKSPACE_PATH/check-ins/weekly"
  "$WORKSPACE_PATH/check-ins/monthly"
  "$WORKSPACE_PATH/memory"
  "$WORKSPACE_PATH/agent-reports"
)

for dir in "${DIRS[@]}"; do
  if [[ ! -d "$dir" ]]; then
    mkdir -p "$dir"
    log_info "  Created: ${dir#$WORKSPACE_PATH/}"
  else
    log_warn "  Exists:  ${dir#$WORKSPACE_PATH/}"
  fi
done

echo ""

# ─── Copy template files (without overwriting) ──────────────────────────────

log_step "Setting up template files..."

copy_template() {
  local src="$1"
  local dest="$2"
  local name="${dest#$WORKSPACE_PATH/}"

  if [[ ! -f "$dest" ]]; then
    cp "$src" "$dest"
    log_info "  Created: $name"
  else
    log_warn "  Exists:  $name (not overwritten)"
  fi
}

# Root-level files
copy_template "$TEMPLATES_DIR/inbox.md"      "$WORKSPACE_PATH/inbox.md"
copy_template "$TEMPLATES_DIR/priorities.md"  "$WORKSPACE_PATH/priorities.md"
copy_template "$TEMPLATES_DIR/tasks.md"       "$WORKSPACE_PATH/tasks.md"
copy_template "$TEMPLATES_DIR/follow-ups.md"  "$WORKSPACE_PATH/follow-ups.md"

# Memory files
copy_template "$TEMPLATES_DIR/decisions.md"   "$WORKSPACE_PATH/memory/decisions.md"
copy_template "$TEMPLATES_DIR/learnings.md"   "$WORKSPACE_PATH/memory/learnings.md"
copy_template "$TEMPLATES_DIR/context.md"     "$WORKSPACE_PATH/memory/context.md"

echo ""

# ─── Create today's daily check-in ──────────────────────────────────────────

log_step "Creating today's daily check-in..."

TODAY=$(date +%Y-%m-%d)
TODAY_DISPLAY=$(date +"%A, %b %-d, %Y")
DAILY_FILE="$WORKSPACE_PATH/check-ins/daily/$TODAY.md"

if [[ ! -f "$DAILY_FILE" ]]; then
  sed "s/__DATE_DISPLAY__/$TODAY_DISPLAY/" "$TEMPLATES_DIR/daily-checkin.md" > "$DAILY_FILE"
  log_info "  Created: check-ins/daily/$TODAY.md"
else
  log_warn "  Exists:  check-ins/daily/$TODAY.md"
fi

echo ""

# ─── Summary ────────────────────────────────────────────────────────────────

log_info "=========================================="
log_info "Workspace initialized!"
log_info "=========================================="
echo ""
echo "  📝  $WORKSPACE_PATH/"
echo "  ├── inbox.md              ← Drop ideas here"
echo "  ├── priorities.md         ← Agent picks #1 nightly"
echo "  ├── tasks.md              ← Track active work"
echo "  ├── follow-ups.md         ← Revisit later"
echo "  ├── check-ins/"
echo "  │   ├── daily/            ← Daily notes"
echo "  │   ├── weekly/           ← Weekly reviews"
echo "  │   └── monthly/          ← Monthly planning"
echo "  ├── memory/"
echo "  │   ├── decisions.md      ← Key decisions"
echo "  │   ├── learnings.md      ← Accumulated learnings"
echo "  │   └── context.md        ← Background for agents"
echo "  └── agent-reports/        ← Agent session summaries"
echo ""
echo "Next steps:"
echo "  1. Edit priorities.md with your actual priorities"
echo "  2. Add project context to memory/context.md"
echo "  3. Drop ideas in inbox.md (or text your bot!)"
echo ""
