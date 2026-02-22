#!/bin/bash
#
# LLM Invoke — Route tasks to Ollama (local) or Claude (paid)
#
# Usage:
#   llm-invoke.sh <task-type> <prompt> [--stdin]
#   llm-invoke.sh analyze "Extract priority from: ..."
#   llm-invoke.sh prd "Create PRD for: ..."
#   llm-invoke.sh uncertain "..."  # Prompts user to choose
#
# Task types and routing:
#   analyze   → Ollama (phi) — short text, JSON extraction, triage
#   convert   → Ollama (phi) — format conversion, structured extraction
#   triage    → Ollama (phi) — inbox triage, categorization
#   prd       → Claude — long-form creative docs
#   implement → Claude — code changes, implementation
#   review    → Claude — learning extraction, complex analysis
#   uncertain → Asks user via stdin/Telegram if configured
#
set -euo pipefail

TASK_TYPE="${1:-}"
PROMPT="${2:-}"
# If prompt empty and stdin is a pipe, read prompt from stdin (for large prompts)
if [[ -z "$PROMPT" ]] && [[ ! -t 0 ]]; then
  PROMPT=$(cat)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment
[[ -f "$HOME/.config/caire/env" ]] && source "$HOME/.config/caire/env"

# OLLAMA_MODEL: local model for simple tasks (default: phi)
OLLAMA_MODEL="${OLLAMA_MODEL:-phi}"
OLLAMA_AVAILABLE=false
if command -v ollama &>/dev/null; then
  if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
    OLLAMA_AVAILABLE=true
  fi
fi

usage() {
  echo "Usage: $0 <task-type> <prompt> [--stdin]"
  echo ""
  echo "Task types:"
  echo "  analyze   — Short analysis, JSON extraction → Ollama"
  echo "  convert   — Format/structure conversion → Ollama"
  echo "  triage    — Inbox triage, categorization → Ollama"
  echo "  prd       — PRD creation, long docs → Claude"
  echo "  implement — Code implementation → Claude"
  echo "  review    — Learning extraction, complex analysis → Claude"
  echo "  uncertain — Ask user which model to use"
  echo ""
  echo "Environment: OLLAMA_MODEL (default: phi), OLLAMA_AVAILABLE auto-detected"
  exit 1
}

ask_user() {
  local prompt_text="$1"
  # Headless (launchd): default to Claude, no prompt possible
  if ! [[ -t 0 ]]; then
    echo "LLM ROUTING (headless): Uncertain → defaulting to Claude" >&2
    echo "claude"
    return 0
  fi
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo "LLM ROUTING: Uncertain which model to use"
  echo "═══════════════════════════════════════════════════════════"
  echo ""
  echo "Task: ${prompt_text:0:200}..."
  echo ""
  echo "Options:"
  echo "  1) ollama  — Local (free, fast, good for simple tasks)"
  echo "  2) claude  — Paid (better for complex/code tasks)"
  echo ""
  printf "Choose [1/2] (default: 2): "
  read -r choice
  case "${choice:-2}" in
    1) echo "ollama"; return 0 ;;
    2) echo "claude"; return 0 ;;
    *) echo "claude"; return 0 ;;
  esac
}

run_ollama() {
  local prompt="$1"
  if ! $OLLAMA_AVAILABLE; then
    echo "⚠️  Ollama not available (model $OLLAMA_MODEL not found). Falling back to Claude." >&2
    run_claude "$prompt"
    return
  fi
  local result
  result=$(echo "$prompt" | ollama run "$OLLAMA_MODEL" 2>/dev/null) || true
  if [[ -z "$result" ]]; then
    echo "⚠️  Ollama returned empty (model may have failed). Falling back to Claude." >&2
    run_claude "$prompt"
  else
    echo "$result"
  fi
}

run_claude() {
  local prompt="$1"
  claude -p "$prompt" --dangerously-skip-permissions 2>/dev/null
}

case "$TASK_TYPE" in
  analyze|convert|triage)
    if $OLLAMA_AVAILABLE; then
      run_ollama "$PROMPT"
    else
      run_claude "$PROMPT"
    fi
    ;;
  prd|implement|review)
    run_claude "$PROMPT"
    ;;
  uncertain)
    CHOICE=$(ask_user "$PROMPT")
    if [[ "$CHOICE" == "ollama" ]]; then
      run_ollama "$PROMPT"
    else
      run_claude "$PROMPT"
    fi
    ;;
  *)
    usage
    ;;
esac
