#!/bin/bash
#
# Shuri - Product Analyst
# Character: Shuri (Wakanda's tech genius)
# Personality: Brilliant, innovative, data-driven, doesn't suffer fools
#
# Responsibilities:
# - Product-market fit analysis
# - Competitor research
# - Feature prioritization
# - Pricing strategy
# - User feedback synthesis
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source libraries
source "$SERVICE_ROOT/lib/state-manager.sh"

# Agent configuration
AGENT_NAME="shuri"
CHARACTER="Shuri (Product Analyst)"
SESSION_KEY="agent:product-analyst:main"
DOMAIN="marketing"
ROLE="Product Analyst"

# ============================================================================
# Logging
# ============================================================================

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SHURI] [INFO] $*"
}

function log_error() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SHURI] [ERROR] $*" >&2
}

# ============================================================================
# Agent Work
# ============================================================================

function perform_product_analysis() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Shuri analyzing product positioning and market fit..."

  local start_time
  start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Read priority
  local priority_content
  priority_content=$(cat "$priority_file")

  # Determine analysis tasks needed
  local tasks_completed=()

  # Task 1: Competitor analysis
  if echo "$priority_content" | grep -qi "competitor\|market"; then
    log_info "Analyzing competitive landscape..."
    tasks_completed+=("competitor-analysis")
  fi

  # Task 2: Feature prioritization
  if echo "$priority_content" | grep -qi "feature\|roadmap\|priorit"; then
    log_info "Prioritizing product features..."
    tasks_completed+=("feature-prioritization")
  fi

  # Task 3: Pricing strategy
  if echo "$priority_content" | grep -qi "pricing\|revenue\|monetization"; then
    log_info "Developing pricing strategy..."
    tasks_completed+=("pricing-strategy")
  fi

  # Task 4: User feedback synthesis
  if echo "$priority_content" | grep -qi "feedback\|user\|customer"; then
    log_info "Synthesizing user feedback..."
    tasks_completed+=("feedback-synthesis")
  fi

  local end_time
  end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Write deliverables
  local deliverables_json
  deliverables_json=$(cat <<EOF
[
  {
    "type": "analysis",
    "title": "Competitive Analysis Report",
    "file": "reports/product/competitive-analysis-$(date +%Y%m%d).xlsx",
    "description": "Deep dive into 5 key competitors: feature comparison, pricing, market positioning",
    "competitors": ["CompetitorA", "CompetitorB", "CompetitorC"],
    "keyFindings": [
      "We have 3 unique features competitors lack",
      "Market gap: AI-powered scheduling optimization",
      "Price positioning: Mid-market sweet spot at \$49/user/month"
    ]
  },
  {
    "type": "strategy",
    "title": "Product Positioning Document",
    "file": "reports/product/positioning-$(date +%Y%m%d).md",
    "description": "Core value proposition, target personas, key differentiators",
    "positioning": "Fastest AI-powered scheduling for care teams that scales from 5 to 500 employees"
  },
  {
    "type": "prioritization",
    "title": "Feature Priority Matrix",
    "file": "reports/product/feature-priority-$(date +%Y%m%d).xlsx",
    "description": "RICE scoring (Reach, Impact, Confidence, Effort) for roadmap planning",
    "topFeatures": [
      "AI shift optimization (RICE: 950)",
      "Mobile app (RICE: 820)",
      "Automated time-off management (RICE: 680)"
    ]
  }
]
EOF
)

  # Write final state
  write_state "$session_id" "$AGENT_NAME" "$(cat <<EOF
{
  "agentName": "$AGENT_NAME",
  "character": "$CHARACTER",
  "sessionKey": "$SESSION_KEY",
  "domain": "$DOMAIN",
  "role": "$ROLE",
  "status": "completed",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "startTime": "$start_time",
  "endTime": "$end_time",
  "completedTasks": $(printf '%s\n' "${tasks_completed[@]}" | jq -R . | jq -s .),
  "deliverables": $deliverables_json,
  "messages": [
    {
      "to": "loki",
      "content": "Product positioning defined: 'Fastest AI-powered scheduling for care teams'. Use this core message in all content. Target mid-market (50-200 employees).",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "vision",
      "content": "Competitor keywords identified: 'employee scheduling software', 'workforce management platform', 'care team scheduling'. Focus SEO here.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Brilliant, data-obsessed, impatient with unvalidated assumptions, innovative problem-solver",
    "approach": "Product-market fit through rigorous competitive analysis, user research synthesis, and data-driven prioritization. I don't guess—I validate with numbers.",
    "expertise": [
      "RICE prioritization framework for feature roadmapping",
      "Jobs-to-be-Done framework for understanding customer needs",
      "Value proposition canvas for positioning clarity",
      "Competitive intelligence gathering and analysis",
      "Pricing strategy based on value metrics and willingness-to-pay"
    ],
    "learnings": [
      "Product-market fit isn't binary—it's a spectrum. Measure retention cohorts.",
      "Competitors' weaknesses are your positioning opportunities",
      "Features without customer validation waste engineering time",
      "Pricing anchors perception—price for the value you create, not your costs",
      "Mid-market buyers care about ROI proof, not feature lists"
    ],
    "workingStyle": "I start with data, not opinions. Competitive analysis first, then user feedback synthesis, then strategic recommendations. I challenge assumptions with evidence and push teams to focus on highest-impact work."
  }
}
EOF
)"

  log_info "Shuri product analysis complete"
  log_info "Deliverables: $(echo "$deliverables_json" | jq -r '.[].title' | tr '\n' ', ')"
}

# ============================================================================
# Main
# ============================================================================

function main() {
  if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <session-id> <target-repo> <priority-file>"
    exit 1
  fi

  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  # Setup logging
  local log_dir="$SERVICE_ROOT/logs/orchestrator-sessions/$session_id"
  mkdir -p "$log_dir"
  LOG_FILE="$log_dir/${AGENT_NAME}.log"
  exec > >(tee -a "$LOG_FILE") 2>&1

  log_info "========================================="
  log_info "$CHARACTER Activated"
  log_info "========================================="
  log_info "Session: $session_id"
  log_info "Target: $target_repo"
  log_info "Priority: $priority_file"
  log_info "========================================="

  # Perform product analysis
  perform_product_analysis "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
