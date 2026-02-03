/**
 * Main Dashboard Page
 * Displays agent status, priorities, and logs for selected repository
 */
import { useState } from 'react';
import { Bot } from 'lucide-react';
import { RepoSelector } from '../components/RepoSelector';
import { AgentStatusCard } from '../components/AgentStatusCard';
import { PriorityBoard } from '../components/PriorityBoard';
import { LogViewer } from '../components/LogViewer';

export function DashboardPage() {
  const [selectedRepo, setSelectedRepo] = useState<string>('');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Agent Service</h1>
                <p className="text-sm text-gray-600">Monitor and control your automation agents</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <RepoSelector value={selectedRepo} onChange={setSelectedRepo} />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!selectedRepo ? (
          <div className="text-center py-12">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Repository Selected</h2>
            <p className="text-gray-600">
              Select a repository from the dropdown above to view its agent status
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Agent Status */}
            <AgentStatusCard repoName={selectedRepo} />

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Priorities */}
              <PriorityBoard repoName={selectedRepo} />

              {/* Logs */}
              <LogViewer repoName={selectedRepo} limit={50} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Agent Service v1.0.0 • Powered by Claude Code
          </p>
        </div>
      </footer>
    </div>
  );
}
