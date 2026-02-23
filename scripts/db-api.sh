#!/bin/bash

# scripts/db-api.sh
# Helper functions for interacting with the Agent Service DB API.
# Source this file from other scripts: source "$SCRIPT_DIR/../db-api.sh"

API_BASE="${AGENT_API_URL:-http://localhost:3010}"

# ─── Session Operations ──────────────────────────────────────────────────────

# Create a new session in the DB
# Usage: db_create_session <session_id> <team_id> <target_repo> [priority_file] [branch_name]
db_create_session() {
  local session_id="$1"
  local team_id="$2"
  local target_repo="$3"
  local priority_file="${4:-}"
  local branch_name="${5:-}"

  curl -s -X POST "$API_BASE/api/sessions" \
    -H "Content-Type: application/json" \
    -d "{
      \"sessionId\": \"$session_id\",
      \"teamId\": \"$team_id\",
      \"targetRepo\": \"$target_repo\",
      \"priorityFile\": \"$priority_file\",
      \"branchName\": \"$branch_name\"
    }" > /dev/null 2>&1

  echo "$session_id"
}

# Update session status
# Usage: db_update_session <session_id> <new_status> [pr_url] [exit_code]
db_update_session() {
  local sid="$1"
  local new_status="$2"
  local pr_url="${3:-}"
  local exit_code="${4:-}"

  local body="{\"status\": \"$new_status\""
  [ -n "$pr_url" ] && body="$body, \"prUrl\": \"$pr_url\""
  [ -n "$exit_code" ] && body="$body, \"exitCode\": $exit_code"
  body="$body}"

  curl -s -X PATCH "$API_BASE/api/sessions/$sid" \
    -H "Content-Type: application/json" \
    -d "$body" > /dev/null 2>&1
}

# ─── Task Operations ─────────────────────────────────────────────────────────

# Create a task for a session
# Usage: db_create_task <task_id> <session_id> <agent_id> <description> [priority]
db_create_task() {
  local _task_id="$1"
  local session_id="$2"
  local agent_id="$3"
  local description="$4"
  local priority="${5:-medium}"

  curl -s -X POST "$API_BASE/api/tasks" \
    -H "Content-Type: application/json" \
    -d "{
      \"sessionId\": \"$session_id\",
      \"agentId\": \"$agent_id\",
      \"description\": \"$(echo "$description" | sed 's/"/\\"/g')\",
      \"priority\": \"$priority\"
    }" > /dev/null 2>&1

  echo "Task $_task_id created for session $session_id"
}

# ─── Command Tracking ────────────────────────────────────────────────────────

# Track a user command for automation detection
# Usage: db_track_command <command_text> [normalized_intent] [team] [model]
db_track_command() {
  local command_text="$1"
  local normalized_intent="${2:-}"
  local team="${3:-}"
  local model="${4:-}"

  curl -s -X POST "$API_BASE/api/commands" \
    -H "Content-Type: application/json" \
    -d "{
      \"commandText\": \"$command_text\",
      \"normalizedIntent\": \"$normalized_intent\",
      \"team\": \"$team\",
      \"model\": \"$model\"
    }" > /dev/null 2>&1
}

# ─── Metrics ─────────────────────────────────────────────────────────────────

# Record a metric
# Usage: db_record_metric <entity_type> <entity_id> <metric_name> <metric_value>
db_record_metric() {
  local entity_type="$1"
  local entity_id="$2"
  local metric_name="$3"
  local metric_value="$4"

  curl -s -X POST "$API_BASE/api/metrics" \
    -H "Content-Type: application/json" \
    -d "{
      \"entityType\": \"$entity_type\",
      \"entityId\": \"$entity_id\",
      \"metricName\": \"$metric_name\",
      \"metricValue\": $metric_value
    }" > /dev/null 2>&1
}

# ─── Health Check ────────────────────────────────────────────────────────────

# Check if the API server is reachable
# Usage: db_api_available && echo "yes" || echo "no"
db_api_available() {
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/health" 2>/dev/null)
  [ "$http_code" = "200" ]
}
