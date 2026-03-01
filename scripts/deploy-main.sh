#!/usr/bin/env bash
# Deploy latest origin/main to the Mac mini service host.
# Intended to be called remotely (e.g. GitHub Actions via SSH).
#
# Environment overrides:
#   REPO_DIR      (default: ~/HomeCare/be-agents-service)
#   DEPLOY_BRANCH (default: main)
#   HEALTH_URL    (default: http://localhost:3010/health)
#   HEALTH_RETRIES (default: 30)
#   HEALTH_SLEEP_SECONDS (default: 2)
#
set -euo pipefail

log() { echo "[deploy-main] $*"; }
fail() { echo "[deploy-main] ERROR: $*" >&2; exit 1; }

export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_DIR="${REPO_DIR:-$HOME/HomeCare/be-agents-service}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
HEALTH_URL="${HEALTH_URL:-http://localhost:3010/health}"
HEALTH_RETRIES="${HEALTH_RETRIES:-30}"
HEALTH_SLEEP_SECONDS="${HEALTH_SLEEP_SECONDS:-2}"

[[ -d "$REPO_DIR/.git" ]] || fail "Repository not found at $REPO_DIR"
command -v git >/dev/null 2>&1 || fail "git is required"
command -v yarn >/dev/null 2>&1 || fail "yarn is required"
command -v curl >/dev/null 2>&1 || fail "curl is required"

cd "$REPO_DIR"

log "Fetching latest origin/$DEPLOY_BRANCH"
git fetch origin "$DEPLOY_BRANCH"

if git show-ref --verify --quiet "refs/heads/$DEPLOY_BRANCH"; then
  git checkout "$DEPLOY_BRANCH"
else
  git checkout -b "$DEPLOY_BRANCH" "origin/$DEPLOY_BRANCH"
fi

log "Resetting local branch to origin/$DEPLOY_BRANCH"
git reset --hard "origin/$DEPLOY_BRANCH"

log "Running restart sequence"
./scripts/restart-darwin.sh

log "Waiting for health endpoint: $HEALTH_URL"
for ((i = 1; i <= HEALTH_RETRIES; i++)); do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    log "Deploy successful. Service is healthy."
    exit 0
  fi
  sleep "$HEALTH_SLEEP_SECONDS"
done

fail "Service did not become healthy at $HEALTH_URL"
