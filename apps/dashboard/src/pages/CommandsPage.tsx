/**
 * Commands & Docs - links to documentation
 */
import { Terminal, ExternalLink } from 'lucide-react';

const DOC_LINKS = [
  { label: 'Quick Start', path: 'guides/quick-start.md' },
  { label: 'PO Workflow', path: 'guides/po-workflow.md' },
  { label: 'Engineering Guide', path: 'guides/engineering-guide.md' },
  { label: 'Marketing Guide', path: 'guides/marketing-guide.md' },
  { label: 'ESS-FSR Workflow', path: 'guides/ess-fsr-workflow.md' },
  { label: 'Architecture', path: 'ARCHITECTURE.md' },
  { label: 'Data Flow', path: 'DATA_FLOW.md' },
  { label: 'Compound Setup', path: 'COMPOUND_SETUP_GUIDE.md' },
];

export function CommandsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Terminal className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Commands & Docs</h2>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <p className="text-gray-600 mb-6">
          Documentation for the agent service. These files live in the <code className="bg-gray-100 px-1 rounded">docs/</code> directory.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DOC_LINKS.map((doc) => (
            <a
              key={doc.path}
              href={`/api/file/docs?path=${encodeURIComponent(doc.path)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-200 transition-colors"
            >
              <span className="font-medium text-gray-900">{doc.label}</span>
              <ExternalLink className="w-4 h-4 text-gray-400" />
            </a>
          ))}
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-medium text-gray-900 mb-2">Common Commands</h3>
        <pre className="text-sm font-mono text-gray-700 overflow-x-auto">
{`# Check status
./scripts/compound/check-status.sh beta-appcaire

# Trigger compound
./scripts/compound/auto-compound.sh beta-appcaire

# Trigger review
./scripts/compound/daily-compound-review.sh beta-appcaire`}
        </pre>
      </div>
    </div>
  );
}
