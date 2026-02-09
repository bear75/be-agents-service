/**
 * Setup Status Component
 * Shows readiness of workspace, OpenClaw, Telegram, and LaunchD
 */
import { useEffect, useState } from 'react';
import {
  Shield,
  CheckCircle,
  XCircle,
  FolderOpen,
  MessageCircle,
  Send,
  Timer,
  AlertCircle,
} from 'lucide-react';
import { getSetupStatus } from '../lib/api';
import type { SetupStatus as SetupStatusType } from '../types';

interface SetupStatusProps {
  repoName: string;
}

export function SetupStatus({ repoName }: SetupStatusProps) {
  const [status, setStatus] = useState<SetupStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStatus = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getSetupStatus(repoName);
        setStatus(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to check status');
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
  }, [repoName]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">Setup check failed</p>
        </div>
        <p className="text-sm text-gray-600">{error}</p>
      </div>
    );
  }

  const items: Array<{
    icon: React.ReactNode;
    label: string;
    ready: boolean;
    detail: string;
    action?: string;
  }> = [
    {
      icon: <FolderOpen className="w-4 h-4" />,
      label: 'Shared Workspace',
      ready: status.workspace.configured && status.workspace.exists,
      detail: status.workspace.exists
        ? `Active at ${status.workspace.path}`
        : status.workspace.configured
        ? `Configured but directory not found — run init-workspace.sh`
        : 'Not configured in repos.yaml',
      action: !status.workspace.exists
        ? './scripts/workspace/init-workspace.sh'
        : undefined,
    },
    {
      icon: <MessageCircle className="w-4 h-4" />,
      label: 'OpenClaw Bot',
      ready: status.openclaw.configured,
      detail: status.openclaw.configured
        ? 'Configured'
        : status.openclaw.configPath
        ? 'Template config found — update with your Telegram credentials'
        : 'Not installed — see config/openclaw/README.md',
      action: !status.openclaw.configured
        ? 'config/openclaw/README.md'
        : undefined,
    },
    {
      icon: <Send className="w-4 h-4" />,
      label: 'Telegram Notifications',
      ready: status.telegram.configured,
      detail: status.telegram.configured
        ? 'Bot token and chat ID configured'
        : 'Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in ~/.config/caire/env',
    },
    {
      icon: <Timer className="w-4 h-4" />,
      label: 'Morning Briefing (8 AM)',
      ready: status.launchd.morningBriefing,
      detail: status.launchd.morningBriefing
        ? 'LaunchD plist ready — load with launchctl'
        : 'Plist not found',
    },
    {
      icon: <Timer className="w-4 h-4" />,
      label: 'Weekly Review (Mon 8 AM)',
      ready: status.launchd.weeklyReview,
      detail: status.launchd.weeklyReview
        ? 'LaunchD plist ready — load with launchctl'
        : 'Plist not found',
    },
  ];

  const readyCount = items.filter((i) => i.ready).length;
  const totalCount = items.length;
  const allReady = readyCount === totalCount;

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Shield className={`w-5 h-5 ${allReady ? 'text-green-600' : 'text-amber-600'}`} />
            <h3 className="text-lg font-semibold text-gray-900">Setup Status</h3>
          </div>
          <span
            className={`text-xs font-medium px-2 py-1 rounded-full ${
              allReady
                ? 'bg-green-100 text-green-700'
                : 'bg-amber-100 text-amber-700'
            }`}
          >
            {readyCount}/{totalCount} ready
          </span>
        </div>

        <div className="space-y-2">
          {items.map((item, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 p-3 rounded-lg ${
                item.ready ? 'bg-green-50' : 'bg-amber-50'
              }`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {item.ready ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <XCircle className="w-4 h-4 text-amber-600" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  {item.icon}
                  <span className="text-sm font-medium text-gray-900">
                    {item.label}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{item.detail}</p>
                {item.action && (
                  <p className="text-xs text-amber-700 font-mono mt-1">
                    → {item.action}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {!allReady && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-500">
              Complete setup on your Mac mini to enable all features.
              See <span className="font-mono">docs/WORKSPACE.md</span> for the full guide.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
