#!/bin/bash
#
# Darwin Manager Agent
# Single responsibility: keep the DARWIN workspace structured per docs/DARWIN_STRUCTURE.md.
# Runs validate → archive-completed → ensure-structure → memory-to-structured.
#
# Usage:
#   ./agents/darwin-manager.sh [workspace-path]
#   ./agents/darwin-manager.sh run
#
# Optional env: DARWIN_WORKSPACE_PATH to override workspace path.
# Can be triggered by orchestrator, launchd, or Telegram.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Repo root (be-agents-service): script lives in agents/
SERVICE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DARWIN_SCRIPTS="$SERVICE_ROOT/scripts/darwin"

WORKSPACE_PATH="${1:-}"
if [[ "$WORKSPACE_PATH" == "run" ]]; then
  WORKSPACE_PATH=""
fi
if [[ -z "$WORKSPACE_PATH" ]] && [[ -n "${DARWIN_WORKSPACE_PATH:-}" ]]; then
  WORKSPACE_PATH="$DARWIN_WORKSPACE_PATH"
fi
if [[ -z "$WORKSPACE_PATH" ]]; then
  source "$SERVICE_ROOT/scripts/workspace/resolve-workspace.sh"
  WORKSPACE_PATH=$(get_workspace_path "darwin")
fi
WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"

echo "[Darwin Manager] Workspace: ${WORKSPACE_PATH:-<not set>}"

if [[ -z "$WORKSPACE_PATH" || ! -d "$WORKSPACE_PATH" ]]; then
  echo "[Darwin Manager] No DARWIN workspace found. Set DARWIN_WORKSPACE_PATH or configure darwin in config/repos.yaml."
  exit 1
fi

# 1) Validate (report only; do not fail run)
"$DARWIN_SCRIPTS/validate-structure.sh" "$WORKSPACE_PATH" || true

# 2) Archive completed inbox and duplicate check-ins
"$DARWIN_SCRIPTS/archive-completed.sh" "$WORKSPACE_PATH"

# 3) Ensure dirs and template files exist
"$DARWIN_SCRIPTS/ensure-structure.sh" "$WORKSPACE_PATH"

# 4) Convert memory/*.md → memory/*.json (machine-readable)
node "$DARWIN_SCRIPTS/memory-to-structured.js" "$WORKSPACE_PATH"

echo "[Darwin Manager] Done."
