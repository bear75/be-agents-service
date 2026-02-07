#!/bin/bash
# ============================================
# OpenClaw Lead Scraper
# ============================================
# Scans email inbox for leads and writes to leads.json
# Triggered: Every 15 minutes via launchd
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="$SERVICE_ROOT/.compound-state/data"
LEADS_FILE="$DATA_DIR/leads.json"
LOG_DIR="$SERVICE_ROOT/logs"
LOG_FILE="$LOG_DIR/openclaw.log"

# Source environment variables
if [ -f "$SERVICE_ROOT/.env" ]; then
  source "$SERVICE_ROOT/.env"
else
  echo "⚠️  Warning: .env file not found. Email scraping will not work."
  echo "Copy .env.template to .env and configure your email credentials."
  exit 1
fi

# Ensure directories exist
mkdir -p "$DATA_DIR"
mkdir -p "$LOG_DIR"

# Initialize leads file if it doesn't exist
if [ ! -f "$LEADS_FILE" ]; then
  echo "[]" > "$LEADS_FILE"
fi

# Logging function
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Calculate lead score based on keywords and domain
calculate_score() {
  local email_body="$1"
  local sender_email="$2"
  local score=50  # Base score

  # High-value keywords (+30 points)
  if echo "$email_body" | grep -iE "(demo|trial|pricing|quote|partnership|integration)" > /dev/null; then
    score=$((score + 30))
  fi

  # Medium keywords (+15 points)
  if echo "$email_body" | grep -iE "(interested|inquiry|contact|schedule|boka|offert)" > /dev/null; then
    score=$((score + 15))
  fi

  # Company domain check (+20 points for business domains)
  if echo "$sender_email" | grep -E "@[^@]+\.(com|se|ai|co\.uk|io|net)$" > /dev/null && \
     ! echo "$sender_email" | grep -iE "@(gmail|yahoo|hotmail|outlook|icloud)" > /dev/null; then
    score=$((score + 20))
  fi

  # Urgency keywords (+10 points)
  if echo "$email_body" | grep -iE "(urgent|asap|immediately|soon|quickly)" > /dev/null; then
    score=$((score + 10))
  fi

  # Phone number mentioned (+10 points)
  if echo "$email_body" | grep -E "\+?[0-9]{1,4}[-\s]?[0-9]{2,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}" > /dev/null; then
    score=$((score + 10))
  fi

  # Employee count mentioned (+15 points)
  if echo "$email_body" | grep -iE "[0-9]+\s*(employees|staff|workers|anställda)" > /dev/null; then
    score=$((score + 15))
  fi

  echo $score
}

# Extract contact name from email header
extract_name() {
  local from_header="$1"
  # Extract name from "Name <email>" format
  if echo "$from_header" | grep -E "^[^<]+<" > /dev/null; then
    echo "$from_header" | sed -E 's/^([^<]+)<.*/\1/' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/"//g'
  else
    # No name, use email prefix
    echo "$from_header" | sed 's/@.*//'
  fi
}

# Extract company from email domain
extract_company() {
  local email="$1"
  local domain=$(echo "$email" | sed 's/.*@//' | sed 's/\..*//')
  # Capitalize first letter
  echo "$domain" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}'
}

# Extract phone number from email body
extract_phone() {
  local body="$1"
  # Look for phone patterns
  echo "$body" | grep -oE "\+?[0-9]{1,4}[-\s]?[0-9]{2,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}" | head -1 || echo ""
}

# Scrape emails from a single account
scrape_account() {
  local email_user="$1"
  local email_pass="$2"
  local source_label="$3"

  log "Checking $email_user..."

  # Connect to IMAP and search for UNSEEN emails
  local unseen_emails=$(curl -s --url "imaps://${EMAIL_IMAP_HOST}:${EMAIL_IMAP_PORT}/INBOX" \
    --user "${email_user}:${email_pass}" \
    -X "SEARCH UNSEEN" 2>/dev/null || echo "")

  if [ -z "$unseen_emails" ] || [ "$unseen_emails" = "* SEARCH" ]; then
    log "  No unread emails"
    return
  fi

  # Extract message IDs
  local msg_ids=$(echo "$unseen_emails" | grep "^\* SEARCH" | sed 's/^\* SEARCH //' || echo "")

  if [ -z "$msg_ids" ]; then
    log "  No unread emails"
    return
  fi

  log "  Found unread emails: $msg_ids"

  # Process each message
  for msg_id in $msg_ids; do
    # Fetch email headers and body
    local email_data=$(curl -s --url "imaps://${EMAIL_IMAP_HOST}:${EMAIL_IMAP_PORT}/INBOX;UID=$msg_id" \
      --user "${email_user}:${email_pass}" 2>/dev/null || echo "")

    if [ -z "$email_data" ]; then
      continue
    fi

    # Extract From header
    local from_header=$(echo "$email_data" | grep -i "^From:" | head -1 | sed 's/^From: //')
    local sender_email=$(echo "$from_header" | grep -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" | head -1)

    # Extract Subject
    local subject=$(echo "$email_data" | grep -i "^Subject:" | head -1 | sed 's/^Subject: //')

    # Get email body (simplified - just get all lines after headers)
    local email_body=$(echo "$email_data" | awk '/^$/{body=1; next} body')

    # Check if email matches lead keywords
    local keywords="${EMAIL_LEAD_KEYWORDS:-demo,trial,pricing,contact,inquiry,interested,quote,schedule,partnership,integration}"
    local keyword_match=false

    IFS=',' read -ra KEYWORD_ARRAY <<< "$keywords"
    for keyword in "${KEYWORD_ARRAY[@]}"; do
      if echo "$email_body $subject" | grep -iq "$keyword"; then
        keyword_match=true
        break
      fi
    done

    if [ "$keyword_match" = false ]; then
      log "    Message $msg_id: No lead keywords found"
      # Mark as read anyway to avoid reprocessing
      curl -s --url "imaps://${EMAIL_IMAP_HOST}:${EMAIL_IMAP_PORT}/INBOX;UID=$msg_id" \
        --user "${email_user}:${email_pass}" \
        -X "STORE $msg_id +FLAGS \\Seen" > /dev/null 2>&1
      continue
    fi

    # Extract lead information
    local contact_name=$(extract_name "$from_header")
    local company=$(extract_company "$sender_email")
    local phone=$(extract_phone "$email_body")
    local score=$(calculate_score "$email_body $subject" "$sender_email")

    # Determine status based on score
    local status="new"
    if [ $score -ge 90 ]; then
      status="hot"
    elif [ $score -ge 70 ]; then
      status="qualified"
    elif [ $score -ge 50 ]; then
      status="warm"
    fi

    # Create lead JSON
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local lead_id="lead-$(date +%s)-$RANDOM"

    # Truncate email body to first 500 chars for notes
    local notes=$(echo "$email_body" | head -c 500 | tr '\n' ' ' | sed 's/"/\\"/g')

    local lead_json=$(cat <<EOF
{
  "id": "$lead_id",
  "source": "email-$source_label",
  "status": "$status",
  "company": "$company",
  "contactName": "$contact_name",
  "email": "$sender_email",
  "phone": "$phone",
  "createdAt": "$timestamp",
  "assignedTo": "fury",
  "score": $score,
  "notes": "$notes",
  "originalSubject": "$subject"
}
EOF
)

    # Append to leads file
    local existing_leads=$(cat "$LEADS_FILE")
    local updated_leads=$(echo "$existing_leads" | jq --argjson new_lead "$lead_json" '. += [$new_lead]')
    echo "$updated_leads" > "$LEADS_FILE"

    log "    ✅ New lead: $contact_name ($sender_email) - Score: $score"

    # Mark email as read
    curl -s --url "imaps://${EMAIL_IMAP_HOST}:${EMAIL_IMAP_PORT}/INBOX;UID=$msg_id" \
      --user "${email_user}:${email_pass}" \
      -X "STORE $msg_id +FLAGS \\Seen" > /dev/null 2>&1
  done
}

# Main execution
log "📧 OpenClaw Lead Scraper Starting..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  log "❌ Error: jq is required but not installed. Install with: brew install jq"
  exit 1
fi

# Counter for new leads
INITIAL_COUNT=$(cat "$LEADS_FILE" | jq 'length')

# Scrape all configured email accounts
for i in {1..9}; do
  email_var="EMAIL_${i}_USER"
  pass_var="EMAIL_${i}_PASSWORD"

  email_user="${!email_var:-}"
  email_pass="${!pass_var:-}"

  if [ -n "$email_user" ] && [ -n "$email_pass" ] && [ "$email_user" != "your-app-password-${i}" ]; then
    scrape_account "$email_user" "$email_pass" "$email_user"
  fi
done

# Calculate new leads found
FINAL_COUNT=$(cat "$LEADS_FILE" | jq 'length')
NEW_LEADS=$((FINAL_COUNT - INITIAL_COUNT))

log ""
log "📊 Lead Statistics:"
log "Total leads: $FINAL_COUNT"
log "New leads this run: $NEW_LEADS"
log "Hot leads (90+): $(cat "$LEADS_FILE" | jq '[.[] | select(.score >= 90)] | length')"
log "Qualified leads (70-89): $(cat "$LEADS_FILE" | jq '[.[] | select(.score >= 70 and .score < 90)] | length')"
log "Warm leads (50-69): $(cat "$LEADS_FILE" | jq '[.[] | select(.score >= 50 and .score < 70)] | length')"

log ""
log "✅ Lead scraper completed"
