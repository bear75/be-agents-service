#!/usr/bin/env node
/**
 * Convert memory/*.md to machine-readable memory/*.json.
 * Reads context.md, decisions.md, learnings.md and writes context.json, decisions.json, learnings.json.
 * Idempotent; only overwrites .json files. See docs/DARWIN_MEMORY_SCHEMA.md.
 *
 * Usage: node memory-to-structured.js [workspace-path]
 *   workspace-path defaults to env DARWIN_WORKSPACE_PATH or config (darwin) workspace path.
 */

const fs = require("fs");
const path = require("path");

function getWorkspacePath() {
  const arg = process.argv[2];
  if (arg) return path.resolve(arg);
  if (process.env.DARWIN_WORKSPACE_PATH) return path.resolve(process.env.DARWIN_WORKSPACE_PATH);
  // Resolve from be-agents-service config/repos.yaml for "darwin"
  const serviceRoot = path.resolve(__dirname, "../..");
  const configPath = path.join(serviceRoot, "config/repos.yaml");
  if (!fs.existsSync(configPath)) return null;
  const yaml = fs.readFileSync(configPath, "utf8");
  const match = yaml.match(/darwin:[\s\S]*?path:\s*([^\s#]+)/);
  if (!match) return null;
  let p = match[1].trim().replace(/^["']|["']$/g, "");
  if (p.startsWith("~")) p = path.join(process.env.HOME || "", p.slice(1));
  return path.resolve(p);
}

function sectionContent(md, title) {
  const re = new RegExp(`##\\s+${title}\\s*\\n([\\s\\S]*?)(?=\\n##\\s|$)`, "i");
  const m = md.match(re);
  return m ? m[1].replace(/\s*<!--[\s\S]*?-->\s*/g, "").trim() : "";
}

function parseContext(md) {
  const project = sectionContent(md, "What is this project?");
  const focus = sectionContent(md, "Current focus");
  const constraintsRaw = sectionContent(md, "Key constraints");
  const constraints = constraintsRaw
    ? constraintsRaw.split(/\n/).map((s) => s.replace(/^[-*]\s*/, "").trim()).filter(Boolean)
    : [];
  const team = sectionContent(md, "Team & roles");
  const linksRaw = sectionContent(md, "Important links");
  const links = [];
  const linkRe = /[-*]\s*\[([^\]]+)\]\(([^)]+)\)/g;
  let m;
  while ((m = linkRe.exec(linksRaw)) !== null) links.push({ label: m[1], url: m[2] });
  if (links.length === 0 && linksRaw.trim()) links.push({ label: "Links", url: linksRaw.trim() });

  return {
    version: 1,
    updated: new Date().toISOString().slice(0, 19) + "Z",
    project: project || "",
    focus: focus || "",
    constraints,
    team: team || "",
    links,
  };
}

function parseDecisions(md) {
  const decisions = [];
  const blockRe = /##\s*(\d{4}-\d{2}-\d{2})\s*:\s*([^\n]+)\n([\s\S]*?)(?=\n##\s*\d{4}|$)/g;
  let i = 0;
  let block;
  while ((block = blockRe.exec(md)) !== null) {
    const [, date, title, body] = block;
    const context = (body.match(/\*\*Context:\*\*\s*([\s\S]*?)(?=\n\*\*|\n\n|$)/i) || [])[1]?.trim() || "";
    const decision = (body.match(/\*\*Decision:\*\*\s*([\s\S]*?)(?=\n\*\*|\n\n|$)/i) || [])[1]?.trim() || "";
    const consequences = (body.match(/\*\*Consequences:\*\*\s*([\s\S]*?)(?=\n\*\*|\n\n|$)/i) || [])[1]?.trim() || "";
    decisions.push({
      id: `dec-${++i}`,
      date,
      title: title.trim(),
      context,
      decision,
      consequences,
    });
  }
  return { version: 1, updated: new Date().toISOString().slice(0, 19) + "Z", decisions };
}

function parseLearnings(md) {
  const learnings = [];
  const lines = md.split(/\n/);
  let i = 0;
  let current = null;
  for (const line of lines) {
    const bullet = line.match(/^[-*]\s+(.+)$/);
    const tagsMatch = line.match(/\(tags:\s*([^)]+)\)/);
    const tags = tagsMatch ? tagsMatch[1].split(",").map((t) => t.trim()) : [];
    const summary = (tagsMatch ? line.replace(/\s*\(tags:\s*[^)]+\)\s*$/, "").trim() : line).replace(/^[-*]\s+/, "");
    if (bullet && summary) {
      current = {
        id: `learn-${++i}`,
        date: new Date().toISOString().slice(0, 10),
        summary: summary.trim(),
        detail: "",
        tags,
      };
      learnings.push(current);
    } else if (current && line.trim() && !line.match(/^#/)) {
      current.detail = (current.detail ? current.detail + "\n" : "") + line.trim();
    }
  }
  return { version: 1, updated: new Date().toISOString().slice(0, 19) + "Z", learnings };
}

function main() {
  const workspacePath = getWorkspacePath();
  if (!workspacePath || !fs.existsSync(workspacePath)) {
    console.error("Darwin workspace path not found. Set DARWIN_WORKSPACE_PATH or pass path as first argument.");
    process.exit(1);
  }
  let memoryDir = path.join(workspacePath, "my", "memory");
  if (!fs.existsSync(memoryDir)) {
    memoryDir = path.join(workspacePath, "memory");
  }
  if (!fs.existsSync(memoryDir)) {
    console.error("my/memory/ or memory/ not found");
    process.exit(1);
  }

  const contextPath = path.join(memoryDir, "context.md");
  const decisionsPath = path.join(memoryDir, "decisions.md");
  const learningsPath = path.join(memoryDir, "learnings.md");

  if (fs.existsSync(contextPath)) {
    const md = fs.readFileSync(contextPath, "utf8");
    const out = parseContext(md);
    fs.writeFileSync(path.join(memoryDir, "context.json"), JSON.stringify(out, null, 2));
    console.log("Wrote my/memory/context.json");
  }
  if (fs.existsSync(decisionsPath)) {
    const md = fs.readFileSync(decisionsPath, "utf8");
    const out = parseDecisions(md);
    fs.writeFileSync(path.join(memoryDir, "decisions.json"), JSON.stringify(out, null, 2));
    console.log("Wrote my/memory/decisions.json");
  }
  if (fs.existsSync(learningsPath)) {
    const md = fs.readFileSync(learningsPath, "utf8");
    const out = parseLearnings(md);
    fs.writeFileSync(path.join(memoryDir, "learnings.json"), JSON.stringify(out, null, 2));
    console.log("Wrote my/memory/learnings.json");
  }
}

main();
