#!/usr/bin/env node
/**
 * Test XP Earning from Task Completion
 *
 * This simulates a real task completion and shows how XP is earned automatically.
 */

const path = require("path");
const db = require("./lib/database");

console.log("\n🧪 Testing Automatic XP Earning from Task Completion\n");
console.log("=".repeat(60));

// 1. Create a test session
const sessionId = "session-test-" + Date.now();
console.log("\n1. Creating test session:", sessionId);

db.createSession({
  sessionId,
  teamId: "team-engineering",
  targetRepo: "/Users/bjornevers_MacPro/HomeCare/beta-appcaire",
  priorityFile: "reports/test.md",
  branchName: "test/gamification",
});

// 2. Create a test task
const taskId = "task-test-" + Date.now();
console.log("2. Creating test task for Backend agent:", taskId);

db.createTask({
  taskId,
  sessionId,
  agentId: "agent-backend",
  taskDescription: "Test task: Update Prisma schema",
});

// 3. Complete the task (this triggers XP award automatically)
console.log("3. Completing task... (this should award XP)");

db.updateTaskStatus(taskId, "completed", "sonnet");

console.log("\n✅ Task completed!");
console.log("\n📊 Checking Backend agent stats...");

// 4. Check agent gamification
const gamification = require("./lib/gamification");
const agentGamification = gamification.getAgentGamification("agent-backend");

console.log("\n" + "=".repeat(60));
console.log("Backend Agent Gamification Status:");
console.log("=".repeat(60));
console.log(
  "Level:",
  agentGamification.level,
  agentGamification.level_emoji,
  agentGamification.title,
);
console.log("Total XP:", agentGamification.total_xp);
console.log("Current XP:", agentGamification.current_xp);
console.log("XP to Next Level:", agentGamification.xp_to_next_level);
console.log("Current Streak:", agentGamification.current_streak);
console.log("Achievements:", agentGamification.achievements_unlocked);

if (agentGamification.recentXP && agentGamification.recentXP.length > 0) {
  console.log("\n📜 Recent XP Transactions:");
  agentGamification.recentXP.forEach((tx) => {
    console.log(
      `  ${tx.amount > 0 ? "+" : ""}${tx.amount} XP - ${tx.reason} (${tx.source_type})`,
    );
  });
}

console.log("\n" + "=".repeat(60));
console.log("✨ Test complete! Refresh dashboard to see changes.");
console.log("🌐 http://localhost:3030/management-team.html");
console.log("=".repeat(60) + "\n");
