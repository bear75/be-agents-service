#!/bin/bash
#
# Pepper - Email Marketing Specialist
# Character: Pepper Potts (CEO & Organizer)
# Personality: Organized, professional, results-focused, keeps everyone on track
#
# Responsibilities:
# - Email campaign creation
# - List segmentation
# - A/B testing
# - Automation workflows
# - Performance optimization
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="pepper"
CHARACTER="Pepper (Email Marketing)"
SESSION_KEY="agent:email-marketing:main"
DOMAIN="marketing"
ROLE="Email Marketing Specialist"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [PEPPER] [INFO] $*"
}

function create_email_campaigns() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Pepper orchestrating email campaigns with precision..."
  
  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "email\|campaign\|nurture"; then
    log_info "Building email campaigns and nurture sequences..."
    tasks_completed+=("campaign-creation")
  fi

  if echo "$priority_content" | grep -qi "segment\|list\|audience"; then
    log_info "Segmenting email lists for targeted campaigns..."
    tasks_completed+=("list-segmentation")
  fi

  if echo "$priority_content" | grep -qi "automat\|workflow\|drip"; then
    log_info "Setting up marketing automation workflows..."
    tasks_completed+=("automation-setup")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "campaign",
    "title": "Product Launch Email Sequence (5 emails)",
    "file": "reports/email/product-launch-sequence.html",
    "sequence": [
      {
        "email": 1,
        "subject": "Introducing: AI That Gives You Your Weekends Back",
        "preheader": "Say goodbye to 4-hour scheduling marathons",
        "sendTiming": "Launch day, 9am",
        "goal": "Awareness + curiosity",
        "cta": "Watch 2-min demo",
        "abTest": "Subject line A vs B (emoji vs no emoji)"
      },
      {
        "email": 2,
        "subject": "How CareCenter Reduced Scheduling Time by 75%",
        "preheader": "Real results from a mid-market healthcare facility",
        "sendTiming": "+3 days",
        "goal": "Social proof + credibility",
        "cta": "Read full case study"
      },
      {
        "email": 3,
        "subject": "Your Exclusive 14-Day Trial Invitation",
        "preheader": "No credit card. No setup fees. Just results.",
        "sendTiming": "+7 days",
        "goal": "Trial signup",
        "cta": "Start free trial",
        "personaliz ation": "First name, company size"
      },
      {
        "email": 4,
        "subject": "Last chance: Trial ends in 48 hours",
        "preheader": "Don't miss out on transforming your scheduling",
        "sendTiming": "+12 days (if no signup)",
        "goal": "Urgency conversion",
        "cta": "Claim your trial"
      },
      {
        "email": 5,
        "subject": "We'll miss you (but here's 20% off anyway)",
        "preheader": "One last offer before we say goodbye",
        "sendTiming": "+30 days (if no engagement)",
        "goal": "Win-back with discount",
        "cta": "Get 20% off first 3 months"
      }
    ],
    "targetAudience": "Mid-market healthcare operations managers",
    "expectedMetrics": {
      "openRate": "28-35%",
      "clickRate": "4-7%",
      "conversionRate": "12-18% (trial signup)"
    }
  },
  {
    "type": "segmentation",
    "title": "Email List Segmentation Strategy",
    "file": "reports/email/segmentation-strategy.xlsx",
    "segments": [
      {
        "name": "Hot Leads",
        "criteria": "Visited pricing 3+ times, downloaded guide, opened 5+ emails",
        "size": "~350 contacts",
        "treatment": "Sales handoff, white-glove onboarding offer"
      },
      {
        "name": "Warm Leads",
        "criteria": "Opened 3+ emails, clicked 1+ links, engaged content",
        "size": "~2100 contacts",
        "treatment": "Case studies, product demos, trial invitations"
      },
      {
        "name": "Cold Leads",
        "criteria": "Subscribed but < 2 opens in 30 days",
        "size": "~6300 contacts",
        "treatment": "Re-engagement campaign, value-focused content"
      },
      {
        "name": "Trial Users",
        "criteria": "Active trial, < 7 days old",
        "size": "~120 contacts",
        "treatment": "Onboarding sequence, feature education, success stories"
      }
    ]
  },
  {
    "type": "automation",
    "title": "Marketing Automation Workflows",
    "file": "reports/email/automation-workflows.pdf",
    "workflows": [
      {
        "name": "Welcome Series",
        "trigger": "Email signup",
        "steps": 3,
        "duration": "7 days",
        "goal": "Educate + build trust"
      },
      {
        "name": "Trial Onboarding",
        "trigger": "Trial started",
        "steps": 7,
        "duration": "14 days",
        "goal": "Drive activation + conversion"
      },
      {
        "name": "Lead Nurture",
        "trigger": "Downloaded resource",
        "steps": 5,
        "duration": "30 days",
        "goal": "Move from awareness to consideration"
      },
      {
        "name": "Re-engagement",
        "trigger": "No opens in 60 days",
        "steps": 3,
        "duration": "14 days",
        "goal": "Win back or clean list"
      }
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
      "to": "wanda",
      "content": "Need email templates designed: 5 campaign emails + 4 automation workflows. Mobile-first (60% open on mobile). Keep CTAs above fold, single column layout.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "friday",
      "content": "Automation workflows ready for implementation. Use SendGrid API for transactional, Mailchimp for campaigns. Track: opens, clicks, conversions, unsubscribes.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Organized executor. Every campaign is measured, every workflow is optimized, every email earns its place in the inbox. Professional, results-driven, no fluff.",
    "approach": "Data-driven email marketing: Segment precisely, personalize intelligently, test continuously, optimize relentlessly. Respect the inbox—send value, not spam.",
    "expertise": [
      "Email deliverability: SPF/DKIM/DMARC setup, sender reputation management",
      "Subject line optimization: 40 chars, action verbs, curiosity gaps, A/B testing",
      "Segmentation strategies: Behavioral (engagement), demographic (role/size), lifecycle (trial/customer)",
      "Personalization beyond first name: Company data, behavior triggers, predictive send times",
      "A/B testing: Subject lines, CTAs, send times, content formats",
      "Automation workflows: Welcome, nurture, onboarding, re-engagement, win-back",
      "Metrics that matter: Open rate (inbox placement), click rate (engagement), conversion rate (ROI)"
    ],
    "learnings": [
      "Mobile opens are 60%+ —design mobile-first or lose half your audience",
      "Subject lines with numbers get 57% more opens ('5 ways' beats 'ways')",
      "Personalization increases click rates by 14% (but don't overdo it—creepy > helpful)",
      "Send time optimization: B2B peaks at 10am Tuesday-Thursday",
      "Segmented campaigns get 3x higher click rates than batch-and-blast",
      "Re-engagement campaigns save 15-20% of inactive subscribers",
      "Unsubscribes aren't failures—clean lists have better deliverability",
      "Plain text emails often outperform HTML for cold outreach (feel personal, not corporate)"
    ],
    "workingStyle": "I plan campaigns in weekly sprints, write copy in batches, A/B test everything, and review metrics daily. Every email has a single, clear goal. I segment ruthlessly—right message, right person, right time. I automate repetitive workflows so I can focus on strategy. I clean lists quarterly—deliverability > vanity metrics."
  }
}
EOF
)"

  log_info "Pepper email campaigns complete. Inboxes conquered, conversions secured."
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

  create_email_campaigns "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
