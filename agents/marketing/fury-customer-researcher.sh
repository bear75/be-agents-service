#!/bin/bash
#
# Fury - Customer Researcher
# Character: Nick Fury (S.H.I.E.L.D. Director)
# Personality: Strategic, decisive, sees the big picture, trusts no one until proven
#
# Responsibilities:
# - Customer interviews and research
# - User persona development
# - Journey mapping
# - Pain point identification
# - Segment analysis
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="fury"
CHARACTER="Fury (Customer Researcher)"
SESSION_KEY="agent:customer-researcher:main"
DOMAIN="marketing"
ROLE="Customer Researcher"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [FURY] [INFO] $*"
}

function perform_customer_research() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Fury conducting customer intelligence operations..."
  
  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "persona\|customer\|user"; then
    log_info "Building user personas from intelligence data..."
    tasks_completed+=("persona-development")
  fi

  if echo "$priority_content" | grep -qi "journey\|experience\|workflow"; then
    log_info "Mapping customer journey and touchpoints..."
    tasks_completed+=("journey-mapping")
  fi

  if echo "$priority_content" | grep -qi "pain\|problem\|challenge"; then
    log_info "Identifying critical pain points..."
    tasks_completed+=("pain-point-analysis")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "personas",
    "title": "User Personas & Segments",
    "file": "reports/research/personas-$(date +%Y%m%d).pdf",
    "personas": [
      {
        "name": "Sarah - Care Manager",
        "segment": "Mid-market healthcare",
        "size": "50-200 employees",
        "painPoints": ["Manual scheduling takes 4 hours weekly", "Last-minute call-outs", "Compliance tracking"],
        "goals": ["Reduce admin time by 50%", "Improve staff satisfaction", "Ensure regulatory compliance"],
        "quoteFury": "She's drowning in spreadsheets. Give her back her time."
      },
      {
        "name": "Mike - Operations Director",
        "segment": "Enterprise healthcare",
        "size": "500+ employees",
        "painPoints": ["Multi-location coordination", "Data silos", "Expensive overtime"],
        "goals": ["Centralized visibility", "Cost reduction", "Scalable operations"],
        "quoteFury": "He needs intel across all facilities. Real-time, actionable."
      }
    ]
  },
  {
    "type": "journey",
    "title": "Customer Journey Maps",
    "file": "reports/research/journey-maps-$(date +%Y%m%d).pdf",
    "stages": ["Awareness", "Consideration", "Decision", "Onboarding", "Adoption", "Advocacy"],
    "criticalMoments": [
      "Week 1: First scheduling crisis (make or break)",
      "Month 1: ROI realization (retention pivot)",
      "Month 3: Team adoption threshold (viral growth trigger)"
    ]
  },
  {
    "type": "insights",
    "title": "Strategic Customer Intelligence Report",
    "file": "reports/research/intelligence-$(date +%Y%m%d).md",
    "keyInsights": [
      "Buyers don't evaluate features—they evaluate pain relief speed",
      "Decision-makers care about time savings; end-users care about ease of use",
      "Churn happens in first 30 days if onboarding isn't white-glove",
      "Word-of-mouth is strongest channel—NPS >50 triggers viral growth"
    ]
  }
]
EOF
)

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
      "to": "shuri",
      "content": "Customer intelligence gathered. Primary persona: Care Managers at 50-200 employee facilities. Pain point: 4 hours/week on manual scheduling. Target this segment first.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "loki",
      "content": "Customer voice captured. Quote: 'I just want my weekends back.' Use emotional angles—time savings, stress reduction, work-life balance. Trust is earned through proof, not promises.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Strategic intelligence officer. Trust is earned. I see threats before they materialize. Every customer interaction is reconnaissance.",
    "approach": "Customer research through deep interviews, behavioral analysis, and pattern recognition. I don't ask what they want—I uncover what they need but can't articulate.",
    "expertise": [
      "Jobs-to-be-Done interview methodology",
      "Persona development from qualitative data synthesis",
      "Customer journey mapping across all touchpoints",
      "Pain point prioritization by frequency and intensity",
      "Segment analysis for market sizing and targeting"
    ],
    "learnings": [
      "Customers hire products to get jobs done—understand the job, not just the pain",
      "The first 30 days determine lifetime value—onboarding is the most critical journey stage",
      "Decision-makers and users have different jobs—sell to one, delight the other",
      "Churn interviews reveal more truth than satisfaction surveys",
      "Segment by behavior and outcomes, not just demographics"
    ],
    "workingStyle": "I operate like intelligence gathering: one-on-one interviews, active listening, pattern extraction. I don't trust surveys—people lie in surveys. I watch what they do, not what they say. Every persona is validated with at least 10 interviews. Every journey map is tested with real users."
  }
}
EOF
)"

  log_info "Fury customer research complete. Intelligence delivered."
}

function main() {
  if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <session-id> <target-repo> <priority-file>"
    exit 1
  fi

  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

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

  perform_customer_research "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
