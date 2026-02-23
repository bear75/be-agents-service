/**
 * Renders markdown docs with human-readable formatting (prose styles).
 */
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Loader2 } from 'lucide-react';

interface DocViewerProps {
  path: string;
  label: string;
}

export function DocViewer({ path, label }: DocViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/file/docs?path=${encodeURIComponent(path)}`)
      .then((res) => {
        if (!res.ok) throw new Error(res.status === 404 ? 'Doc not found' : 'Failed to load');
        return res.text();
      })
      .then(setContent)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, [path]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-700">
        <p>{error}</p>
      </div>
    );
  }

  if (!content) return null;

  return (
    <article className="prose prose-gray prose-sm max-w-none bg-white text-gray-900 rounded-lg">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-200">
        <FileText className="w-5 h-5 text-gray-500" />
        <span className="font-medium text-gray-700">{label}</span>
      </div>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre: ({ children }) => (
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              {children}
            </pre>
          ),
          code: ({ className, children, ...props }) =>
            className ? (
              <code className={className} {...props}>
                {children}
              </code>
            ) : (
              <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-gray-200 rounded-lg">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-gray-200 bg-gray-50 px-3 py-2 text-left font-medium">
              {children}
            </th>
          ),
          td: ({ children }) => <td className="border border-gray-200 px-3 py-2">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </article>
  );
}
