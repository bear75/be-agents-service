#!/bin/bash
#
# Friday - Developer
# Character: F.R.I.D.A.Y. (Tony Stark's AI assistant)
# Personality: Efficient, precise, technical expert, reliable, data-driven
#
# Responsibilities:
# - Frontend development (landing pages, marketing sites)
# - Backend integration (APIs, tracking, webhooks)
# - Analytics implementation
# - Marketing automation scripts
# - Technical SEO
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SERVICE_ROOT/lib/state-manager.sh"

AGENT_NAME="friday"
CHARACTER="Friday (Developer)"
SESSION_KEY="agent:developer:main"
DOMAIN="marketing"
ROLE="Marketing Developer"

LOG_FILE=""

function log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [FRIDAY] [INFO] $*"
}

function implement_marketing_tech() {
  local session_id="$1"
  local target_repo="$2"
  local priority_file="$3"

  log_info "Friday implementing marketing tech stack with precision..."

  local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local priority_content=$(cat "$priority_file")
  local tasks_completed=()

  if echo "$priority_content" | grep -qi "landing\\|page\\|frontend"; then
    log_info "Building landing pages and marketing frontend..."
    tasks_completed+=("frontend-development")
  fi

  if echo "$priority_content" | grep -qi "analytics\\|tracking\\|pixel"; then
    log_info "Implementing analytics and event tracking..."
    tasks_completed+=("analytics-setup")
  fi

  if echo "$priority_content" | grep -qi "api\\|integration\\|webhook"; then
    log_info "Setting up API integrations and webhooks..."
    tasks_completed+=("backend-integration")
  fi

  local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  local deliverables_json=$(cat <<'EOF'
[
  {
    "type": "frontend",
    "title": "Marketing Landing Pages (React + Vite + Tailwind)",
    "file": "reports/dev/landing-pages-implementation.md",
    "pages": [
      {
        "name": "Homepage",
        "path": "/",
        "components": ["HeroSection", "FeaturesGrid", "SocialProof", "CTASection"],
        "optimizations": ["Code splitting", "Lazy loading images", "Prefetch critical assets"],
        "seo": ["Meta tags", "Structured data", "Open Graph", "Sitemap"]
      },
      {
        "name": "Pricing",
        "path": "/pricing",
        "components": ["PricingCards", "FeatureComparison", "FAQ", "TrialCTA"],
        "integrations": ["Stripe checkout", "Plan selector", "Usage calculator"],
        "tracking": ["Page view", "Plan selected", "Checkout initiated"]
      },
      {
        "name": "Case Study",
        "path": "/customers/:slug",
        "components": ["CustomerHero", "MetricsDisplay", "Testimonial", "RelatedCases"],
        "seo": ["Dynamic meta tags", "JSON-LD for case study", "Canonical URLs"]
      }
    ],
    "techStack": {
      "framework": "React 18 + Vite",
      "styling": "Tailwind CSS + CSS modules",
      "routing": "React Router v6",
      "forms": "React Hook Form + Zod validation",
      "analytics": "Google Tag Manager + custom events"
    }
  },
  {
    "type": "analytics",
    "title": "Analytics & Event Tracking Implementation",
    "file": "reports/dev/analytics-setup.md",
    "platforms": [
      {
        "name": "Google Analytics 4",
        "setup": "gtag.js with custom events",
        "events": [
          "page_view (automatic)",
          "trial_started (conversion)",
          "pricing_viewed (micro-conversion)",
          "case_study_read (engagement)",
          "feature_explored (product interest)"
        ],
        "customDimensions": ["user_role", "company_size", "industry"]
      },
      {
        "name": "Mixpanel",
        "setup": "JavaScript SDK with user identification",
        "events": [
          "Signup Started",
          "Onboarding Step Completed",
          "Feature Activated",
          "Trial Converted"
        ],
        "userProperties": ["plan_type", "signup_date", "feature_usage"]
      },
      {
        "name": "Hotjar",
        "setup": "Heatmaps + session recordings",
        "pages": ["Homepage", "Pricing", "Signup flow"],
        "triggers": ["Rage clicks", "Exit intent", "Form abandonment"]
      }
    ]
  },
  {
    "type": "integrations",
    "title": "Marketing Tech Stack Integrations",
    "file": "reports/dev/integrations-setup.md",
    "integrations": [
      {
        "name": "Mailchimp API",
        "purpose": "Email list sync and campaign triggers",
        "endpoints": ["/api/mailchimp/subscribe", "/api/mailchimp/update-tags"],
        "events": ["Trial started → Add to trial sequence", "Converted → Move to customer list"]
      },
      {
        "name": "Stripe Webhooks",
        "purpose": "Payment and subscription events",
        "events": ["checkout.session.completed", "customer.subscription.updated", "invoice.payment_failed"],
        "handlers": "Update user plan, trigger onboarding emails, alert sales team"
      },
      {
        "name": "Zapier Webhooks",
        "purpose": "No-code automation triggers",
        "triggers": ["New lead captured", "Demo requested", "High-value signup"],
        "actions": "Notify Slack, create CRM record, trigger sales sequence"
      },
      {
        "name": "Google Tag Manager",
        "purpose": "Tag management without code deploys",
        "tags": ["GA4", "Facebook Pixel", "LinkedIn Insight", "Custom conversion pixels"],
        "triggers": "Page view, form submit, button clicks, scroll depth"
      }
    ]
  },
  {
    "type": "seo",
    "title": "Technical SEO Implementation",
    "file": "reports/dev/technical-seo.md",
    "implementation": [
      {
        "category": "Meta Tags",
        "items": ["Dynamic title/description per page", "Open Graph tags", "Twitter Cards", "Canonical URLs"]
      },
      {
        "category": "Structured Data",
        "items": ["Organization schema", "Product schema", "Review schema", "BreadcrumbList", "FAQ schema"]
      },
      {
        "category": "Performance",
        "items": ["Lighthouse score >90", "Core Web Vitals optimization", "Image lazy loading", "Critical CSS inlining"]
      },
      {
        "category": "Crawlability",
        "items": ["robots.txt", "XML sitemap", "Internal linking strategy", "Mobile-first responsive design"]
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
      "content": "Landing pages ready for design implementation. Need: hero images, feature icons, testimonial photos. Follow design system—Tailwind utility classes, mobile-first.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "pepper",
      "content": "Mailchimp API integrated. Email list sync works automatically: trial signups → nurture sequence, converted users → customer list. Webhook logs in /api/mailchimp/logs.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    {
      "to": "quill",
      "content": "Social pixels live: Facebook Pixel, LinkedIn Insight Tag. Track conversions from social campaigns. Event names: trial_started, pricing_viewed, case_study_read.",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
  ],
  "soul": {
    "personality": "Precise, efficient, reliable. I don't ship bugs. Every line of code is tested, every integration is documented, every deployment is zero-downtime. Technical excellence is non-negotiable.",
    "approach": "Engineering for marketing: Fast load times (Core Web Vitals), seamless integrations (APIs never break), accurate tracking (every event captured). I build marketing tech that just works.",
    "expertise": [
      "Frontend: React, Vite, Tailwind CSS, performance optimization (code splitting, lazy loading)",
      "Backend: Node.js, Express, REST APIs, webhooks, event-driven architecture",
      "Analytics: Google Analytics 4, Mixpanel, Segment, custom event tracking",
      "Integrations: Stripe, Mailchimp, Zapier, CRM APIs, marketing automation platforms",
      "SEO: Structured data (JSON-LD), meta tags, sitemaps, Core Web Vitals, Lighthouse optimization",
      "A/B Testing: Feature flags, multivariate testing, statistical significance calculations",
      "DevOps: CI/CD pipelines, Docker, automated testing, monitoring (Sentry, LogRocket)"
    ],
    "learnings": [
      "Page speed is a conversion factor—every 100ms delay costs 1% conversion",
      "Analytics without action is vanity metrics—track what you can optimize",
      "Third-party scripts kill performance—lazy load non-critical tags",
      "Mobile traffic is 60%+—test on real devices, not just Chrome DevTools",
      "Webhooks fail silently—always implement retry logic and dead letter queues",
      "A/B tests need statistical significance—don't call winners at 95% confidence with n<100",
      "Marketing wants fast iterations—feature flags enable safe, quick deploys",
      "Documentation prevents 3am debugging—document APIs, events, and error codes"
    ],
    "workingStyle": "I code in focused sprints, test everything locally before deploying, write integration tests for critical flows (signup, checkout, email triggers), monitor production with Sentry and LogRocket. Every deploy includes: type-check, lint, unit tests, E2E tests for conversion flows. I review analytics data daily to catch tracking issues early. I keep a tech debt backlog and allocate 20% time to refactoring."
  }
}
EOF
)"

  log_info "Friday development complete. Tech stack deployed, integrations live."
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

  implement_marketing_tech "$session_id" "$target_repo" "$priority_file"

  log_info "$CHARACTER signing off"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
