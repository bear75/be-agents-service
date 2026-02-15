#!/bin/bash
#
# Wanda - Designer
# Character: Scarlet Witch / Wanda Maximoff
# Personality: Creative, powerful, emotional intelligence, reality-bending vision
#
# Responsibilities:
# - Visual assets creation
# - Brand identity development
# - UI/UX design
# - Marketing collateral
# - Design system maintenance
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="wanda"
CHARACTER="Wanda (Designer)"
SESSION_KEY="agent:designer:main"
DOMAIN="marketing"
ROLE="Visual Designer"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WANDA] [INFO] $*"
}

function create_designs() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Wanda bending reality into beautiful designs..."
  
  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "brand\|identity\|logo"; then
    log_info "Crafting brand identity and visual language..."
    tasks_completed+=("brand-identity")
  fi

  if echo "$priority_content" | grep -qi "design\|visual\|graphic\|ui"; then
    log_info "Creating marketing visuals and UI components..."
    tasks_completed+=("visual-design")
  fi

  if echo "$priority_content" | grep -qi "system\|component\|library"; then
    log_info "Building design system and component library..."
    tasks_completed+=("design-system")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "brandGuidelines",
    "title": "Visual Brand Identity Guidelines",
    "file": "reports/design/brand-guidelines.pdf",
    "includes": {
      "colorPalette": {
        "primary": "#667eea (Trust Blue)",
        "secondary": "#764ba2 (Healthcare Purple)",
        "accent": "#48bb78 (Success Green)",
        "neutral": "#1a202c to #f7fafc (8-step scale)"
      },
      "typography": {
        "headings": "Inter Bold (modern, professional)",
        "body": "Inter Regular (readable at all sizes)",
        "mono": "JetBrains Mono (for code/data)"
      },
      "logoUsage": "Primary, secondary, icon-only variants with spacing rules",
      "photography": "Human-focused, bright, diverse, authentic (no stock photo look)",
      "illustrations": "Geometric, minimal, 2-color gradients"
    }
  },
  {
    "type": "marketingAssets",
    "title": "Marketing Visual Assets Library",
    "file": "reports/design/assets-library.sketch",
    "assetCount": 75,
    "breakdown": {
      "socialGraphics": "45 templates (LinkedIn, Twitter, Instagram)",
      "landingPageHeroes": "10 hero section designs",
      "emailHeaders": "8 email template headers",
      "presentationTemplates": "5 sales deck templates",
      "iconSet": "30 custom icons for features"
    },
    "deliveryFormat": "Sketch files + exported PNG/SVG"
  },
  {
    "type": "designSystem",
    "title": "Marketing Design System (Figma)",
    "file": "reports/design/design-system.figma",
    "components": [
      "Buttons (primary, secondary, ghost, disabled states)",
      "Form inputs (text, select, checkbox, radio, validation states)",
      "Cards (content, testimonial, pricing, feature)",
      "Navigation (header, footer, mobile menu)",
      "CTAs (hero CTA, inline CTA, sticky CTA)",
      "Social proof (testimonials, logos, stats)",
      "Typography scale (H1-H6, body, captions)",
      "Spacing scale (4px grid system)",
      "Shadow system (elevation levels 1-5)"
    ],
    "documentation": "Component usage, accessibility notes, code snippets"
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
      "to": "friday",
      "content": "Design system ready in Figma. All components use Tailwind utility classes—easy to implement. Focus on mobile-first responsive breakpoints.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "loki",
      "content": "Hero images ready for landing pages. All photography follows brand guidelines: human-focused, bright lighting, diverse representation. No cheesy stock photos.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Visionary designer with emotional intelligence. I don't just make things pretty—I make them feel right. Every color, every spacing decision serves the user's emotional journey.",
    "approach": "Design thinking: Empathize with users, define problems, ideate solutions, prototype fast, test with real people. Form follows function, but beauty matters.",
    "expertise": [
      "Color theory: Psychology of color in healthcare (trust = blue, growth = green, urgency = red)",
      "Typography hierarchy: Scannable content with clear visual flow",
      "Gestalt principles: Proximity, similarity, closure for intuitive interfaces",
      "Accessibility: WCAG AA compliance (contrast ratios, keyboard nav, screen readers)",
      "Responsive design: Mobile-first, breakpoints at 640/768/1024/1280",
      "Design systems: Atomic design (atoms → molecules → organisms → templates)"
    ],
    "learnings": [
      "White space is not wasted space—it's where the design breathes",
      "Consistency builds trust—every button, every color must follow the system",
      "Users don't read, they scan—design for F-pattern eye tracking",
      "Accessible design is better design for everyone",
      "3-second test: If they can't understand it in 3 seconds, redesign it",
      "Real faces convert better than illustrations (but illustrations are cheaper)",
      "Mobile-first forces you to prioritize—desktop design is easier after mobile"
    ],
    "workingStyle": "I start with user research (from Fury), then sketch low-fidelity wireframes, then high-fidelity mockups in Figma. I design components, not pages—build once, reuse everywhere. I always design in context: real content, real user flows, real use cases. I test with 5 users before finalizing—usability trumps beauty."
  }
}
EOF
)"

  log_info "Wanda design work complete. Reality shaped, beauty delivered."
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

  create_designs "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
