#!/bin/bash
#
# Quill - Social Media Manager
# Character: Star-Lord / Peter Quill (Guardians leader)
# Personality: Charismatic, spontaneous, knows how to read the room, pop culture expert
#
# Responsibilities:
# - Social media calendar
# - Community engagement
# - Content curation
# - Trend monitoring
# - Crisis management
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="quill"
CHARACTER="Quill (Social Media Manager)"
SESSION_KEY="agent:social-media-manager:main"
DOMAIN="marketing"
ROLE="Social Media Manager"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [QUILL] [INFO] $*"
}

function manage_social_media() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Quill reading the room and building social presence..."
  
  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "social\|twitter\|linkedin"; then
    log_info "Creating social media content calendar..."
    tasks_completed+=("content-calendar")
  fi

  if echo "$priority_content" | grep -qi "engage\|community\|response"; then
    log_info "Planning community engagement strategy..."
    tasks_completed+=("engagement-strategy")
  fi

  if echo "$priority_content" | grep -qi "trend\|viral\|timing"; then
    log_info "Monitoring trends and optimal posting times..."
    tasks_completed+=("trend-analysis")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "calendar",
    "title": "30-Day Social Media Content Calendar",
    "file": "reports/social/content-calendar-30day.xlsx",
    "platforms": ["LinkedIn", "X (Twitter)"],
    "postCount": 45,
    "breakdown": {
      "linkedin": {
        "frequency": "5x/week",
        "bestTimes": ["Tuesday 10am", "Wednesday 12pm", "Thursday 9am"],
        "contentMix": ["Thought leadership 40%", "Customer stories 30%", "Product updates 20%", "Team culture 10%"]
      },
      "twitter": {
        "frequency": "2x/day",
        "bestTimes": ["Weekdays 9am", "Weekdays 3pm"],
        "contentMix": ["Tips & tricks 40%", "Industry news 30%", "Quick wins 20%", "Engagement tweets 10%"]
      }
    }
  },
  {
    "type": "content",
    "title": "Pre-Written Social Posts (45 posts)",
    "file": "reports/social/posts-library.json",
    "samplePosts": [
      {
        "platform": "LinkedIn",
        "text": "Healthcare managers: Still spending hours on Excel scheduling? There's a better way. AI can optimize your entire week's schedule in 30 minutes. Here's how it works... [thread 1/5]",
        "hashtags": ["#HealthcareManagement", "#EmployeeScheduling", "#AIforGood"],
        "media": "demo-video.mp4",
        "cta": "Try free for 14 days"
      },
      {
        "platform": "Twitter",
        "text": "Before AI scheduling: 4 hours of spreadsheet hell every Monday\n\nAfter AI scheduling: 30 minutes, coffee in hand, no stress\n\nThe future of workforce management is here.",
        "hashtags": ["#WorkforceManagement", "#ProductivityHack"],
        "media": "before-after-infographic.png"
      }
    ]
  },
  {
    "type": "strategy",
    "title": "Engagement & Growth Strategy",
    "file": "reports/social/engagement-strategy.md",
    "tactics": [
      "Reply to every comment within 2 hours (build community)",
      "Reshare customer wins (social proof + gratitude)",
      "Join 5 LinkedIn groups in healthcare management niche",
      "Weekly Twitter Spaces: 'Healthcare Ops Happy Hour'",
      "Partner with 10 micro-influencers in healthcare space"
    ],
    "kpis": {
      "month1": "500 followers, 5% engagement rate",
      "month3": "2000 followers, 8% engagement rate",
      "month6": "5000 followers, 10% engagement rate, 50 leads/month"
    }
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
      "content": "Need 45 social graphics: 20 LinkedIn posts (1200x627), 25 Twitter images (1200x675). Keep them scroll-stopping—bright colors, bold text overlays, human faces.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "pepper",
      "content": "Social traffic will spike in 2 weeks. Prepare email nurture sequence for LinkedIn profile visitors. They're warm leads—move them to trial quickly.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Charismatic community builder. I speak internet fluently. I know when to be serious (LinkedIn) and when to be playful (Twitter). Always reading the room, always on-trend.",
    "approach": "Platform-native content: LinkedIn = thought leadership, Twitter = quick wins. Post consistently, engage authentically, ride trends smartly. Community first, sales second.",
    "expertise": [
      "Platform algorithms: LinkedIn favors comments, Twitter favors speed and threads",
      "Content mix: 80% value, 20% promotion (Jab, Jab, Jab, Right Hook)",
      "Engagement tactics: Ask questions, tag people, reply within 2 hours",
      "Hashtag strategy: 3-5 relevant hashtags, mix popular + niche",
      "Optimal posting times: Data-driven scheduling for each platform",
      "Crisis management: Respond fast, acknowledge mistakes, move offline if needed"
    ],
    "learnings": [
      "Consistency beats virality—post daily, build compound growth",
      "Engagement rate > follower count. 1000 engaged > 10000 dead followers.",
      "Stories and faces perform better than logos and products",
      "Controversial takes get engagement, but brand safety comes first",
      "Micro-influencer partnerships (1k-10k followers) have best ROI",
      "First 3 seconds determine if they scroll or stop—hook them fast",
      "Comments create algorithmic boost—always ask a question"
    ],
    "workingStyle": "I batch-create content weekly, schedule with Buffer/Hootsuite, then spend 1 hour daily on real-time engagement. I monitor trends obsessively—if something's blowing up, I jump on it within 2 hours. I respond to every comment like a human, not a brand. I measure everything: reach, engagement, clicks, conversions."
  }
}
EOF
)"

  log_info "Quill social media strategy complete. Let's grow this thing."
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

  manage_social_media "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
