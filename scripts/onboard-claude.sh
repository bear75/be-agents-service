#!/bin/bash
# scripts/onboard-claude.sh
# Quick onboarding for new Claude Code sessions

set -e

cd ~/HomeCare/beta-appcaire

echo "🎓 Welcome to AppCaire Monorepo!"
echo ""
echo "This will guide you through the essential knowledge for working in this codebase."
echo ""

# Use Claude to read and understand the learning materials
claude -p "Welcome to the AppCaire monorepo! This is your onboarding session.

Please read the following files in order and summarize your understanding:

1. docs/learning/01-monorepo-basics.md
   - Understand the monorepo structure (11 apps + 3 packages)
   - Learn the critical architecture rules
   - Understand the most common workflows
   - Memorize the common mistakes to avoid

2. /CLAUDE.md
   - Read the complete learnings
   - Understand GraphQL development workflow
   - Learn database migration workflow
   - Understand multi-app patterns

3. docs/ARCHITECT_PROMPT.md
   - Understand the full architecture
   - Learn the coding standards
   - Understand the monorepo principles

4. .claude/skills/ directory
   - Check available skills (graphql-full-stack, database-migration, extract-learnings)
   - Understand when to use each skill

After reading, please:
1. Summarize the key architecture rules (2-3 sentences each)
2. List the top 5 most critical mistakes to avoid
3. Explain the GraphQL full-stack workflow in steps
4. Ask any clarifying questions you have

This understanding will help you work effectively in this codebase!" --dangerously-skip-permissions

echo ""
echo "✅ Onboarding complete!"
echo ""
echo "You're now ready to work in the AppCaire monorepo."
echo ""
echo "Remember:"
echo "  - Always check CLAUDE.md for relevant app before starting"
echo "  - Use skills for common workflows (.claude/skills/)"
echo "  - Update CLAUDE.md with new learnings (compound/extract-learnings skill)"
echo "  - Ask questions if architecture rules are unclear"
echo ""
echo "Happy coding! 🚀"
echo ""
