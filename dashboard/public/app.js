/**
 * Multi-Agent Dashboard - Frontend Application
 */

const API_BASE = '';
const REFRESH_INTERVAL = 3000; // 3 seconds

let refreshTimer = null;
let currentSessionId = null;

/**
 * Initialize dashboard
 */
function init() {
  loadSystemStats();
  loadSessions();

  // Auto-refresh
  refreshTimer = setInterval(() => {
    loadSystemStats();
    loadSessions();

    // Refresh modal if open
    if (currentSessionId) {
      loadSessionDetails(currentSessionId);
    }
  }, REFRESH_INTERVAL);
}

/**
 * Load system statistics
 */
async function loadSystemStats() {
  try {
    const response = await fetch(`${API_BASE}/api/stats`);
    const stats = await response.json();

    document.getElementById('total-sessions').textContent = stats.total;
    document.getElementById('running-sessions').textContent = stats.running;
    document.getElementById('completed-sessions').textContent = stats.completed;
    document.getElementById('failed-sessions').textContent = stats.failed;
    document.getElementById('blocked-sessions').textContent = stats.blocked;

    updateLastUpdate();
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

/**
 * Load sessions list
 */
async function loadSessions() {
  try {
    const response = await fetch(`${API_BASE}/api/sessions`);
    const sessions = await response.json();

    const container = document.getElementById('sessions-list');

    if (sessions.length === 0) {
      container.innerHTML = '<div class="loading">No sessions found</div>';
      return;
    }

    container.innerHTML = sessions.map(session => renderSessionCard(session)).join('');
  } catch (error) {
    console.error('Error loading sessions:', error);
    document.getElementById('sessions-list').innerHTML = '<div class="loading">Error loading sessions</div>';
  }
}

/**
 * Render session card
 */
function renderSessionCard(session) {
  const orchestratorStatus = session.orchestrator?.status || 'unknown';
  const verificationStatus = session.verification?.status || '';
  const phase = session.orchestrator?.phase || '';
  const targetRepo = session.orchestrator?.targetRepo || '';
  const prUrl = session.orchestrator?.prUrl || '';

  // Determine card status class
  let statusClass = '';
  let statusText = orchestratorStatus;

  if (orchestratorStatus === 'in_progress' || phase) {
    statusClass = 'running';
    statusText = 'running';
  } else if (verificationStatus === 'blocked') {
    statusClass = 'blocked';
    statusText = 'blocked';
  } else if (orchestratorStatus === 'completed') {
    statusClass = 'completed';
    statusText = 'completed';
  } else if (orchestratorStatus === 'failed') {
    statusClass = 'failed';
    statusText = 'failed';
  }

  // Get agent statuses
  const agents = [];
  if (session.backend?.status) agents.push({ name: 'Backend', status: session.backend.status });
  if (session.frontend?.status) agents.push({ name: 'Frontend', status: session.frontend.status });
  if (session.infrastructure?.status) agents.push({ name: 'Infrastructure', status: session.infrastructure.status });
  if (session.verification?.status) agents.push({ name: 'Verification', status: session.verification.status });

  const repoName = targetRepo ? targetRepo.split('/').pop() : 'Unknown';
  const createdAt = new Date(session.createdAt).toLocaleString();

  return `
    <div class="session-card ${statusClass}" onclick="showSessionDetails('${session.sessionId}')">
      <div class="session-header">
        <div class="session-id">${session.sessionId}</div>
        <span class="session-status ${statusClass}">${statusText}</span>
      </div>
      <div class="session-info">
        <div>📁 Repository: <strong>${repoName}</strong></div>
        <div>🕐 Created: ${createdAt}</div>
        ${phase ? `<div>⚡ Phase: <strong>${phase}</strong></div>` : ''}
        ${prUrl ? `<div>🔗 PR: <a href="${prUrl}" target="_blank" onclick="event.stopPropagation()">View PR</a></div>` : ''}
      </div>
      ${agents.length > 0 ? `
        <div class="session-agents">
          ${agents.map(agent => `
            <span class="agent-badge ${agent.status}">${agent.name}: ${agent.status}</span>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;
}

/**
 * Show session details modal
 */
async function showSessionDetails(sessionId) {
  currentSessionId = sessionId;

  const modal = document.getElementById('session-modal');
  const title = document.getElementById('modal-title');
  const body = document.getElementById('modal-body');

  title.textContent = sessionId;
  body.innerHTML = '<div class="loading">Loading session details...</div>';

  modal.style.display = 'flex';

  loadSessionDetails(sessionId);
}

/**
 * Load session details
 */
async function loadSessionDetails(sessionId) {
  try {
    const [sessionResponse, logsResponse] = await Promise.all([
      fetch(`${API_BASE}/api/sessions/${sessionId}`),
      fetch(`${API_BASE}/api/logs/${sessionId}`)
    ]);

    const session = await sessionResponse.json();
    const logs = await logsResponse.json();

    const body = document.getElementById('modal-body');
    body.innerHTML = renderSessionDetails(session, logs);
  } catch (error) {
    console.error('Error loading session details:', error);
    document.getElementById('modal-body').innerHTML = '<div class="loading">Error loading session details</div>';
  }
}

/**
 * Render session details
 */
function renderSessionDetails(session, logs) {
  const agents = session.agents || {};

  let html = '';

  // Orchestrator section
  if (agents.orchestrator) {
    html += `
      <div class="agent-section">
        <h3>🎯 Orchestrator</h3>
        <div class="agent-details">
          ${renderAgentDetails(agents.orchestrator)}
        </div>
      </div>
    `;
  }

  // Backend section
  if (agents.backend) {
    html += `
      <div class="agent-section">
        <h3>⚙️ Backend Specialist</h3>
        <div class="agent-details">
          ${renderAgentDetails(agents.backend)}
        </div>
        ${logs.backend ? `<div class="log-content">${escapeHtml(logs.backend)}</div>` : ''}
      </div>
    `;
  }

  // Frontend section
  if (agents.frontend) {
    html += `
      <div class="agent-section">
        <h3>🎨 Frontend Specialist</h3>
        <div class="agent-details">
          ${renderAgentDetails(agents.frontend)}
        </div>
        ${logs.frontend ? `<div class="log-content">${escapeHtml(logs.frontend)}</div>` : ''}
      </div>
    `;
  }

  // Infrastructure section
  if (agents.infrastructure) {
    html += `
      <div class="agent-section">
        <h3>🏗️ Infrastructure Specialist</h3>
        <div class="agent-details">
          ${renderAgentDetails(agents.infrastructure)}
        </div>
        ${logs.infrastructure ? `<div class="log-content">${escapeHtml(logs.infrastructure)}</div>` : ''}
      </div>
    `;
  }

  // Verification section
  if (agents.verification) {
    html += `
      <div class="agent-section">
        <h3>✅ Verification Specialist</h3>
        <div class="agent-details">
          ${renderAgentDetails(agents.verification)}
          ${agents.verification.blockers && agents.verification.blockers.length > 0 ? `
            <div class="detail-row">
              <div class="detail-label">Blockers:</div>
              <div class="detail-value">
                ${agents.verification.blockers.map(b => b.message).join('<br>')}
              </div>
            </div>
          ` : ''}
        </div>
        ${logs.verification ? `<div class="log-content">${escapeHtml(logs.verification)}</div>` : ''}
      </div>
    `;
  }

  // Orchestrator logs
  if (logs.orchestrator) {
    html += `
      <div class="agent-section">
        <h3>📋 Orchestrator Logs</h3>
        <div class="log-content">${escapeHtml(logs.orchestrator)}</div>
      </div>
    `;
  }

  return html || '<div class="loading">No agent data available</div>';
}

/**
 * Render agent details
 */
function renderAgentDetails(agent) {
  let html = '';

  if (agent.status) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Status:</div>
        <div class="detail-value"><span class="agent-badge ${agent.status}">${agent.status}</span></div>
      </div>
    `;
  }

  if (agent.phase) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Phase:</div>
        <div class="detail-value">${agent.phase}</div>
      </div>
    `;
  }

  if (agent.startTime) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Started:</div>
        <div class="detail-value">${new Date(agent.startTime).toLocaleString()}</div>
      </div>
    `;
  }

  if (agent.endTime) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Ended:</div>
        <div class="detail-value">${new Date(agent.endTime).toLocaleString()}</div>
      </div>
    `;
  }

  if (agent.targetRepo) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Repository:</div>
        <div class="detail-value">${agent.targetRepo}</div>
      </div>
    `;
  }

  if (agent.prUrl) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Pull Request:</div>
        <div class="detail-value"><a href="${agent.prUrl}" target="_blank">${agent.prUrl}</a></div>
      </div>
    `;
  }

  if (agent.completedTasks && agent.completedTasks.length > 0) {
    html += `
      <div class="detail-row">
        <div class="detail-label">Completed Tasks:</div>
        <div class="detail-value">${agent.completedTasks.length} task(s)</div>
      </div>
    `;
  }

  return html;
}

/**
 * Close modal
 */
function closeModal() {
  document.getElementById('session-modal').style.display = 'none';
  currentSessionId = null;
}

/**
 * Update last update time
 */
function updateLastUpdate() {
  document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Close modal when clicking outside
window.onclick = function(event) {
  const modal = document.getElementById('session-modal');
  if (event.target === modal) {
    closeModal();
  }
};

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
