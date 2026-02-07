#!/bin/bash
#
# Parallel Executor - Spawn and manage parallel agent execution
# Enables backend + infrastructure to run simultaneously
#

#
# Spawn agent in background
# Args:
#   $1 - Agent script path
#   $2 - Session ID
#   $3 - Target repo
#   $4 - Priority file
#   $5 - Log file
#
spawn_agent() {
  local agent_script="$1"
  local session_id="$2"
  local target_repo="$3"
  local priority_file="$4"
  local log_file="$5"

  if [[ ! -f "$agent_script" ]]; then
    echo "ERROR: Agent script not found: $agent_script"
    return 1
  fi

  echo "Spawning agent: $(basename "$agent_script")..."

  # Run agent in background
  "$agent_script" "$session_id" "$target_repo" "$priority_file" >> "$log_file" 2>&1 &
  local pid=$!

  echo "$pid"
}

#
# Wait for multiple agents to complete
# Args:
#   $@ - Array of PIDs to wait for
#
# Returns:
#   0 if all agents completed successfully
#   1 if any agent failed
#
wait_for_agents() {
  local pids=("$@")
  local failed=0

  echo "Waiting for ${#pids[@]} agents to complete..."

  for pid in "${pids[@]}"; do
    if wait "$pid"; then
      echo "✓ Agent $pid completed successfully"
    else
      exit_code=$?
      echo "✗ Agent $pid failed (exit code: $exit_code)"
      failed=$((failed + 1))
    fi
  done

  if [[ $failed -gt 0 ]]; then
    echo "ERROR: $failed agent(s) failed"
    return 1
  fi

  echo "✓ All agents completed successfully"
  return 0
}

#
# Check if agent should be spawned based on priority content
# Args:
#   $1 - Agent name ("backend", "frontend", "infrastructure")
#   $2 - Priority file path
#
# Returns:
#   0 if agent should run
#   1 if agent should be skipped
#
should_spawn_agent() {
  local agent_name="$1"
  local priority_file="$2"

  if [[ ! -f "$priority_file" ]]; then
    echo "WARNING: Priority file not found: $priority_file"
    return 1
  fi

  local priority_content=$(cat "$priority_file")

  case "$agent_name" in
    backend)
      # Backend if: schema, database, migration, graphql, resolver, prisma
      if echo "$priority_content" | grep -qi "schema\|database\|migration\|graphql\|resolver\|prisma"; then
        return 0
      fi
      ;;

    frontend)
      # Frontend if: ui, component, page, react, vite
      if echo "$priority_content" | grep -qi "ui\|component\|page\|react\|vite\|frontend"; then
        return 0
      fi
      ;;

    infrastructure)
      # Infrastructure if: package, dependency, config, documentation, docs
      if echo "$priority_content" | grep -qi "package\|dependency\|config\|documentation\|docs"; then
        return 0
      fi
      ;;

    *)
      echo "ERROR: Unknown agent name: $agent_name"
      return 1
      ;;
  esac

  # Agent not needed based on priority content
  return 1
}

#
# Spawn agents in parallel based on priority analysis
# Args:
#   $1 - Session ID
#   $2 - Target repo
#   $3 - Priority file
#   $4 - Agents directory path
#   $5 - Log directory path
#
# Returns:
#   0 if all agents completed successfully
#   1 if any agent failed
#
spawn_parallel_agents() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"
  local agents_dir="$4"
  local log_dir="$5"

  local pids=()
  local agent_names=()

  # Backend + Infrastructure can run in parallel
  if should_spawn_agent "backend" "$priority_file"; then
    echo "Backend specialist needed"
    local backend_pid=$(spawn_agent \
      "$agents_dir/backend-specialist.sh" \
      "$session_id" \
      "$target_repo" \
      "$priority_file" \
      "$log_dir/backend-parallel.log")
    pids+=("$backend_pid")
    agent_names+=("backend")
  fi

  if should_spawn_agent "infrastructure" "$priority_file"; then
    echo "Infrastructure specialist needed"
    local infra_pid=$(spawn_agent \
      "$agents_dir/infrastructure-specialist.sh" \
      "$session_id" \
      "$target_repo" \
      "$priority_file" \
      "$log_dir/infrastructure-parallel.log")
    pids+=("$infra_pid")
    agent_names+=("infrastructure")
  fi

  # Wait for parallel agents
  if [[ ${#pids[@]} -gt 0 ]]; then
    echo "Waiting for parallel agents: ${agent_names[*]}"
    if ! wait_for_agents "${pids[@]}"; then
      echo "ERROR: Parallel agents failed"
      return 1
    fi
  else
    echo "No parallel agents to spawn"
  fi

  return 0
}

# Export functions for use in other scripts
export -f spawn_agent
export -f wait_for_agents
export -f should_spawn_agent
export -f spawn_parallel_agents
