/**
 * Plans Board Component
 * Shows PRD documents with priority, status, limitations, and expandable content
 */
import { useEffect, useState } from 'react';
import {
  FileText,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Lock,
  BookOpen,
  AlertCircle,
} from 'lucide-react';
import { getPlans, getPlan } from '../lib/api';
import type { PlanDocument } from '../types';

export function PlansBoard() {
  const [plans, setPlans] = useState<PlanDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null);
  const [expandedContent, setExpandedContent] = useState<string | null>(null);
  const [contentLoading, setContentLoading] = useState(false);

  useEffect(() => {
    const loadPlans = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getPlans();
        setPlans(data.sort((a, b) => (a.priority || 99) - (b.priority || 99)));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load plans');
      } finally {
        setLoading(false);
      }
    };

    loadPlans();
  }, []);

  const handleExpand = async (slug: string) => {
    if (expandedSlug === slug) {
      setExpandedSlug(null);
      setExpandedContent(null);
      return;
    }

    setExpandedSlug(slug);
    setContentLoading(true);
    try {
      const plan = await getPlan(slug);
      setExpandedContent(plan.content || null);
    } catch {
      setExpandedContent('Failed to load document content.');
    } finally {
      setContentLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            <div className="h-24 bg-gray-200 rounded"></div>
            <div className="h-24 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600 mb-2">
          <AlertCircle className="w-5 h-5" />
          <p className="font-medium">Error</p>
        </div>
        <p className="text-sm text-gray-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-indigo-600" />
          <h3 className="text-lg font-semibold text-gray-900">Plans & PRDs</h3>
          <span className="text-xs text-gray-400 ml-auto">from docs/</span>
        </div>

        {plans.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No PRD documents found in docs/
          </p>
        ) : (
          <div className="space-y-3">
            {plans.map((plan) => {
              const isExpanded = expandedSlug === plan.slug;

              return (
                <div
                  key={plan.slug}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                >
                  {/* Plan Header */}
                  <button
                    onClick={() => handleExpand(plan.slug)}
                    className="w-full text-left p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      {/* Priority badge */}
                      <div className="flex-shrink-0">
                        {plan.priority && (
                          <span
                            className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold ${
                              plan.priority === 1
                                ? 'bg-red-100 text-red-700'
                                : plan.priority === 2
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}
                          >
                            P{plan.priority}
                          </span>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-semibold text-gray-900 truncate">
                            {plan.title}
                          </h4>
                          <StatusBadge status={plan.status} />
                        </div>

                        {plan.summary && (
                          <p className="text-xs text-gray-500 line-clamp-2 mb-2">
                            {plan.summary}
                          </p>
                        )}

                        {/* Limitations */}
                        {plan.limitations && plan.limitations.length > 0 && (
                          <div className="flex flex-wrap gap-1.5">
                            {plan.limitations.slice(0, 3).map((limitation, i) => (
                              <span
                                key={i}
                                className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200"
                              >
                                <AlertTriangle className="w-3 h-3" />
                                {limitation}
                              </span>
                            ))}
                            {plan.limitations.length > 3 && (
                              <span className="text-xs text-gray-400">
                                +{plan.limitations.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Expand icon */}
                      <div className="flex-shrink-0">
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </div>
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                      {contentLoading ? (
                        <div className="animate-pulse">
                          <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                        </div>
                      ) : expandedContent ? (
                        <div className="max-h-96 overflow-y-auto">
                          <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                            {expandedContent}
                          </pre>
                        </div>
                      ) : (
                        <p className="text-xs text-gray-400">No content available</p>
                      )}
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-200">
                        <BookOpen className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-400">
                          {plan.filename} · Last modified:{' '}
                          {new Date(plan.lastModified).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Status Badge ───────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: PlanDocument['status'] }) {
  const config: Record<
    string,
    { icon: React.ReactNode; label: string; className: string }
  > = {
    planning: {
      icon: <Clock className="w-3 h-3" />,
      label: 'Planning',
      className: 'bg-gray-100 text-gray-600',
    },
    'in-progress': {
      icon: <Clock className="w-3 h-3" />,
      label: 'In Progress',
      className: 'bg-blue-100 text-blue-700',
    },
    blocked: {
      icon: <Lock className="w-3 h-3" />,
      label: 'Blocked',
      className: 'bg-red-100 text-red-700',
    },
    done: {
      icon: <CheckCircle className="w-3 h-3" />,
      label: 'Done',
      className: 'bg-green-100 text-green-700',
    },
    'docs-only': {
      icon: <FileText className="w-3 h-3" />,
      label: 'Docs Only',
      className: 'bg-purple-100 text-purple-700',
    },
  };

  const c = config[status] || config.planning;

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${c.className}`}
    >
      {c.icon}
      {c.label}
    </span>
  );
}
