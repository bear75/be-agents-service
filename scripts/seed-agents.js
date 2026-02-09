#!/usr/bin/env node
/**
 * Seed Agent Database
 * Initializes all teams and agents in the database
 * Run this after creating a fresh database or to reset agent data
 */

const db = require('../lib/database');

console.log('🌱 Seeding agent database...\n');

// ============================================
// TEAMS
// ============================================

const teams = [
  {
    id: 'team-engineering',
    name: 'Engineering',
    domain: 'engineering',
    description: '6 engineering specialists + orchestrator + senior reviewer'
  },
  {
    id: 'team-marketing',
    name: 'Marketing',
    domain: 'marketing',
    description: '10 Marvel character agents led by Jarvis'
  },
  {
    id: 'team-management',
    name: 'Management',
    domain: 'management',
    description: 'Executive leadership: CEO, CPO/CTO, CMO/CSO, HR Agent Lead'
  }
];

console.log('📋 Creating teams...');
for (const team of teams) {
  try {
    const existing = db.getTeamById(team.id);
    if (existing) {
      console.log(`  ⏭️  Team ${team.name} already exists`);
    } else {
      db.createTeam(team);
      console.log(`  ✅ Created team: ${team.name}`);
    }
  } catch (error) {
    console.error(`  ❌ Error creating team ${team.name}: ${error.message}`);
  }
}

console.log('');

// ============================================
// AGENTS
// ============================================

const agents = [
  // ========== ENGINEERING TEAM ==========
  {
    id: 'agent-orchestrator',
    teamId: 'team-engineering',
    name: 'Orchestrator',
    role: 'Scrum Master',
    emoji: '🎯',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-backend',
    teamId: 'team-engineering',
    name: 'Backend',
    role: 'Database & GraphQL',
    emoji: '⚙️',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-frontend',
    teamId: 'team-engineering',
    name: 'Frontend',
    role: 'React & UI',
    emoji: '🎨',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-infrastructure',
    teamId: 'team-engineering',
    name: 'Infrastructure',
    role: 'DevOps & CI/CD',
    emoji: '🏗️',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-verification',
    teamId: 'team-engineering',
    name: 'Verification',
    role: 'Testing & QA',
    emoji: '✅',
    llmPreference: 'haiku'
  },
  {
    id: 'agent-senior-reviewer',
    teamId: 'team-engineering',
    name: 'Senior Reviewer',
    role: 'Code Review',
    emoji: '🔍',
    llmPreference: 'opus'
  },
  {
    id: 'agent-db-architect',
    teamId: 'team-engineering',
    name: 'DB Architect',
    role: 'Database design, Prisma schema, Apollo GraphQL, PostgreSQL optimization, query performance',
    emoji: '🗄️',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-ux-designer',
    teamId: 'team-engineering',
    name: 'UX Designer',
    role: 'Modern UX 2026, responsive design, PWA, React Native, brand guidelines, accessibility, mobile-first',
    emoji: '🎭',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-docs-expert',
    teamId: 'team-engineering',
    name: 'Documentation Expert',
    role: 'Keep docs updated, archive obsolete docs, verify with team, publish to docs page, maintain accuracy',
    emoji: '📚',
    llmPreference: 'haiku'
  },
  {
    id: 'agent-levelup',
    teamId: 'team-engineering',
    name: 'Agent Levelup',
    role: 'Gamification expert: XP systems, achievements, leaderboards, progression mechanics, engagement optimization',
    emoji: '🎮',
    llmPreference: 'sonnet'
  },

  // ========== MARKETING TEAM (Marvel Avengers) ==========
  {
    id: 'agent-jarvis',
    teamId: 'team-marketing',
    name: 'Jarvis',
    role: 'Marketing Lead',
    emoji: '🤵',
    llmPreference: 'opus'
  },
  {
    id: 'agent-shuri',
    teamId: 'team-marketing',
    name: 'Shuri',
    role: 'Product Marketing',
    emoji: '👩‍🔬',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-fury',
    teamId: 'team-marketing',
    name: 'Fury',
    role: 'Market Research',
    emoji: '👁️',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-vision',
    teamId: 'team-marketing',
    name: 'Vision',
    role: 'SEO Analyst',
    emoji: '💎',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-loki',
    teamId: 'team-marketing',
    name: 'Loki',
    role: 'Content Writer',
    emoji: '✍️',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-quill',
    teamId: 'team-marketing',
    name: 'Quill',
    role: 'Social Media',
    emoji: '🎸',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-wanda',
    teamId: 'team-marketing',
    name: 'Wanda',
    role: 'Design',
    emoji: '✨',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-pepper',
    teamId: 'team-marketing',
    name: 'Pepper',
    role: 'Email Marketing',
    emoji: '💼',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-friday',
    teamId: 'team-marketing',
    name: 'Friday',
    role: 'Marketing Dev',
    emoji: '💻',
    llmPreference: 'sonnet'
  },
  {
    id: 'agent-wong',
    teamId: 'team-marketing',
    name: 'Wong',
    role: 'Notion Manager',
    emoji: '📚',
    llmPreference: 'haiku'
  },

  // ========== MANAGEMENT TEAM ==========
  {
    id: 'agent-ceo',
    teamId: 'team-management',
    name: 'CEO',
    role: 'Strategic Direction',
    emoji: '👔',
    llmPreference: 'opus'
  },
  {
    id: 'agent-cpo-cto',
    teamId: 'team-management',
    name: 'CPO/CTO',
    role: 'Engineering Lead',
    emoji: '🎯',
    llmPreference: 'opus'
  },
  {
    id: 'agent-cmo-cso',
    teamId: 'team-management',
    name: 'CMO/CSO',
    role: 'Marketing Lead',
    emoji: '📊',
    llmPreference: 'opus'
  },
  {
    id: 'agent-hr-lead',
    teamId: 'team-management',
    name: 'HR Agent Lead',
    role: 'Agent Development',
    emoji: '👥',
    llmPreference: 'sonnet'
  }
];

console.log('🤖 Creating agents...');
let created = 0;
let skipped = 0;

for (const agent of agents) {
  try {
    const existing = db.getAgentById(agent.id);
    if (existing) {
      console.log(`  ⏭️  Agent ${agent.emoji} ${agent.name} already exists`);
      skipped++;
    } else {
      db.createAgent(agent);
      console.log(`  ✅ Created agent: ${agent.emoji} ${agent.name} (${agent.role})`);
      created++;
    }
  } catch (error) {
    console.error(`  ❌ Error creating agent ${agent.name}: ${error.message}`);
  }
}

console.log('');
console.log('📊 Summary:');
console.log(`  ✅ Created: ${created} agents`);
console.log(`  ⏭️  Skipped: ${skipped} agents (already exist)`);
console.log(`  📋 Total: ${agents.length} agents`);
console.log('');
console.log('✨ Agent database seeded successfully!');
