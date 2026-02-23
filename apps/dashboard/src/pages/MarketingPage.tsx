/**
 * Marketing Page - Campaigns & Leads
 * Purpose: Marketing domain (no overlap)
 */
import { useEffect, useState } from 'react';
import { TrendingUp, Mail, Target } from 'lucide-react';
import { PagePurpose } from '../components/PagePurpose';
import { getCampaigns, getLeads } from '../lib/api';
import type { DbCampaign, DbLead } from '../types';

export function MarketingPage() {
  const [campaigns, setCampaigns] = useState<DbCampaign[]>([]);
  const [leads, setLeads] = useState<DbLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'campaigns' | 'leads'>('campaigns');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [campaignsData, leadsData] = await Promise.all([
        getCampaigns(),
        getLeads()
      ]);
      // Handle both array and wrapped response
      const campaignsArray = Array.isArray(campaignsData) ? campaignsData : (campaignsData.campaigns || []);
      const leadsArray = Array.isArray(leadsData) ? leadsData : (leadsData.leads || []);
      setCampaigns(campaignsArray);
      setLeads(leadsArray);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load marketing data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PagePurpose
        purpose="Marketing domain."
        how="Campaigns and leads. View data, stats. Start marketing jobs from Roster or dedicated scripts."
        tip="Domain-specific surface — only if you use marketing agents."
      />
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Marketing</h2>
        </div>
        <p className="text-sm text-gray-500">
          Campaigns & leads. Marketing jobs are started from Engineering or marketing scripts. View data and stats here.
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Active Campaigns</div>
          <div className="text-2xl font-bold text-gray-900">{campaigns.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Total Leads</div>
          <div className="text-2xl font-bold text-blue-600">{leads.length}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-500">Conversion Rate</div>
          <div className="text-2xl font-bold text-green-600">—</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('campaigns')}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'campaigns'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Campaigns ({campaigns.length})
            </div>
          </button>
          <button
            onClick={() => setActiveTab('leads')}
            className={`px-4 py-2 border-b-2 font-medium transition-colors ${
              activeTab === 'leads'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Leads ({leads.length})
            </div>
          </button>
        </div>
      </div>

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div className="space-y-4">
          {campaigns.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
              <p className="text-gray-500">
                Marketing campaigns will appear here once they're created.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaigns.map((campaign) => (
                <div
                  key={campaign.id}
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-medium text-gray-900">{campaign.name}</h3>
                    {campaign.status && (
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          campaign.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : campaign.status === 'paused'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {campaign.status}
                      </span>
                    )}
                  </div>
                  {campaign.owner_name && (
                    <div className="text-sm text-gray-500 flex items-center gap-1">
                      {campaign.owner_emoji} {campaign.owner_name}
                    </div>
                  )}
                  <div className="mt-4 text-sm text-gray-600">
                    <div>ID: {campaign.id}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Leads Tab */}
      {activeTab === 'leads' && (
        <div className="space-y-4">
          {leads.length === 0 ? (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No leads yet</h3>
              <p className="text-gray-500">
                Leads from campaigns will appear here.
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                      Lead ID
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                      Source
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                      Assigned To
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900 font-mono">
                        {lead.id}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {lead.source || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {lead.status && (
                          <span
                            className={`px-2 py-1 text-xs rounded ${
                              lead.status === 'new'
                                ? 'bg-blue-100 text-blue-800'
                                : lead.status === 'contacted'
                                ? 'bg-yellow-100 text-yellow-800'
                                : lead.status === 'qualified'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {lead.status}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {lead.assigned_to_name ? (
                          <div className="flex items-center gap-1">
                            {lead.assigned_to_emoji} {lead.assigned_to_name}
                          </div>
                        ) : (
                          '—'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
