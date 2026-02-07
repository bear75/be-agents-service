#!/bin/bash
#
# Jarvis - Marketing Squad Lead Orchestrator
# Character: J.A.R.V.I.S. (Just A Rather Very Intelligent System)
# Personality: Sophisticated, analytical, efficient coordinator
#
# Responsibilities:
# - Read marketing priority files
# - Create marketing PRD
# - Assign tasks to specialist marketing agents
# - Coordinate parallel execution (research agents run together)
# - Aggregate deliverables
# - Create PR for marketing changes
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source libraries
source "$SERVICE_ROOT/lib/state-manager.sh"
source "$SERVICE_ROOT/lib/parallel-executor.sh"

# Agent configuration
AGENT_NAME="jarvis"
CHARACTER="J.A.R.V.I.S. (Marketing Squad Lead)"
SESSION_KEY="agent:main:main"
DOMAIN="marketing"

# Directories
AGENTS_DIR="$SERVICE_ROOT/agents/marketing"
PROMPTS_DIR="$SERVICE_ROOT/.claude/prompts/marketing"
LOGS_DIR="$SERVICE_ROOT/logs/orchestrator-sessions"

# ============================================================================
# Usage
# ============================================================================

function usage() {
  cat <<EOF
Jarvis - Marketing Squad Lead Orchestrator

Usage:
  $0 <target-repo> <priority-file> <prd-file> <branch-name>

Arguments:
  target-repo    - Path to target repository
  priority-file  - Path to priority file (marketing task)
  prd-file       - Path to PRD file (optional, will create if missing)
  branch-name    - Git branch to work on

Examples:
  # Marketing blog post
  $0 ~/HomeCare/beta-appcaire reports/marketing-priorities-2026-02-07.md \\
     tasks/marketing-prd.json feature/blog-post-scheduling

  # SEO campaign
  $0 ~/HomeCare/website reports/seo-campaign.md \\
     tasks/seo-prd.json feature/seo-optimization

Environment Variables:
  USE_MARKETING_SPECIALISTS - Enable specialist agents (default: true)
  MARKETING_PARALLEL        - Run research agents in parallel (default: true)

Session Key: $SESSION_KEY
Character: $CHARACTER
EOF
  exit 1
}

# ============================================================================
# Logging
# ============================================================================

LOG_FILE=""

function setup_logging() {
  local session_id="${1:-}"
  local log_dir="$LOGS_DIR/$session_id"
  mkdir -p "$log_dir"
  LOG_FILE="$log_dir/${AGENT_NAME}.log"
  exec > >(tee -a "$LOG_FILE") 2>&1
}

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [JARVIS] [INFO] $*"
}

function log_error() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [JARVIS] [ERROR] $*" >&2
}

function log_agent() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [JARVIS] [AGENT] $*"
}

# ============================================================================
# Agent Intelligence
# ============================================================================

function analyze_marketing_priority() {
  local priority_file="$1"
  local priority_content
  priority_content=$(cat "$priority_file")

  # Determine which marketing agents are needed
  local needs_seo=false
  local needs_content=false
  local needs_design=false
  local needs_social=false
  local needs_email=false
  local needs_product_analysis=false
  local needs_customer_research=false
  local needs_developer=false
  local needs_notion=false

  # Analyze keywords to determine agents
  if echo "$priority_content" | grep -qi "seo\|keyword\|search\|ranking\|organic"; then
    needs_seo=true
  fi

  if echo "$priority_content" | grep -qi "blog\|content\|article\|copy\|writing"; then
    needs_content=true
  fi

  if echo "$priority_content" | grep -qi "design\|visual\|graphic\|image\|brand"; then
    needs_design=true
  fi

  if echo "$priority_content" | grep -qi "social\|twitter\|linkedin\|instagram\|facebook"; then
    needs_social=true
  fi

  if echo "$priority_content" | grep -qi "email\|newsletter\|campaign"; then
    needs_email=true
  fi

  if echo "$priority_content" | grep -qi "product\|market\|competitor\|pricing\|positioning"; then
    needs_product_analysis=true
  fi

  if echo "$priority_content" | grep -qi "customer\|user\|persona\|journey\|pain point"; then
    needs_customer_research=true
  fi

  if echo "$priority_content" | grep -qi "landing page\|website\|technical\|implement"; then
    needs_developer=true
  fi

  if echo "$priority_content" | grep -qi "notion\|documentation\|knowledge\|process"; then
    needs_notion=true
  fi

  # Export for use in orchestration
  cat <<EOF
needs_seo=$needs_seo
needs_content=$needs_content
needs_design=$needs_design
needs_social=$needs_social
needs_email=$needs_email
needs_product_analysis=$needs_product_analysis
needs_customer_research=$needs_customer_research
needs_developer=$needs_developer
needs_notion=$needs_notion
EOF
}

# ============================================================================
# Orchestration
# ============================================================================

function orchestrate_marketing_workflow() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"
  local branch_name="$4"

  log_info "========================================="
  log_info "Jarvis Marketing Orchestrator"
  log_info "========================================="
  log_info "Session: $session_id"
  log_info "Target repo: $target_repo"
  log_info "Priority: $priority_file"
  log_info "Branch: $branch_name"
  log_info "Character: $CHARACTER"
  log_info "========================================="

  # Analyze priority to determine agents needed
  log_info "Analyzing marketing priority..."
  local analysis
  analysis=$(analyze_marketing_priority "$priority_file")
  eval "$analysis"

  log_info "Required agents:"
  [[ "$needs_seo" == true ]] && log_agent "✓ Vision (SEO Analyst)"
  [[ "$needs_content" == true ]] && log_agent "✓ Loki (Content Writer)"
  [[ "$needs_design" == true ]] && log_agent "✓ Wanda (Designer)"
  [[ "$needs_social" == true ]] && log_agent "✓ Quill (Social Media)"
  [[ "$needs_email" == true ]] && log_agent "✓ Pepper (Email Marketing)"
  [[ "$needs_product_analysis" == true ]] && log_agent "✓ Shuri (Product Analyst)"
  [[ "$needs_customer_research" == true ]] && log_agent "✓ Fury (Customer Researcher)"
  [[ "$needs_developer" == true ]] && log_agent "✓ Friday (Developer)"
  [[ "$needs_notion" == true ]] && log_agent "✓ Wong (Notion Agent)"

  # Phase 1: Research (Parallel)
  log_info ""
  log_info "Phase 1: Research & Analysis (Parallel Execution)"
  log_info "========================================="

  local phase1_pids=()

  if [[ "$needs_product_analysis" == true ]]; then
    log_agent "Spawning Shuri (Product Analyst)..."
    "$AGENTS_DIR/shuri-product-analyst.sh" "$session_id" "$target_repo" "$priority_file" &
    phase1_pids+=($!)
  fi

  if [[ "$needs_customer_research" == true ]]; then
    log_agent "Spawning Fury (Customer Researcher)..."
    "$AGENTS_DIR/fury-customer-researcher.sh" "$session_id" "$target_repo" "$priority_file" &
    phase1_pids+=($!)
  fi

  if [[ "$needs_seo" == true ]]; then
    log_agent "Spawning Vision (SEO Analyst)..."
    "$AGENTS_DIR/vision-seo-analyst.sh" "$session_id" "$target_repo" "$priority_file" &
    phase1_pids+=($!)
  fi

  # Wait for research agents
  if [[ ${#phase1_pids[@]} -gt 0 ]]; then
    log_info "Waiting for research agents to complete..."
    for pid in "${phase1_pids[@]}"; do
      wait "$pid" && log_agent "✓ Research agent $pid completed" || log_error "Research agent $pid failed"
    done
  else
    log_info "No research agents needed, skipping Phase 1"
  fi

  # Phase 2: Content Creation (Sequential, waits for research)
  log_info ""
  log_info "Phase 2: Content Creation"
  log_info "========================================="

  if [[ "$needs_content" == true ]]; then
    log_agent "Spawning Loki (Content Writer)..."
    "$AGENTS_DIR/loki-content-writer.sh" "$session_id" "$target_repo" "$priority_file"
  fi

  if [[ "$needs_email" == true ]]; then
    log_agent "Spawning Pepper (Email Marketing)..."
    "$AGENTS_DIR/pepper-email-marketing.sh" "$session_id" "$target_repo" "$priority_file"
  fi

  # Phase 3: Design & Technical (Parallel)
  log_info ""
  log_info "Phase 3: Design & Technical (Parallel Execution)"
  log_info "========================================="

  local phase3_pids=()

  if [[ "$needs_design" == true ]]; then
    log_agent "Spawning Wanda (Designer)..."
    "$AGENTS_DIR/wanda-designer.sh" "$session_id" "$target_repo" "$priority_file" &
    phase3_pids+=($!)
  fi

  if [[ "$needs_developer" == true ]]; then
    log_agent "Spawning Friday (Developer)..."
    "$AGENTS_DIR/friday-developer.sh" "$session_id" "$target_repo" "$priority_file" &
    phase3_pids+=($!)
  fi

  # Wait for design/tech agents
  if [[ ${#phase3_pids[@]} -gt 0 ]]; then
    log_info "Waiting for design and technical agents..."
    for pid in "${phase3_pids[@]}"; do
      wait "$pid" && log_agent "✓ Design/tech agent $pid completed" || log_error "Design/tech agent $pid failed"
    done
  fi

  # Phase 4: Distribution (Sequential)
  log_info ""
  log_info "Phase 4: Distribution & Documentation"
  log_info "========================================="

  if [[ "$needs_social" == true ]]; then
    log_agent "Spawning Quill (Social Media Manager)..."
    "$AGENTS_DIR/quill-social-media.sh" "$session_id" "$target_repo" "$priority_file"
  fi

  if [[ "$needs_notion" == true ]]; then
    log_agent "Spawning Wong (Notion Agent)..."
    "$AGENTS_DIR/wong-notion-agent.sh" "$session_id" "$target_repo" "$priority_file"
  fi

  # Complete
  log_info ""
  log_info "========================================="
  log_info "All marketing agents completed"
  log_info "========================================="

  # Write final orchestrator state
  write_state "$session_id" "$AGENT_NAME" "$(cat <<EOF
{
  "agentName": "$AGENT_NAME",
  "character": "$CHARACTER",
  "sessionKey": "$SESSION_KEY",
  "domain": "$DOMAIN",
  "status": "completed",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "targetRepo": "$target_repo",
  "priorityFile": "$priority_file",
  "branchName": "$branch_name",
  "specialists": {
    "shuri": $(if [[ "$needs_product_analysis" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "fury": $(if [[ "$needs_customer_research" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "vision": $(if [[ "$needs_seo" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "loki": $(if [[ "$needs_content" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "wanda": $(if [[ "$needs_design" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "friday": $(if [[ "$needs_developer" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "quill": $(if [[ "$needs_social" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "pepper": $(if [[ "$needs_email" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi),
    "wong": $(if [[ "$needs_notion" == true ]]; then echo '"completed"'; else echo '"skipped"'; fi)
  }
}
EOF
)"

  log_info "Marketing workflow complete!"
  log_info "Session state: .compound-state/$session_id/"
  log_info "Logs: $LOG_FILE"
}

# ============================================================================
# Main
# ============================================================================

function main() {
  # Parse arguments
  if [[ $# -lt 3 ]]; then
    usage
  fi

  local target_repo="$1"
  local priority_file="$2"
  local prd_file="${3:-}"
  local branch_name="${4:-feature/marketing-$(date +%Y%m%d)}"

  # Validate
  if [[ ! -d "$target_repo" ]]; then
    log_error "Target repo does not exist: $target_repo"
    exit 1
  fi

  if [[ ! -f "$priority_file" ]]; then
    log_error "Priority file does not exist: $priority_file"
    exit 1
  fi

  # Create session
  local session_id="session-marketing-$(date +%s)"
  init_session "$session_id"

  # Setup logging
  setup_logging "$session_id"

  # Orchestrate
  orchestrate_marketing_workflow "$session_id" "$target_repo" "$priority_file" "$branch_name"

  log_info "Jarvis signing off. Marketing mission accomplished."
}

# Run if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
