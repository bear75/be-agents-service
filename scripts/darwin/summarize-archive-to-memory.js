#!/usr/bin/env node
/**
 * Summarize DARWIN archive/notes and research/ into memory/context.md, and update
 * memory/decisions.md and memory/learnings.md with restructure notes.
 * Run this on your machine (where DARWIN is on disk) after the memory restructure.
 *
 * Usage: node summarize-archive-to-memory.js [workspace-path]
 *   workspace-path defaults to env DARWIN_WORKSPACE_PATH or config (darwin) path.
 */

const fs = require("fs");
const path = require("path");

const MAX_EXCERPT_LINES = 12;
const MAX_EXCERPT_CHARS = 500;
const SECTION_HEADER = "## Summary of archived content (from restructure)";

function getWorkspacePath() {
  const arg = process.argv[2];
  if (arg) return path.resolve(arg);
  if (process.env.DARWIN_WORKSPACE_PATH) return path.resolve(process.env.DARWIN_WORKSPACE_PATH);
  const serviceRoot = path.resolve(__dirname, "../..");
  const configPath = path.join(serviceRoot, "config/repos.yaml");
  if (!fs.existsSync(configPath)) return null;
  const yaml = fs.readFileSync(configPath, "utf8");
  const match = yaml.match(/darwin:[\s\S]*?path:\s*([^\s#\n]+)/);
  if (!match) return null;
  let p = match[1].trim().replace(/^["']|["']$/g, "");
  if (p.startsWith("~")) p = path.join(process.env.HOME || "", p.slice(1));
  return path.resolve(p);
}

function collectMdFiles(dir, baseDir, list) {
  if (!fs.existsSync(dir)) return;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    const rel = path.relative(baseDir, full);
    if (e.isDirectory() && !e.name.startsWith(".")) {
      collectMdFiles(full, baseDir, list);
    } else if (e.isFile() && e.name.endsWith(".md")) {
      list.push(rel);
    }
  }
}

function excerpt(content) {
  const lines = content.split(/\n/).slice(0, MAX_EXCERPT_LINES);
  let text = lines.join("\n").replace(/```[\s\S]*?```/g, "").trim();
  if (text.length > MAX_EXCERPT_CHARS) text = text.slice(0, MAX_EXCERPT_CHARS) + "…";
  return text.replace(/\n+/g, " ").trim() || "(no text)";
}

function buildSummary(workspacePath) {
  const archiveNotes = path.join(workspacePath, "archive", "notes");
  const research = path.join(workspacePath, "research");
  const sections = [];

  for (const [label, dir] of [
    ["archive/notes", archiveNotes],
    ["research", research],
  ]) {
    const files = [];
    collectMdFiles(dir, dir, files);
    files.sort();
    if (files.length === 0) continue;
    const bullets = [];
    for (const rel of files) {
      const full = path.join(dir, rel);
      let content = "";
      try {
        content = fs.readFileSync(full, "utf8");
      } catch (_) {
        content = "";
      }
      const ex = excerpt(content);
      bullets.push(`- **${rel}**: ${ex}`);
    }
    sections.push(`### From ${label}\n\n${bullets.join("\n")}`);
  }

  if (sections.length === 0) return null;
  return `${SECTION_HEADER}\n\nContent that was moved out of memory/ during restructure. Full files are in \`archive/notes/\` and \`research/\`.\n\n${sections.join("\n\n")}`;
}

function ensureMemoryDir(workspacePath) {
  const memoryDir = path.join(workspacePath, "memory");
  if (!fs.existsSync(memoryDir)) fs.mkdirSync(memoryDir, { recursive: true });
  return memoryDir;
}

function updateContext(workspacePath, summaryBlock) {
  const memoryDir = ensureMemoryDir(workspacePath);
  const contextPath = path.join(memoryDir, "context.md");
  const template = `# Project Context

Background information that agents need to do good work.
Update this when the project direction changes.

## What is this project?

<!-- Describe your project in a few sentences -->

## Current focus

<!-- What are we building right now? -->

## Key constraints

<!-- Technical, business, or timeline constraints -->

## Team & roles

<!-- Who's involved and what they do -->

## Important links

<!-- GitHub repos, docs, dashboards, etc. -->
`;

  let content = "";
  if (fs.existsSync(contextPath)) {
    content = fs.readFileSync(contextPath, "utf8");
    if (content.includes(SECTION_HEADER)) {
      content = content.replace(/\n*## Summary of archived content \(from restructure\)[\s\S]*/, "");
    }
  }
  if (!content.trim()) content = template;
  content = content.trimEnd();
  if (summaryBlock) content += "\n\n" + summaryBlock + "\n";
  fs.writeFileSync(contextPath, content, "utf8");
  console.log("Updated memory/context.md");
}

function appendDecision(workspacePath) {
  const memoryDir = ensureMemoryDir(workspacePath);
  const decisionsPath = path.join(memoryDir, "decisions.md");
  const block = `
## 2026-03-02: Memory restructure – content moved out of memory/

**Context:** memory/ had 48+ files (run outputs, dated notes, methodology docs) that diluted agent focus. Restructure moved them to archive/notes and research/.

**Decision:** Keep in memory/ only context.md, decisions.md, learnings.md (and optional identity files). Dated notes and run outputs live in archive/notes and research/.

**Consequences:** Agents read only the three core memory files; full archived content is summarized in context.md and lives in archive/ and research/.
`;

  let content = "";
  if (fs.existsSync(decisionsPath)) {
    content = fs.readFileSync(decisionsPath, "utf8");
  } else {
    content = `# Decisions Log

Record key architecture, product, and process decisions here.
Both you and agents can reference this for context.

<!-- Format:
## YYYY-MM-DD: Decision Title

**Context:** Why this decision was needed
**Decision:** What was decided
**Consequences:** What this means going forward
-->
`;
  }
  if (content.includes("Memory restructure – content moved")) return;
  fs.writeFileSync(decisionsPath, content.trimEnd() + block + "\n", "utf8");
  console.log("Updated memory/decisions.md");
}

function appendLearning(workspacePath) {
  const memoryDir = ensureMemoryDir(workspacePath);
  const learningsPath = path.join(memoryDir, "learnings.md");
  const bullet = "- Archived run outputs and dated notes (48+ files) live in archive/notes and research/. See context.md section \"Summary of archived content\" for a file-by-file summary. (tags: darwin, restructure)\n";

  let content = "";
  if (fs.existsSync(learningsPath)) {
    content = fs.readFileSync(learningsPath, "utf8");
  } else {
    content = `# Learnings

Accumulated learnings across agent sessions and human work.
Agents append here after each session. You can add your own too.

`;
  }
  if (content.includes("archive/notes and research/")) return;
  fs.writeFileSync(learningsPath, content.trimEnd() + "\n" + bullet, "utf8");
  console.log("Updated memory/learnings.md");
}

function main() {
  const workspacePath = getWorkspacePath();
  if (!workspacePath || !fs.existsSync(workspacePath)) {
    console.error("DARWIN workspace not found. Set DARWIN_WORKSPACE_PATH or pass path as first argument.");
    process.exit(1);
  }
  const summaryBlock = buildSummary(workspacePath);
  updateContext(workspacePath, summaryBlock);
  appendDecision(workspacePath);
  appendLearning(workspacePath);
  if (summaryBlock) console.log("Summary: added file-by-file excerpt to context.md.");
}

main();
