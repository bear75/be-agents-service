#!/bin/bash
#
# State Manager - Agent coordination via JSON state files
# Enables multi-agent workflows with shared state and feedback
#

set -euo pipefail

# State directory for current session
STATE_DIR="${COMPOUND_STATE_DIR:-.compound-state}"

#
# Initialize a new agent session
# Creates state directory and session metadata
#
# Args:
#   $1 - Session ID (typically timestamp or UUID)
#
# Example:
#   init_session "session-$(date +%s)"
#
init_session() {
  local session_id="${1:-}"

  if [[ -z "$session_id" ]]; then
    echo "Error: Session ID required" >&2
    return 1
  fi

  local session_dir="$STATE_DIR/$session_id"
  mkdir -p "$session_dir"

  # Create session metadata
  cat > "$session_dir/session.json" <<EOF
{
  "sessionId": "$session_id",
  "createdAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "active",
  "agents": []
}
EOF

  echo "$session_dir"
}

#
# Write agent state to JSON file
# Merges with existing state if present
#
# Args:
#   $1 - Session ID
#   $2 - Agent name (e.g., "orchestrator", "backend", "verification")
#   $3 - JSON state (must be valid JSON string)
#
# Example:
#   write_state "session-123" "backend" '{"status": "in_progress", "tasks": []}'
#
write_state() {
  local session_id="${1:-}"
  local agent_name="${2:-}"
  local state_json="${3:-}"

  if [[ -z "$session_id" || -z "$agent_name" || -z "$state_json" ]]; then
    echo "Error: Session ID, agent name, and state JSON required" >&2
    return 1
  fi

  local session_dir="$STATE_DIR/$session_id"
  local state_file="$session_dir/${agent_name}.json"

  # Validate JSON
  if ! echo "$state_json" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON state" >&2
    return 1
  fi

  # Create directory if needed
  mkdir -p "$session_dir"

  # Write state with timestamp
  local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "$state_json" | jq --arg ts "$timestamp" '. + {updatedAt: $ts}' > "$state_file"

  # Update session metadata with agent registration
  if [[ -f "$session_dir/session.json" ]]; then
    jq --arg agent "$agent_name" '
      if (.agents | index($agent)) == null then
        .agents += [$agent]
      else
        .
      end
    ' "$session_dir/session.json" > "$session_dir/session.json.tmp"
    mv "$session_dir/session.json.tmp" "$session_dir/session.json"
  fi

  echo "$state_file"
}

#
# Read agent state from JSON file
# Returns empty object if file doesn't exist
#
# Args:
#   $1 - Session ID
#   $2 - Agent name
#   $3 - Optional jq query (default: ".")
#
# Example:
#   read_state "session-123" "backend"
#   read_state "session-123" "backend" ".status"
#
read_state() {
  local session_id="${1:-}"
  local agent_name="${2:-}"
  local query="${3:-.}"

  if [[ -z "$session_id" || -z "$agent_name" ]]; then
    echo "Error: Session ID and agent name required" >&2
    return 1
  fi

  local state_file="$STATE_DIR/$session_id/${agent_name}.json"

  if [[ ! -f "$state_file" ]]; then
    echo "{}"
    return 0
  fi

  jq -r "$query" "$state_file"
}

#
# Update specific field in agent state
# Uses jq to perform atomic update
#
# Args:
#   $1 - Session ID
#   $2 - Agent name
#   $3 - Field path (jq syntax, e.g., ".status" or ".tasks[0].completed")
#   $4 - New value (will be JSON-encoded)
#
# Example:
#   update_state "session-123" "backend" ".status" "completed"
#   update_state "session-123" "backend" ".tasks" '["task1", "task2"]'
#
update_state() {
  local session_id="${1:-}"
  local agent_name="${2:-}"
  local field_path="${3:-}"
  local new_value="${4:-}"

  if [[ -z "$session_id" || -z "$agent_name" || -z "$field_path" ]]; then
    echo "Error: Session ID, agent name, and field path required" >&2
    return 1
  fi

  local state_file="$STATE_DIR/$session_id/${agent_name}.json"

  # Read current state or create empty object
  local current_state="{}"
  if [[ -f "$state_file" ]]; then
    current_state=$(cat "$state_file")
  fi

  # Update field
  local updated_state
  updated_state=$(echo "$current_state" | jq --arg val "$new_value" "${field_path} = \$val")

  # Write back
  write_state "$session_id" "$agent_name" "$updated_state"
}

#
# Wait for agent to reach specific status
# Polls state file until condition is met or timeout
#
# Args:
#   $1 - Session ID
#   $2 - Agent name
#   $3 - Expected status value
#   $4 - Timeout in seconds (default: 300)
#
# Returns:
#   0 if condition met, 1 if timeout
#
# Example:
#   wait_for_status "session-123" "backend" "completed" 600
#
wait_for_status() {
  local session_id="${1:-}"
  local agent_name="${2:-}"
  local expected_status="${3:-}"
  local timeout="${4:-300}"

  if [[ -z "$session_id" || -z "$agent_name" || -z "$expected_status" ]]; then
    echo "Error: Session ID, agent name, and expected status required" >&2
    return 1
  fi

  local elapsed=0
  local poll_interval=2

  while [[ $elapsed -lt $timeout ]]; do
    local current_status
    current_status=$(read_state "$session_id" "$agent_name" ".status" 2>/dev/null || echo "unknown")

    if [[ "$current_status" == "$expected_status" ]]; then
      return 0
    fi

    sleep $poll_interval
    elapsed=$((elapsed + poll_interval))
  done

  echo "Error: Timeout waiting for $agent_name to reach status: $expected_status" >&2
  return 1
}

#
# Get all agent names in session
# Returns JSON array of agent names
#
# Args:
#   $1 - Session ID
#
# Example:
#   get_agents "session-123"
#
get_agents() {
  local session_id="${1:-}"

  if [[ -z "$session_id" ]]; then
    echo "Error: Session ID required" >&2
    return 1
  fi

  local session_file="$STATE_DIR/$session_id/session.json"

  if [[ ! -f "$session_file" ]]; then
    echo "[]"
    return 0
  fi

  jq -r '.agents[]' "$session_file"
}

#
# Clean up old sessions
# Removes session directories older than specified days
#
# Args:
#   $1 - Days to keep (default: 7)
#
# Example:
#   cleanup_sessions 14
#
cleanup_sessions() {
  local days_to_keep="${1:-7}"

  if [[ ! -d "$STATE_DIR" ]]; then
    return 0
  fi

  find "$STATE_DIR" -maxdepth 1 -type d -mtime +"$days_to_keep" -exec rm -rf {} \;

  echo "Cleaned up sessions older than $days_to_keep days"
}

# Export functions for use in other scripts
export -f init_session
export -f write_state
export -f read_state
export -f update_state
export -f wait_for_status
export -f get_agents
export -f cleanup_sessions
