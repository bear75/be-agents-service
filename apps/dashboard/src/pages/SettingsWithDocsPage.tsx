/**
 * Settings + Docs - Config & reference (no overlap)
 * Purpose: Setup & reference
 */
import { useState } from 'react';
import { Sliders, Terminal } from 'lucide-react';
import { PagePurpose } from '../components/PagePurpose';
import { SettingsPage } from './SettingsPage';
import { CommandsPage } from './CommandsPage';

const TABS = [
  { id: 'config', label: 'Config', icon: Sliders, desc: 'Integrations & setup' },
  { id: 'docs', label: 'Docs', icon: Terminal, desc: 'Commands & reference' },
] as const;

export function SettingsWithDocsPage() {
  const [activeTab, setActiveTab] = useState<'config' | 'docs'>('config');

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Setup & reference."
        how="Config: integrations, setup status. Docs: commands, guides, API. Everything to run and configure the service."
        tip="OpenClaw pattern: keep reference close to config."
      />
      <div className="border-b border-gray-200">
        <nav className="flex gap-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors -mb-px ${
                  isActive
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
      {activeTab === 'config' && <SettingsPage />}
      {activeTab === 'docs' && (
        <div className="pt-2">
          <CommandsPage />
        </div>
      )}
    </div>
  );
}
