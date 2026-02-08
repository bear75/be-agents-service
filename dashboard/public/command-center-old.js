/**
 * PO Command Center - Unified Dashboard Controller
 */

const API_BASE = '';
const REFRESH_INTERVAL = 3000; // 3 seconds

let refreshTimer = null;
let currentSessionId = null;
let currentTab = 'sessions';
let currentSubtab = 'engineering';

/**
 * Initialize Command Center
 */
function init() {
  setupTabNavigation();
  setupSubtabNavigation();
  loadFromHash();

  // Initialize first tab
  initializeTab(currentTab);

  // Auto-refresh current tab only
  refreshTimer = setInterval(() => {
    refreshCurrentTab();
  }, REFRESH_INTERVAL);

  // Listen for hash changes
  window.addEventListener('hashchange', loadFromHash);
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
}

/**
 * Setup sub-tab navigation
 */
function setupSubtabNavigation() {
  const subtabButtons = document.querySelectorAll('.subtab-btn');
  subtabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const subtabName = btn.getAttribute('data-subtab');
      switchSubtab(subtabName);
    });
  });
}

/**
 * Switch tab
 */
function switchTab(tabName) {
  // Update active tab button
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    }
  });

  // Update active tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  document.getElementById(`tab-${tabName}`).classList.add('active');

  currentTab = tabName;
  window.location.hash = tabName;

  // Initialize tab if needed
  initializeTab(tabName);
}

/**
 * Switch sub-tab
 */
function switchSubtab(subtabName) {
  // Update active subtab button
  document.querySelectorAll('.subtab-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-subtab') === subtabName) {
      btn.classList.add('active');
    }
  });

  // Update active subtab content
  document.querySelectorAll('.subtab-content').forEach(content => {
    content.style.display = 'none';
  });
  document.getElementById(`subtab-${subtabName}`).style.display = 'block';

  currentSubtab = subtabName;
  window.location.hash = `data/${subtabName}`;

  // Load subtab data
  loadSubtabData(subtabName);
}

/**
 * Load from URL hash
 */
function loadFromHash() {
  const hash = window.location.hash.slice(1);

  if (hash.startsWith('data/')) {
    const subtab = hash.split('/')[1];
    switchTab('data');
    switchSubtab(subtab || 'engineering');
  } else if (hash) {
    switchTab(hash);
  }
}

/**
 * Initialize tab
 */
function initializeTab(tabName) {
  switch (tabName) {
    case 'sessions':
      loadSystemStats();
      loadSessions();
      break;
    case 'control-tower':
      loadControlTowerSessions();
      break;
    case 'data':
      loadSubtabData(currentSubtab);
      break;
  }
}

/**
 * Refresh current tab
 */
function refreshCurrentTab() {
  updateLastUpdate();

  switch (currentTab) {
    case 'sessions':
      loadSystemStats();
      loadSessions();
      break;
    case 'control-tower':
      if (currentSessionId) {
        refreshControlTower();
      }
      break;
    case 'data':
      loadSubtabData(currentSubtab);
      break;
  }
}

/**
 * Update last update time
 */
function updateLastUpdate() {
  document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

// =============================================================================
// SESSIONS TAB (from app.js)
// =============================================================================

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
  showEntity('session', sessionId);
}

// =============================================================================
// CONTROL TOWER TAB
// =============================================================================

/**
 * Load Control Tower sessions
 */
async function loadControlTowerSessions() {
  try {
    const response = await fetch('/api/sessions');
    const sessions = await response.json();

    const selector = document.getElementById('ct-session-selector');
    selector.innerHTML = '<option value="">-- Select Session --</option>';

    sessions.forEach(session => {
      const option = document.createElement('option');
      option.value = session.sessionId;
      option.textContent = `${session.sessionId} (${new Date(session.createdAt).toLocaleString()})`;
      selector.appendChild(option);
    });

    // Auto-select latest
    if (sessions.length > 0) {
      currentSessionId = sessions[0].sessionId;
      selector.value = currentSessionId;
      refreshControlTower();
    }
  } catch (error) {
    console.error('Error loading sessions:', error);
  }
}

/**
 * Load Control Tower session
 */
function loadControlTowerSession(sessionId) {
  currentSessionId = sessionId;
  refreshControlTower();
}

/**
 * Refresh Control Tower
 */
async function refreshControlTower() {
  if (!currentSessionId) return;

  try {
    const response = await fetch(`/api/sessions/${currentSessionId}`);
    const session = await response.json();

    // Update agents list
    const agentsList = document.getElementById('ct-agents-list');
    agentsList.innerHTML = '';

    Object.entries(session.agents || {}).forEach(([name, state]) => {
      const div = document.createElement('div');
      div.className = `agent-item ${state.status || 'idle'}`;
      div.style.cssText = 'background: rgba(248, 250, 252, 0.8); padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; border: 2px solid rgba(102, 126, 234, 0.1);';
      div.innerHTML = `
        <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">${name}</div>
        <div style="font-size: 12px; color: var(--text-secondary); font-weight: 500;">${state.status || 'idle'}</div>
      `;
      div.onclick = () => showEntity('agent', name, session);
      agentsList.appendChild(div);
    });

    // Parse tasks from session
    const tasks = extractTasks(session);

    // Render Kanban board
    const kanbanColumns = document.getElementById('kanban-columns');
    kanbanColumns.innerHTML = `
      ${renderKanbanColumn('Inbox', 'inbox', tasks.inbox)}
      ${renderKanbanColumn('Assigned', 'assigned', tasks.assigned)}
      ${renderKanbanColumn('In Progress', 'in-progress', tasks.inProgress)}
      ${renderKanbanColumn('Review', 'review', tasks.review)}
      ${renderKanbanColumn('Done', 'done', tasks.done)}
    `;
  } catch (error) {
    console.error('Error refreshing Control Tower:', error);
  }
}

/**
 * Extract tasks from session
 */
function extractTasks(session) {
  const tasks = {
    inbox: [],
    assigned: [],
    inProgress: [],
    review: [],
    done: []
  };

  Object.entries(session.agents || {}).forEach(([agentName, state]) => {
    // Completed tasks → Done
    (state.completedTasks || []).forEach(task => {
      tasks.done.push({
        ...task,
        agent: agentName,
        status: 'completed'
      });
    });

    // Current task → In Progress
    if (state.status === 'in_progress' && state.currentTask) {
      tasks.inProgress.push({
        ...state.currentTask,
        agent: agentName,
        status: 'in_progress'
      });
    }

    // Pending tasks → Assigned
    if (state.status === 'pending') {
      tasks.assigned.push({
        id: `${agentName}-pending`,
        description: `Waiting to start: ${agentName}`,
        agent: agentName,
        status: 'assigned'
      });
    }

    // Blockers → Review
    (state.blockers || []).forEach(blocker => {
      tasks.review.push({
        id: `blocker-${agentName}`,
        description: blocker.message || blocker,
        agent: agentName,
        status: 'blocked',
        priority: 'high'
      });
    });
  });

  return tasks;
}

/**
 * Render Kanban column
 */
function renderKanbanColumn(title, columnId, tasks) {
  const emoji = {
    'inbox': '📥',
    'assigned': '📌',
    'in-progress': '⚡',
    'review': '👀',
    'done': '✅'
  }[columnId] || '📋';

  return `
    <div style="background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border: 2px solid rgba(102, 126, 234, 0.15); border-radius: var(--border-radius); padding: 15px; min-height: 500px; box-shadow: var(--shadow-sm);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid rgba(102, 126, 234, 0.2);">
        <span style="font-weight: 700; color: var(--text-primary); font-size: 14px;">${emoji} ${title}</span>
        <span style="background: rgba(102, 126, 234, 0.15); color: var(--text-primary); padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 700;">${tasks.length}</span>
      </div>
      <div>
        ${tasks.length === 0 ? '<div style="text-align: center; color: var(--text-muted); padding: 40px 20px; font-size: 14px; font-weight: 500;">No tasks</div>' :
          tasks.map(task => renderTaskCard(task)).join('')}
      </div>
    </div>
  `;
}

/**
 * Render task card
 */
function renderTaskCard(task) {
  const priorityColor = {
    'high': 'var(--danger)',
    'medium': 'var(--warning)',
    'low': 'var(--success)'
  }[task.priority || 'medium'] || 'var(--warning)';

  return `
    <div class="task-card" onclick="showEntity('task', '${task.id || task.description}', ${JSON.stringify(task).replace(/"/g, '&quot;')})" style="background: #ffffff; border-radius: 10px; padding: 14px; margin-bottom: 12px; cursor: pointer; transition: all 0.3s; border-left: 4px solid ${priorityColor}; border: 2px solid rgba(102, 126, 234, 0.1); box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);">
      <div style="color: var(--text-primary); font-size: 14px; font-weight: 600; margin-bottom: 8px; line-height: 1.4;">${task.description || task.title || 'Untitled task'}</div>
      ${task.priority ? `<span style="display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-top: 4px; background: rgba(${task.priority === 'high' ? '239, 68, 68' : task.priority === 'low' ? '16, 185, 129' : '245, 158, 11'}, 0.2); color: ${task.priority === 'high' ? '#f87171' : task.priority === 'low' ? '#34d399' : '#fbbf24'};">${task.priority.toUpperCase()}</span>` : ''}
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
        <span style="background: rgba(102, 126, 234, 0.15); color: #667eea; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">${task.agent}</span>
        <span style="color: var(--text-muted); font-size: 11px; font-weight: 500;">${task.duration ? `${Math.floor(task.duration / 60)}m` : '-'}</span>
      </div>
    </div>
  `;
}

/**
 * Start nightly job
 */
async function startNightlyJob() {
  const result = confirm('Start nightly auto-compound job now?');
  if (!result) return;
  alert('Triggering: launchctl start com.appcaire.auto-compound');
}

// =============================================================================
// DATA TAB
// =============================================================================

/**
 * Load subtab data
 */
async function loadSubtabData(subtabName) {
  switch (subtabName) {
    case 'engineering':
      await loadEngineeringData();
      break;
    case 'marketing':
      await loadMarketingData();
      break;
    case 'documentation':
      await loadDocumentationData();
      break;
  }
}

/**
 * Load engineering data
 */
async function loadEngineeringData() {
  try {
    // Load all sessions and extract tasks, PRs, blockers
    const response = await fetch('/api/sessions');
    const sessions = await response.json();

    const tasks = [];
    const prs = [];
    const blockers = [];

    sessions.forEach(session => {
      // Extract tasks
      Object.entries(session.agents || {}).forEach(([agentName, state]) => {
        (state.completedTasks || []).forEach(task => {
          tasks.push({
            ...task,
            agent: agentName,
            sessionId: session.sessionId
          });
        });

        if (state.currentTask) {
          tasks.push({
            ...state.currentTask,
            agent: agentName,
            sessionId: session.sessionId
          });
        }
      });

      // Extract PRs
      if (session.orchestrator?.prUrl) {
        prs.push({
          url: session.orchestrator.prUrl,
          sessionId: session.sessionId,
          status: session.orchestrator.status,
          createdAt: session.createdAt
        });
      }

      // Extract blockers
      Object.entries(session.agents || {}).forEach(([agentName, state]) => {
        (state.blockers || []).forEach(blocker => {
          blockers.push({
            message: blocker.message || blocker,
            agent: agentName,
            sessionId: session.sessionId
          });
        });
      });
    });

    // Render grids
    document.getElementById('engineering-tasks').innerHTML = tasks.length === 0
      ? '<div class="loading">No tasks found</div>'
      : tasks.map(task => renderTaskEntity(task)).join('');

    document.getElementById('engineering-prs').innerHTML = prs.length === 0
      ? '<div class="loading">No PRs found</div>'
      : prs.map(pr => renderPREntity(pr)).join('');

    document.getElementById('engineering-blockers').innerHTML = blockers.length === 0
      ? '<div class="loading">No blockers found</div>'
      : blockers.map(blocker => renderBlockerEntity(blocker)).join('');
  } catch (error) {
    console.error('Error loading engineering data:', error);
  }
}

/**
 * Load marketing data
 */
async function loadMarketingData() {
  try {
    const [campaigns, leads, content, social] = await Promise.all([
      fetch('/api/data/campaigns').then(r => r.json()).catch(() => []),
      fetch('/api/data/leads').then(r => r.json()).catch(() => []),
      fetch('/api/data/content').then(r => r.json()).catch(() => []),
      fetch('/api/data/social').then(r => r.json()).catch(() => [])
    ]);

    document.getElementById('marketing-campaigns').innerHTML = campaigns.length === 0
      ? '<div class="loading">No campaigns found</div>'
      : campaigns.map(campaign => renderCampaignEntity(campaign)).join('');

    document.getElementById('marketing-leads').innerHTML = leads.length === 0
      ? '<div class="loading">No leads found</div>'
      : leads.map(lead => renderLeadEntity(lead)).join('');

    document.getElementById('marketing-content').innerHTML = content.length === 0
      ? '<div class="loading">No content found</div>'
      : content.map(item => renderContentEntity(item)).join('');

    document.getElementById('marketing-social').innerHTML = social.length === 0
      ? '<div class="loading">No social posts found</div>'
      : social.map(post => renderSocialEntity(post)).join('');
  } catch (error) {
    console.error('Error loading marketing data:', error);
  }
}

/**
 * Load documentation data
 */
async function loadDocumentationData() {
  // For now, show placeholder
  document.getElementById('docs-team').innerHTML = `
    <div class="loading">Documentation viewer coming soon</div>
  `;
}

// =============================================================================
// ENTITY RENDERERS
// =============================================================================

function renderTaskEntity(task) {
  return `
    <div class="entity-card task" onclick='showEntity("task", "${task.id || task.description}", ${JSON.stringify(task).replace(/'/g, "\\'")})'>
      <div class="entity-title">${task.description || task.title || 'Untitled Task'}</div>
      <div class="entity-meta">
        Agent: <strong>${task.agent}</strong><br>
        Session: <strong>${task.sessionId}</strong>
      </div>
    </div>
  `;
}

function renderPREntity(pr) {
  return `
    <div class="entity-card pr" onclick='showEntity("pr", "${pr.url}", ${JSON.stringify(pr).replace(/'/g, "\\'")})'>
      <div class="entity-title">Pull Request</div>
      <div class="entity-meta">
        Session: <strong>${pr.sessionId}</strong><br>
        Status: <strong>${pr.status}</strong><br>
        <a href="${pr.url}" target="_blank" onclick="event.stopPropagation()">View on GitHub</a>
      </div>
      <span class="entity-badge badge-active">${pr.status}</span>
    </div>
  `;
}

function renderBlockerEntity(blocker) {
  return `
    <div class="entity-card blocker" onclick='showEntity("blocker", "${blocker.message}", ${JSON.stringify(blocker).replace(/'/g, "\\'")})'>
      <div class="entity-title">⚠️ Blocker</div>
      <div class="entity-meta">
        ${blocker.message}<br>
        Agent: <strong>${blocker.agent}</strong><br>
        Session: <strong>${blocker.sessionId}</strong>
      </div>
    </div>
  `;
}

function renderCampaignEntity(campaign) {
  const statusClass = campaign.status === 'active' ? 'badge-active' : 'badge-draft';
  return `
    <div class="entity-card campaign" onclick='showEntity("campaign", "${campaign.id}", ${JSON.stringify(campaign).replace(/'/g, "\\'")})'>
      <div class="entity-title">${campaign.name}</div>
      <div class="entity-meta">
        Type: <strong>${campaign.type}</strong><br>
        Owner: <strong>${campaign.owner}</strong><br>
        Channels: ${campaign.channels.join(', ')}
      </div>
      <span class="entity-badge ${statusClass}">${campaign.status}</span>
    </div>
  `;
}

function renderLeadEntity(lead) {
  const statusClass = lead.status === 'qualified' ? 'badge-qualified' : 'badge-draft';
  return `
    <div class="entity-card lead" onclick='showEntity("lead", "${lead.id}", ${JSON.stringify(lead).replace(/'/g, "\\'")})'>
      <div class="entity-title">${lead.contactName || lead.company}</div>
      <div class="entity-meta">
        Company: <strong>${lead.company}</strong><br>
        Source: ${lead.source}<br>
        Score: <strong>${lead.score}</strong>
      </div>
      <span class="entity-badge ${statusClass}">${lead.status}</span>
    </div>
  `;
}

function renderContentEntity(content) {
  const statusClass = content.status === 'published' ? 'badge-published' : 'badge-draft';
  return `
    <div class="entity-card content" onclick='showEntity("content", "${content.id}", ${JSON.stringify(content).replace(/'/g, "\\'")})'>
      <div class="entity-title">${content.title}</div>
      <div class="entity-meta">
        Type: <strong>${content.type}</strong><br>
        Author: ${content.author}<br>
        Words: ${content.wordCount}
      </div>
      <span class="entity-badge ${statusClass}">${content.status}</span>
    </div>
  `;
}

function renderSocialEntity(post) {
  const statusClass = post.status === 'published' ? 'badge-published' : 'badge-draft';
  return `
    <div class="entity-card social" onclick='showEntity("social", "${post.id}", ${JSON.stringify(post).replace(/'/g, "\\'")})'>
      <div class="entity-title">${post.platform} Post</div>
      <div class="entity-meta">
        ${post.content.substring(0, 100)}...<br>
        Created by: ${post.createdBy}
      </div>
      <span class="entity-badge ${statusClass}">${post.status}</span>
    </div>
  `;
}

// =============================================================================
// UNIVERSAL MODAL SYSTEM
// =============================================================================

/**
 * Show entity modal
 */
async function showEntity(type, id, data = null) {
  const modal = document.getElementById('universal-modal');
  const title = document.getElementById('modal-title');
  const body = document.getElementById('modal-body');

  title.textContent = `${type.charAt(0).toUpperCase() + type.slice(1)} Details`;
  body.innerHTML = '<div class="loading">Loading...</div>';

  modal.style.display = 'flex';

  // If data is string, parse it
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data.replace(/&quot;/g, '"'));
    } catch (e) {
      console.error('Error parsing data:', e);
    }
  }

  try {
    let content = '';

    switch (type) {
      case 'session':
        content = await renderSessionModal(id);
        break;
      case 'agent':
        content = renderAgentModal(id, data);
        break;
      case 'task':
        content = renderTaskModal(data);
        break;
      case 'pr':
        content = renderPRModal(data);
        break;
      case 'blocker':
        content = renderBlockerModal(data);
        break;
      case 'campaign':
        content = renderCampaignModal(data);
        break;
      case 'lead':
        content = renderLeadModal(data);
        break;
      case 'content':
        content = renderContentModal(data);
        break;
      case 'social':
        content = renderSocialModal(data);
        break;
      default:
        content = '<div class="loading">Unknown entity type</div>';
    }

    body.innerHTML = content;
  } catch (error) {
    console.error('Error showing entity:', error);
    body.innerHTML = '<div class="loading">Error loading details</div>';
  }
}

/**
 * Render session modal
 */
async function renderSessionModal(sessionId) {
  try {
    const [sessionResponse, logsResponse] = await Promise.all([
      fetch(`${API_BASE}/api/sessions/${sessionId}`),
      fetch(`${API_BASE}/api/logs/${sessionId}`)
    ]);

    const session = await sessionResponse.json();
    const logs = await logsResponse.json();

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

    // Other agents
    ['backend', 'frontend', 'infrastructure', 'verification'].forEach(agentType => {
      if (agents[agentType]) {
        const emoji = { backend: '⚙️', frontend: '🎨', infrastructure: '🏗️', verification: '✅' }[agentType];
        html += `
          <div class="agent-section">
            <h3>${emoji} ${agentType.charAt(0).toUpperCase() + agentType.slice(1)}</h3>
            <div class="agent-details">
              ${renderAgentDetails(agents[agentType])}
            </div>
            ${logs[agentType] ? `<div class="log-content">${escapeHtml(logs[agentType])}</div>` : ''}
          </div>
        `;
      }
    });

    return html || '<div class="loading">No agent data available</div>';
  } catch (error) {
    console.error('Error rendering session modal:', error);
    return '<div class="loading">Error loading session details</div>';
  }
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

  return html;
}

function renderAgentModal(agentName, session) {
  const agent = session.agents[agentName] || {};
  return `
    <div class="agent-section">
      <h3>${agentName}</h3>
      <div class="agent-details">
        ${renderAgentDetails(agent)}
      </div>
    </div>
  `;
}

function renderTaskModal(task) {
  return `
    <div class="agent-section">
      <h3>Task Details</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Description:</div>
          <div class="detail-value">${task.description || task.title || 'N/A'}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Agent:</div>
          <div class="detail-value">${task.agent}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Session:</div>
          <div class="detail-value">${task.sessionId || 'N/A'}</div>
        </div>
        ${task.priority ? `
          <div class="detail-row">
            <div class="detail-label">Priority:</div>
            <div class="detail-value">${task.priority}</div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

function renderPRModal(pr) {
  return `
    <div class="agent-section">
      <h3>Pull Request</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">URL:</div>
          <div class="detail-value"><a href="${pr.url}" target="_blank">${pr.url}</a></div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Session:</div>
          <div class="detail-value">${pr.sessionId}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status:</div>
          <div class="detail-value">${pr.status}</div>
        </div>
      </div>
    </div>
  `;
}

function renderBlockerModal(blocker) {
  return `
    <div class="agent-section">
      <h3>⚠️ Blocker</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Message:</div>
          <div class="detail-value">${blocker.message}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Agent:</div>
          <div class="detail-value">${blocker.agent}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Session:</div>
          <div class="detail-value">${blocker.sessionId}</div>
        </div>
      </div>
    </div>
  `;
}

function renderCampaignModal(campaign) {
  return `
    <div class="agent-section">
      <h3>📢 Campaign Details</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Name:</div>
          <div class="detail-value">${campaign.name}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Type:</div>
          <div class="detail-value">${campaign.type}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status:</div>
          <div class="detail-value">${campaign.status}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Owner:</div>
          <div class="detail-value">${campaign.owner}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Channels:</div>
          <div class="detail-value">${campaign.channels.join(', ')}</div>
        </div>
        ${campaign.metrics ? `
          <div class="detail-row">
            <div class="detail-label">Metrics:</div>
            <div class="detail-value">
              Pageviews: ${campaign.metrics.pageviews || 0}<br>
              Leads: ${campaign.metrics.leads || 0}
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

function renderLeadModal(lead) {
  return `
    <div class="agent-section">
      <h3>👤 Lead Details</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Contact:</div>
          <div class="detail-value">${lead.contactName}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Company:</div>
          <div class="detail-value">${lead.company}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Email:</div>
          <div class="detail-value">${lead.email}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Source:</div>
          <div class="detail-value">${lead.source}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status:</div>
          <div class="detail-value">${lead.status}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Score:</div>
          <div class="detail-value">${lead.score}</div>
        </div>
      </div>
    </div>
  `;
}

function renderContentModal(content) {
  return `
    <div class="agent-section">
      <h3>📝 Content Details</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Title:</div>
          <div class="detail-value">${content.title}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Type:</div>
          <div class="detail-value">${content.type}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status:</div>
          <div class="detail-value">${content.status}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Author:</div>
          <div class="detail-value">${content.author}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Word Count:</div>
          <div class="detail-value">${content.wordCount}</div>
        </div>
        ${content.url ? `
          <div class="detail-row">
            <div class="detail-label">URL:</div>
            <div class="detail-value"><a href="${content.url}" target="_blank">${content.url}</a></div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

function renderSocialModal(post) {
  return `
    <div class="agent-section">
      <h3>🎸 Social Post Details</h3>
      <div class="agent-details">
        <div class="detail-row">
          <div class="detail-label">Platform:</div>
          <div class="detail-value">${post.platform}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Status:</div>
          <div class="detail-value">${post.status}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Created By:</div>
          <div class="detail-value">${post.createdBy}</div>
        </div>
        <div class="detail-row">
          <div class="detail-label">Content:</div>
          <div class="detail-value" style="white-space: pre-wrap;">${post.content}</div>
        </div>
        ${post.publishedAt ? `
          <div class="detail-row">
            <div class="detail-label">Published:</div>
            <div class="detail-value">${new Date(post.publishedAt).toLocaleString()}</div>
          </div>
        ` : ''}
        ${post.metrics ? `
          <div class="detail-row">
            <div class="detail-label">Metrics:</div>
            <div class="detail-value">
              Impressions: ${post.metrics.impressions || 0}<br>
              Clicks: ${post.metrics.clicks || 0}
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

/**
 * Close modal
 */
function closeModal() {
  document.getElementById('universal-modal').style.display = 'none';
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
  const modal = document.getElementById('universal-modal');
  if (event.target === modal) {
    closeModal();
  }
};

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
