#!/bin/bash
# scripts/ci-monitor.sh
# Monitors CI/CD runs and auto-fixes failures when possible

set -e

cd ~/HomeCare/beta-appcaire

# Ensure logs directory exists
mkdir -p logs

# Get latest CI run
echo "Checking latest CI run..."
LATEST_RUN=$(gh run list --limit 1 --json status,conclusion,databaseId,name,headBranch -q '.[0]' 2>/dev/null)

if [ -z "$LATEST_RUN" ]; then
  echo "No CI runs found or gh CLI not configured"
  exit 0
fi

STATUS=$(echo $LATEST_RUN | jq -r '.status')
CONCLUSION=$(echo $LATEST_RUN | jq -r '.conclusion')
RUN_ID=$(echo $LATEST_RUN | jq -r '.databaseId')
RUN_NAME=$(echo $LATEST_RUN | jq -r '.name')
BRANCH=$(echo $LATEST_RUN | jq -r '.headBranch')

echo "Latest run: #$RUN_ID ($RUN_NAME) on branch '$BRANCH'"
echo "Status: $STATUS"
echo "Conclusion: $CONCLUSION"

# Only process completed failures
if [ "$STATUS" != "completed" ]; then
  echo "Run still in progress. Exiting."
  exit 0
fi

if [ "$CONCLUSION" = "success" ]; then
  echo "✅ CI passed! No action needed."
  exit 0
fi

if [ "$CONCLUSION" != "failure" ]; then
  echo "Run conclusion: $CONCLUSION (not a failure). Exiting."
  exit 0
fi

# CI failed - fetch logs
echo ""
echo "❌ CI failure detected: Run #$RUN_ID"
echo "Fetching failure logs..."

LOG_FILE="logs/ci-failure-$RUN_ID.log"
gh run view $RUN_ID --log-failed > $LOG_FILE 2>&1

echo "Logs saved to: $LOG_FILE"
echo ""

# Analyze failure type
echo "Analyzing failure..."
if grep -q "TypeScript error" $LOG_FILE || grep -q "TS[0-9]" $LOG_FILE; then
  FAILURE_TYPE="typescript"
elif grep -q "ESLint" $LOG_FILE || grep -q "Parsing error" $LOG_FILE; then
  FAILURE_TYPE="lint"
elif grep -q "FAIL" $LOG_FILE || grep -q "Test failed" $LOG_FILE; then
  FAILURE_TYPE="test"
elif grep -q "Cannot find module '@appcaire/graphql'" $LOG_FILE; then
  FAILURE_TYPE="codegen"
else
  FAILURE_TYPE="unknown"
fi

echo "Failure type: $FAILURE_TYPE"
echo ""

# Determine if auto-fixable
AUTO_FIXABLE=false
case $FAILURE_TYPE in
  typescript|lint|codegen)
    AUTO_FIXABLE=true
    ;;
  test)
    # Only auto-fix if simple assertion failures, not integration issues
    if ! grep -q "ECONNREFUSED\|timeout\|network" $LOG_FILE; then
      AUTO_FIXABLE=true
    fi
    ;;
esac

if [ "$AUTO_FIXABLE" = false ]; then
  echo "⚠️  Failure is not auto-fixable. Manual intervention required."
  echo "Creating GitHub issue..."

  ISSUE_BODY="CI run #$RUN_ID failed on branch \`$BRANCH\`

**Failure type:** $FAILURE_TYPE
**Run:** https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions/runs/$RUN_ID

**Logs:**
\`\`\`
$(tail -50 $LOG_FILE)
\`\`\`

**Action required:** Manual investigation needed.
"

  gh issue create \
    --title "CI Failure: $RUN_NAME (#$RUN_ID)" \
    --body "$ISSUE_BODY" \
    --label "ci-failure" \
    2>/dev/null || echo "Failed to create issue (may already exist)"

  exit 1
fi

# Auto-fix attempt
echo "✅ Failure appears auto-fixable. Attempting fix..."
echo ""

# Checkout the failing branch
if [ "$BRANCH" = "main" ]; then
  echo "⚠️  Failure on main branch. Creating fix branch..."
  FIX_BRANCH="fix/ci-failure-$RUN_ID"
  git checkout -b $FIX_BRANCH main
else
  echo "Checking out branch: $BRANCH"
  git checkout $BRANCH
  git pull origin $BRANCH
  FIX_BRANCH=$BRANCH
fi

# Run Claude to fix
claude -p "CI build failed (run #$RUN_ID). Read $LOG_FILE to see the failure.

Failure type: $FAILURE_TYPE

Your task:
1. Read the log file to understand the error
2. Reproduce the error locally if possible
3. Fix the issue:
   - TypeScript errors: Fix type issues, ensure codegen run
   - Lint errors: Run 'yarn format' and fix ESLint issues
   - Codegen: Run 'yarn workspace @appcaire/graphql codegen'
   - Test failures: Fix failing test logic
4. Verify fix:
   - Run: turbo run type-check
   - Run: turbo run lint
   - Run: turbo run test (if test failure)
5. Commit with message: 'fix(ci): [description of fix]'
6. Push to trigger new CI run

Only fix if you're confident it's correct. If uncertain, create an issue instead." \
  --dangerously-skip-permissions

echo ""
echo "Claude attempted to fix the issue."
echo "Check git log to see if a fix was committed:"
echo "  git log -1"
echo ""
echo "If fixed and pushed, a new CI run should start automatically."
echo "Monitor at: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
echo ""
