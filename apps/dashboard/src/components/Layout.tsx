/**
 * Shared layout with single nav - wraps all pages
 */
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  Bot,
  Layers,
  Clock,
  Users,
  Rocket,
  LayoutGrid,
  Map,
  Cpu,
  Sliders,
  TrendingUp,
  Brain,
  Target,
  Briefcase,
  Terminal,
} from 'lucide-react';
import { RepoSelector } from './RepoSelector';
import { useState } from 'react';

const NAV_ITEMS = [
  { path: '/', label: 'Workspace', icon: Layers },
  { path: '/sessions', label: 'Sessions', icon: Clock },
  { path: '/teams', label: 'Teams', icon: Target },
  { path: '/control', label: 'Control Tower', icon: Rocket },
  { path: '/kanban', label: 'Kanban', icon: LayoutGrid },
  { path: '/plans', label: 'Plans', icon: Map },
  { path: '/management', label: 'Management', icon: Briefcase },
  { path: '/marketing', label: 'Marketing', icon: TrendingUp },
  { path: '/engineering', label: 'Engineering', icon: Cpu },
  { path: '/agents', label: 'Agents', icon: Users },
  { path: '/rl', label: 'Analytics', icon: Brain },
  { path: '/commands', label: 'Docs', icon: Terminal },
  { path: '/settings', label: 'Settings', icon: Sliders },
];

export function Layout() {
  const location = useLocation();
  const [selectedRepo, setSelectedRepo] = useState('');

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Darwin</h1>
                <p className="text-sm text-gray-600">Workspace & agent automation</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <RepoSelector value={selectedRepo} onChange={setSelectedRepo} />
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
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet context={{ selectedRepo }} />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-600">
            Darwin v1.0.0 • Powered by Claude Code
          </p>
        </div>
      </footer>
    </div>
  );
}
