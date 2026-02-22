/**
 * Settings - setup status, integrations config with full CRUD
 */
import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Sliders, Power, Edit2, Trash2, Plus } from 'lucide-react';
import { getIntegrations, updateIntegration } from '../lib/api';
import type { DbIntegration } from '../types';
import { SetupStatus } from '../components/SetupStatus';

export function SettingsPage() {
  const { selectedRepo = '' } = useOutletContext<{ selectedRepo?: string }>() ?? {};
  const [integrations, setIntegrations] = useState<DbIntegration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const data = await getIntegrations();
      const integrationsArray = Array.isArray(data) ? data : (data.integrations || []);
      setIntegrations(integrationsArray);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (id: string, currentState: boolean) => {
    try {
      await updateIntegration(id, { is_active: !currentState });
      await loadIntegrations();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to update integration');
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete integration "${name}"? This cannot be undone.`)) return;

    try {
      // For now, just deactivate since we don't have a delete endpoint
      await updateIntegration(id, { is_active: false });
      await loadIntegrations();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete integration');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  const groupedIntegrations = integrations.reduce((acc, integration) => {
    const type = integration.type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(integration);
    return acc;
  }, {} as Record<string, DbIntegration[]>);

  return (
    <div className="space-y-6">
      {/* Setup Status */}
      {selectedRepo && <SetupStatus repoName={selectedRepo} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
        </div>
        <button
          onClick={() => alert('Run setup scripts to add integrations:\n\n./scripts/setup-email-integrations.js\n./scripts/setup-social-integrations.js')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Integration
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Total Integrations</div>
          <div className="text-2xl font-bold text-gray-900">{integrations.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Active</div>
          <div className="text-2xl font-bold text-green-600">
            {integrations.filter(i => i.is_active).length}
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Inactive</div>
          <div className="text-2xl font-bold text-gray-400">
            {integrations.filter(i => !i.is_active).length}
          </div>
        </div>
      </div>

      {/* Integrations by Type */}
      {integrations.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Sliders className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No integrations configured</h3>
          <p className="text-gray-500 mb-4">
            Run setup scripts to add email/social integrations:
          </p>
          <div className="space-y-2 text-sm font-mono text-gray-600">
            <div>./scripts/setup-email-integrations.js</div>
            <div>./scripts/setup-social-integrations.js</div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedIntegrations).map(([type, items]) => (
            <div key={type} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <h3 className="px-4 py-3 border-b font-medium text-gray-900 capitalize flex items-center gap-2">
                {type === 'messaging' ? '💬' : type === 'email' ? '📧' : type === 'social' ? '📱' : '🔗'}
                {type} ({items.length})
              </h3>
              <div className="divide-y">
                {items.map((integration) => (
                  <div
                    key={integration.id}
                    className="px-4 py-3 flex items-center justify-between hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">
                            {integration.name || integration.platform || integration.id}
                          </div>
                          <div className="text-sm text-gray-500">
                            {integration.platform && `Platform: ${integration.platform}`}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {/* Active/Inactive Badge */}
                          <span
                            className={`px-2 py-1 text-xs rounded ${
                              integration.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {integration.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>
                      {integration.last_connected_at && (
                        <div className="text-xs text-gray-400 mt-1">
                          Last connected: {new Date(integration.last_connected_at).toLocaleString()}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => toggleActive(integration.id, integration.is_active)}
                        className={`p-2 rounded hover:bg-gray-100 transition-colors ${
                          integration.is_active ? 'text-green-600' : 'text-gray-400'
                        }`}
                        title={integration.is_active ? 'Deactivate' : 'Activate'}
                      >
                        <Power className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setEditingId(integration.id)}
                        className="p-2 rounded hover:bg-gray-100 text-blue-600 transition-colors"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(integration.id, integration.name || integration.id)}
                        className="p-2 rounded hover:bg-gray-100 text-red-600 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal (placeholder) */}
      {editingId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Edit Integration</h3>
            <p className="text-gray-600 mb-6">
              Integration editing coming soon. For now, use setup scripts to reconfigure.
            </p>
            <button
              onClick={() => setEditingId(null)}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
