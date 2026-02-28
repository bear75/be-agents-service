/**
 * Shared layout with single nav - wraps all pages
 * Repo context defaults to "darwin" (shared workspace); no repo switcher in header.
 */
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  Bot,
  Layers,
  Clock,
  Users,
  Rocket,
  Map,
  Sliders,
  TrendingUp,
  Brain,
  BarChart2,
} from 'lucide-react';

const DEFAULT_REPO = 'darwin';

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: Layers, subtitle: 'Entry point & workspace' },
  { path: '/run', label: 'Run', icon: Rocket, subtitle: 'Launch automation' },
  { path: '/work', label: 'Work', icon: Clock, subtitle: 'Sessions & Kanban' },
  { path: '/roster', label: 'Roster', icon: Users, subtitle: 'Agents & teams' },
  { path: '/plans', label: 'Plans', icon: Map, subtitle: 'PRDs & roadmaps' },
  { path: '/insights', label: 'Insights', icon: Brain, subtitle: 'Analytics & leaderboard' },
  { path: '/schedules', label: 'Schedules', icon: BarChart2, subtitle: 'Schedule optimization pipeline' },
  { path: '/marketing', label: 'Marketing', icon: TrendingUp, subtitle: 'Campaigns & leads' },
  { path: '/settings', label: 'Settings', icon: Sliders, subtitle: 'Config & docs' },
];

export function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Darwin</h1>
                <p className="text-sm text-gray-600">Workspace & agent automation</p>
              </div>
            </div>
          </div>

          <nav className="flex flex-wrap gap-x-1 gap-y-2 mt-3 text-sm items-center">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                location.pathname === item.path || (item.path === '/' && location.pathname === '/');
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  title={item.subtitle}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>
                    {item.label}
                    {item.subtitle && <span className="hidden sm:inline text-gray-400 font-normal ml-1">· {item.subtitle}</span>}
                  </span>
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet context={{ selectedRepo: DEFAULT_REPO }} />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Darwin v1.0.0 • Powered by Claude Code
          </p>
        </div>
      </footer>
    </div>
  );
}
