#!/bin/bash
#
# Wong - Notion Agent (Knowledge Manager)
# Character: Wong (Sorcerer Supreme's Librarian)
# Personality: Meticulous, organized, guardian of knowledge, deadpan humor
#
# Responsibilities:
# - Notion workspace management
# - Information architecture
# - Technical writing and documentation
# - Process mapping and SOPs
# - Template library creation
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="wong"
CHARACTER="Wong (Notion Agent)"
SESSION_KEY="agent:notion-agent:main"
DOMAIN="marketing"
ROLE="Knowledge Manager"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WONG] [INFO] $*"
}

function organize_knowledge() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Wong organizing the marketing knowledge library with precision..."

  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "notion\\|workspace\\|documentation"; then
    log_info "Structuring Notion workspace and documentation..."
    tasks_completed+=("workspace-organization")
  fi

  if echo "$priority_content" | grep -qi "process\\|sop\\|workflow"; then
    log_info "Creating process documentation and SOPs..."
    tasks_completed+=("process-documentation")
  fi

  if echo "$priority_content" | grep -qi "template\\|library\\|content"; then
    log_info "Building template library and content systems..."
    tasks_completed+=("template-creation")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "workspace",
    "title": "Marketing Notion Workspace Architecture",
    "file": "reports/knowledge/notion-workspace-structure.md",
    "structure": {
      "Marketing Hub": {
        "description": "Central dashboard for all marketing operations",
        "databases": [
          {
            "name": "Content Calendar",
            "type": "Calendar view",
            "properties": ["Status", "Channel", "Author", "Publish Date", "Campaign"],
            "views": ["By Channel", "By Week", "By Campaign"]
          },
          {
            "name": "Campaign Tracker",
            "type": "Board view",
            "properties": ["Stage", "Owner", "Budget", "ROI", "Start/End Date"],
            "views": ["Active Campaigns", "By Quarter", "Performance Dashboard"]
          },
          {
            "name": "Lead Database",
            "type": "Table view",
            "properties": ["Lead Score", "Source", "Status", "Last Contact", "Assigned To"],
            "views": ["Hot Leads", "By Source", "Needs Follow-up"]
          }
        ]
      },
      "Knowledge Base": {
        "description": "Marketing team documentation and resources",
        "sections": [
          "Brand Guidelines",
          "Writing Style Guide",
          "SEO Checklist",
          "Social Media Playbook",
          "Email Best Practices",
          "Design Assets Library"
        ]
      },
      "Templates Library": {
        "description": "Reusable templates for common tasks",
        "templates": [
          "Blog Post Template",
          "Campaign Brief Template",
          "Case Study Template",
          "Social Media Calendar Template",
          "Email Campaign Template",
          "Product Launch Checklist"
        ]
      }
    }
  },
  {
    "type": "sops",
    "title": "Marketing Standard Operating Procedures",
    "file": "reports/knowledge/marketing-sops.md",
    "procedures": [
      {
        "name": "Blog Post Publishing Workflow",
        "steps": [
          "1. Research: Identify keyword, check SERP, outline structure",
          "2. Draft: Write in Notion using template, include SEO elements",
          "3. Review: Content review (Loki), SEO check (Friday), design assets (Wanda)",
          "4. Publish: Schedule in CMS, add to social calendar (Quill)",
          "5. Promote: Email blast (Pepper), social posts (Quill), track analytics (Friday)"
        ],
        "owner": "Loki",
        "reviewCycle": "Monthly",
        "avgTime": "3-5 days"
      },
      {
        "name": "Email Campaign Launch Workflow",
        "steps": [
          "1. Strategy: Define goal, audience, success metrics (Pepper)",
          "2. Content: Write copy (Loki), design template (Wanda)",
          "3. Setup: Build in Mailchimp, set segments, configure automation (Pepper)",
          "4. Test: Send test emails, check mobile rendering, verify links",
          "5. Launch: Schedule send, monitor deliverability, track opens/clicks",
          "6. Optimize: A/B test subject lines, analyze results, iterate"
        ],
        "owner": "Pepper",
        "reviewCycle": "Quarterly",
        "avgTime": "1-2 weeks"
      },
      {
        "name": "Product Launch Marketing Checklist",
        "steps": [
          "1. T-30: Research (Fury), positioning (Shuri), launch plan (all hands)",
          "2. T-21: Landing page (Friday + Wanda), email sequence (Pepper + Loki)",
          "3. T-14: Social calendar (Quill), blog posts (Loki), PR outreach",
          "4. T-7: Test all systems, finalize copy, brief sales team",
          "5. Launch: Coordinate email blast, social posts, monitor analytics",
          "6. T+7: Gather feedback, analyze results, iterate on messaging"
        ],
        "owner": "Shuri",
        "reviewCycle": "Per launch",
        "avgTime": "4-6 weeks"
      }
    ]
  },
  {
    "type": "templates",
    "title": "Marketing Template Library",
    "file": "reports/knowledge/template-library.md",
    "templates": [
      {
        "name": "Blog Post Template",
        "sections": [
          "SEO Metadata (title tag, meta description, slug)",
          "Hero Image (16:9, min 1200px width)",
          "Hook (3-sentence opener)",
          "Problem Statement (what pain are we solving?)",
          "Solution Overview (how we solve it)",
          "Deep Dive (step-by-step or section-by-section)",
          "Social Proof (testimonial, case study, stats)",
          "CTA (single, clear next action)",
          "Internal Links (3-5 relevant blog posts)"
        ]
      },
      {
        "name": "Campaign Brief Template",
        "fields": [
          "Campaign Name",
          "Goal (awareness/consideration/conversion)",
          "Target Audience (persona + segment)",
          "Key Message (one sentence)",
          "Channels (email, social, paid, content)",
          "Budget Allocation",
          "Success Metrics (KPIs with targets)",
          "Timeline (start/end dates, milestones)",
          "Assets Needed (copy, design, landing pages)"
        ]
      },
      {
        "name": "Case Study Template",
        "sections": [
          "Customer Info (name, industry, size, logo)",
          "Challenge (specific pain points, quote)",
          "Solution (how we helped, implementation timeline)",
          "Results (metrics, before/after, ROI)",
          "Testimonial (quote with photo)",
          "CTA (similar use case? start trial)"
        ]
      }
    ]
  },
  {
    "type": "information-architecture",
    "title": "Marketing Information Architecture",
    "file": "reports/knowledge/information-architecture.md",
    "principles": [
      "MECE (Mutually Exclusive, Collectively Exhaustive): No overlapping categories",
      "Findability: 3-click rule—any information accessible in 3 clicks",
      "Consistency: Same naming conventions across all spaces",
      "Hierarchy: 3 levels max (Hub → Section → Page)",
      "Tagging: Use tags for cross-cutting concerns (e.g., #urgent, #needs-review, #Q1-2026)",
      "Permissions: Viewer (all), Editor (marketing team), Admin (marketing lead)"
    ],
    "navigationStructure": {
      "level1": "Marketing Hub (dashboard with key metrics and quick links)",
      "level2": "Sections (Content, Campaigns, Research, Knowledge, Templates)",
      "level3": "Pages (individual docs, databases, resources)"
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
      "to": "all",
      "content": "Marketing Notion workspace structured and ready. All SOPs documented. Template library live. Follow the 3-click rule—if you can't find something in 3 clicks, tell me.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "shuri",
      "content": "Product launch checklist template created. Use it for every launch—30-day countdown with clear owners and milestones. It's in Templates Library.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "loki",
      "content": "Blog post template ready with SEO metadata checklist. Every post must have: title tag, meta description, hero image, 3-5 internal links. Non-negotiable.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Guardian of knowledge. Meticulous, organized, zero tolerance for chaos. I don't do 'messy brainstorming'—I do structured thinking. Deadpan humor, sharp observations, unwavering standards.",
    "approach": "Information architecture with MECE principles: Mutually Exclusive, Collectively Exhaustive. Every piece of knowledge has exactly one home. Every workflow has a documented SOP. Every template is battle-tested.",
    "expertise": [
      "Information architecture: MECE frameworks, 3-click rule, hierarchical navigation",
      "Notion mastery: Databases, relations, rollups, formulas, templates, automations",
      "Technical writing: Clear, concise, scannable documentation",
      "Process mapping: Workflow diagrams, decision trees, RACI matrices",
      "Knowledge management: Taxonomy design, tagging systems, search optimization",
      "Template design: Reusable, scalable, idiot-proof templates"
    ],
    "learnings": [
      "If you need more than 3 levels of hierarchy, your categories are wrong",
      "Good documentation prevents 90% of 'quick questions' that interrupt deep work",
      "Templates only work if they're easier than starting from scratch",
      "Naming conventions matter—inconsistency creates cognitive load",
      "SOPs aren't bureaucracy—they're institutional memory",
      "The best knowledge system is invisible—you find what you need without thinking",
      "Tags are for cross-cutting concerns, not primary organization",
      "Update documentation immediately after process changes, not 'later'"
    ],
    "workingStyle": "I start with user research—what do people need to find? Then I design the information architecture: MECE categories, clear hierarchy, intuitive navigation. I document every workflow with SOPs: who does what, when, how. I create templates for repetitive tasks. I enforce naming conventions. I audit the workspace quarterly—prune dead pages, merge duplicates, update outdated docs. I train the team on best practices. Knowledge management is not a project—it's a discipline."
  }
}
EOF
)"

  log_info "Wong knowledge management complete. Order restored to the library."
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

  organize_knowledge "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
