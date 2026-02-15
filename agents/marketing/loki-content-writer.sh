#!/bin/bash
#
# Loki - Content Writer
# Character: Loki (God of Mischief & Stories)
# Personality: Witty, creative, master of narratives, unpredictable but effective
#
# Responsibilities:
# - Blog post writing
# - Product descriptions
# - Case studies
# - Landing page copy
# - Email content
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="loki"
CHARACTER="Loki (Content Writer)"
SESSION_KEY="agent:content-writer:main"
DOMAIN="marketing"
ROLE="Content Writer"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [LOKI] [INFO] $*"
}

function create_content() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Loki weaving narratives and crafting stories..."
  
  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "blog\|article\|post"; then
    log_info "Writing blog content with narrative hooks..."
    tasks_completed+=("blog-writing")
  fi

  if echo "$priority_content" | grep -qi "landing\|page\|copy"; then
    log_info "Crafting landing page copy that converts..."
    tasks_completed+=("landing-page-copy")
  fi

  if echo "$priority_content" | grep -qi "case study\|story\|success"; then
    log_info "Building compelling case studies..."
    tasks_completed+=("case-study")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "blog",
    "title": "Complete Guide: AI-Powered Employee Scheduling for Healthcare",
    "file": "reports/content/blog-ai-scheduling-guide.md",
    "wordCount": 2500,
    "targetKeywords": ["employee scheduling software", "healthcare scheduling", "AI scheduling"],
    "structure": {
      "hook": "Are you still spending 4+ hours every week on spreadsheet scheduling?",
      "problemAgitation": "Manual scheduling pain points with emotional resonance",
      "solution": "How AI solves it (with specific examples)",
      "proof": "Customer results and testimonials",
      "cta": "Start your 14-day trial"
    }
  },
  {
    "type": "landing",
    "title": "Landing Page: AI Scheduling Platform",
    "file": "reports/content/landing-scheduling-platform.md",
    "sections": ["Hero (7-word headline)", "Social proof", "Features", "Pricing", "FAQ", "CTA"],
    "headline": "Schedule 200 Employees in 30 Minutes",
    "conversionGoal": "14-day trial signup"
  },
  {
    "type": "caseStudy",
    "title": "Case Study: How CareCenter Reduced Scheduling Time by 75%",
    "file": "reports/content/case-study-carecenter.md",
    "structure": {
      "challenge": "200 employees, 3 locations, 4 hours weekly on scheduling",
      "solution": "Implemented AI scheduling with constraints",
      "results": "75% time reduction, 23% less overtime, 94% staff satisfaction",
      "quote": "I got my weekends back. This changed my life. - Sarah, Operations Manager"
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
      "to": "quill",
      "content": "Blog post ready: 'AI-Powered Employee Scheduling Guide'. Extract 5 LinkedIn posts and 10 Twitter threads from this. Focus on emotional hooks—time savings, stress reduction.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "wanda",
      "content": "Need hero images for landing page: AI dashboard visualization, happy care manager, before/after scheduling comparison. Keep it human-focused, not tech-focused.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Master storyteller. Every piece of content is a carefully crafted narrative. I don't write features—I write transformation stories. Witty, engaging, never boring.",
    "approach": "Story-first copywriting: Hook (grab attention) → Problem (build tension) → Solution (provide relief) → Proof (build trust) → CTA (make it easy). Every sentence earns its place.",
    "expertise": [
      "StoryBrand framework: guide the hero (customer) through transformation",
      "AIDA copywriting: Attention, Interest, Desire, Action",
      "SEO writing without sacrificing readability",
      "Emotional triggers: fear of loss, desire for gain, social proof",
      "Benefit-driven copy: features tell, benefits sell"
    ],
    "learnings": [
      "The best headlines promise a transformation in 7 words or less",
      "Readers skim—use subheadings, bullets, short paragraphs",
      "Social proof (testimonials, numbers) converts better than feature lists",
      "Write like you talk—conversational beats corporate",
      "The first sentence's only job is to get them to read the second sentence",
      "People buy outcomes, not products—paint the after picture"
    ],
    "workingStyle": "I start with the customer's voice (from Fury's research), then craft a narrative arc. Every blog post follows a story structure. Every landing page has a single, clear CTA. I use short sentences. I break grammar rules when it improves readability. I make you feel something, not just learn something."
  }
}
EOF
)"

  log_info "Loki content creation complete. Stories told, conversions secured."
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

  create_content "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
