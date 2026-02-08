#!/bin/bash
#
# Resolve workspace path from config/repos.yaml
#
# Usage:
#   source scripts/workspace/resolve-workspace.sh
#   WORKSPACE_PATH=$(get_workspace_path "beta-appcaire")
#

# Get the directory where this script lives
_RESOLVE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_RESOLVE_SERVICE_ROOT="$(cd "$_RESOLVE_SCRIPT_DIR/../.." && pwd)"
_RESOLVE_CONFIG_FILE="$_RESOLVE_SERVICE_ROOT/config/repos.yaml"

# Get workspace path for a repo from config
# Returns empty string if not configured
get_workspace_path() {
  local repo_name="${1:-}"

  if [[ -z "$repo_name" ]]; then
    echo ""
    return 1
  fi

  if [[ ! -f "$_RESOLVE_CONFIG_FILE" ]]; then
    echo ""
    return 1
  fi

  local workspace_enabled
  workspace_enabled=$(grep -A 20 "^  $repo_name:" "$_RESOLVE_CONFIG_FILE" \
    | grep -A 5 "workspace:" \
    | grep "enabled:" \
    | head -1 \
    | sed 's/.*enabled: *//')

  if [[ "$workspace_enabled" != "true" ]]; then
    echo ""
    return 1
  fi

  local workspace_path
  workspace_path=$(grep -A 20 "^  $repo_name:" "$_RESOLVE_CONFIG_FILE" \
    | grep -A 5 "workspace:" \
    | grep "path:" \
    | head -1 \
    | sed 's/.*path: *//' \
    | sed "s|~|$HOME|")

  echo "$workspace_path"
}

# Get templates directory
get_templates_dir() {
  echo "$_RESOLVE_SCRIPT_DIR/templates"
}
