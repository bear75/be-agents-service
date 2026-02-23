/**
 * Commands & Docs - formatted documentation viewer
 */
import { useState } from 'react';
import { Terminal } from 'lucide-react';
import { DocViewer } from '../components/DocViewer';

const DOC_LINKS = [
  { label: 'Docs Index', path: 'README.md' },
  { label: 'Quick Start', path: 'guides/quick-start.md' },
  { label: 'Quick Reference', path: 'QUICK_REFERENCE.md' },
  { label: 'Compound Setup', path: 'COMPOUND_SETUP_GUIDE.md' },
  { label: 'PO Workflow', path: 'guides/po-workflow.md' },
  { label: 'Engineering Guide', path: 'guides/engineering-guide.md' },
  { label: 'Marketing Guide', path: 'guides/marketing-guide.md' },
  { label: 'ESS-FSR Workflow', path: 'guides/ess-fsr-workflow.md' },
  { label: 'Architecture', path: 'ARCHITECTURE.md' },
  { label: 'Architecture (reference)', path: 'reference/architecture.md' },
  { label: 'Agents Reference', path: 'reference/agents.md' },
  { label: 'Workflow Reference', path: 'reference/workflow.md' },
  { label: 'API Reference', path: 'reference/api-reference.md' },
  { label: 'Priority Integration', path: 'reference/priority-integration.md' },
  { label: 'Data Flow', path: 'DATA_FLOW.md' },
  { label: 'Agents vs Human Docs', path: 'AGENT_VS_HUMAN_DOCS.md' },
];

export function CommandsPage() {
  const [selected, setSelected] = useState<typeof DOC_LINKS[0] | null>(
    () => DOC_LINKS.find((d) => d.path === 'QUICK_REFERENCE.md') ?? null
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Terminal className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Commands & Docs</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 p-4 sticky top-4">
            <p className="text-sm text-gray-600 mb-4">
              Click a doc to view it formatted below. From <code className="bg-gray-100 px-1 rounded">docs/</code>.
            </p>
            <div className="space-y-1 max-h-[60vh] overflow-y-auto">
              {DOC_LINKS.map((doc) => {
                const isActive = selected?.path === doc.path;
                return (
                  <button
                    key={doc.path}
                    type="button"
                    onClick={() => setSelected(doc)}
                    className={`w-full text-left px-3 py-2 rounded text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50 border border-transparent'
                    }`}
                  >
                    {doc.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-gray-200 p-6 min-h-[400px] overflow-y-auto max-h-[calc(100vh-12rem)]">
            {selected ? (
              <DocViewer path={selected.path} label={selected.label} />
            ) : (
              <p className="text-gray-500">Select a doc to view.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
