#!/usr/bin/env node
/**
 * OpenClaw MCP Bridge
 *
 * An MCP (Model Context Protocol) server that exposes the shared markdown
 * workspace as tools. OpenClaw (or any MCP client) connects via stdio
 * and can read/write inbox, priorities, tasks, check-ins, memory, and follow-ups.
 *
 * Usage:
 *   node dist/index.js                          # Uses WORKSPACE_CONFIG env var
 *   WORKSPACE_CONFIG=~/config/repos.yaml node dist/index.js
 *   WORKSPACE_REPO=beta-appcaire node dist/index.js
 *
 * Configuration:
 *   WORKSPACE_CONFIG - Path to repos.yaml (default: ../../config/repos.yaml)
 *   WORKSPACE_REPO   - Repo name to use (default: first enabled repo with workspace)
 *   WORKSPACE_PATH   - Direct path override (bypasses repos.yaml)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { registerWorkspaceTools } from './tools.js';
import { resolveWorkspacePath } from './workspace-bridge.js';

async function main() {
  const workspacePath = resolveWorkspacePath();

  if (!workspacePath) {
    console.error('Error: Could not resolve workspace path.');
    console.error('Set WORKSPACE_PATH, or WORKSPACE_CONFIG + WORKSPACE_REPO env vars.');
    process.exit(1);
  }

  console.error(`[openclaw-bridge] Workspace: ${workspacePath}`);

  const server = new McpServer({
    name: 'agent-workspace',
    version: '1.0.0',
  });

  // Register all workspace tools
  registerWorkspaceTools(server, workspacePath);

  // Connect via stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('[openclaw-bridge] MCP server running on stdio');
}

main().catch((error) => {
  console.error('[openclaw-bridge] Fatal error:', error);
  process.exit(1);
});
