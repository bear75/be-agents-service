/**
 * Overview Page (/) — Quick start guide & workspace (when repo selected)
 */
import { Link, useOutletContext } from 'react-router-dom';
import { Bot, Rocket, Clock, Users, Map, Brain, TrendingUp, Terminal } from 'lucide-react';
import { PagePurpose } from '../components/PagePurpose';
import { WorkspaceOverview } from '../components/WorkspaceOverview';
import { InboxView } from '../components/InboxView';
import { CheckInTimeline } from '../components/CheckInTimeline';
import { PriorityBoard } from '../components/PriorityBoard';
import { MemoryViewer } from '../components/MemoryViewer';

export function DashboardPage() {
  const { selectedRepo = '' } = useOutletContext<{ selectedRepo?: string }>() ?? {};

  if (!selectedRepo) {
    return (
      <div className="space-y-8 max-w-3xl mx-auto">
        <div className="text-center py-8">
          <Bot className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Darwin Overview</h2>
          <p className="text-gray-600">
            Your agent automation hub. Get things done with compound, sessions, and tasks.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Quick Start — How to get things done</h3>
          <div className="space-y-4 text-sm">
            <div className="flex gap-4">
              <Rocket className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/run" className="font-medium text-blue-600 hover:underline">Run</Link>
                <p className="text-gray-600 mt-0.5">
                  Compound: start auto-compound (priority → PRD → PR). Control Tower: launch sessions. Nightly at 23:00 or start manually.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <Clock className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/work" className="font-medium text-blue-600 hover:underline">Work</Link>
                <p className="text-gray-600 mt-0.5">
                  Sessions and tasks in one view. Click a session to expand and see details.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <Users className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/roster" className="font-medium text-blue-600 hover:underline">Roster</Link>
                <p className="text-gray-600 mt-0.5">
                  Agents & teams. Hire, fire, configure who does what.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <Map className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/plans" className="font-medium text-blue-600 hover:underline">Plans</Link>
                <p className="text-gray-600 mt-0.5">
                  PRDs, roadmaps. Repo status and logs when repo selected.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <Brain className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/insights" className="font-medium text-blue-600 hover:underline">Insights</Link>
                <p className="text-gray-600 mt-0.5">
                  Analytics & leaderboard. Experiments, LLM usage, agent XP.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <TrendingUp className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/marketing" className="font-medium text-blue-600 hover:underline">Marketing</Link>
                <p className="text-gray-600 mt-0.5">
                  Campaigns & leads. Marketing jobs from Roster or dedicated scripts.
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <Terminal className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <Link to="/settings" className="font-medium text-blue-600 hover:underline">Settings</Link>
                <p className="text-gray-600 mt-0.5">
                  Config, integrations. Docs tab: commands, guides, API.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
          <p className="font-medium mb-1">Next step</p>
          <p>Select a repository from the dropdown above to view workspace (inbox, priorities, check-ins).</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {selectedRepo && (
        <PagePurpose
          purpose="Entry point & context."
          how="Workspace: inbox, priorities, check-ins, memory. Select a repo above."
          tip="Quick start links below when no repo."
        />
      )}
      <WorkspaceOverview repoName={selectedRepo} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <InboxView repoName={selectedRepo} />
        <CheckInTimeline repoName={selectedRepo} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PriorityBoard repoName={selectedRepo} />
        <MemoryViewer repoName={selectedRepo} />
      </div>
    </div>
  );
}
