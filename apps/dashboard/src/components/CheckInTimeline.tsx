/**
 * Check-in Timeline Component
 * Shows daily/weekly/monthly check-ins in a timeline view
 */
import { useEffect, useState } from 'react';
import { Calendar, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { getWorkspaceCheckIns } from '../lib/api';
import type { CheckIn } from '../types';

interface CheckInTimelineProps {
  repoName: string;
}

export function CheckInTimeline({ repoName }: CheckInTimelineProps) {
  const [checkIns, setCheckIns] = useState<CheckIn[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeType, setActiveType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    const loadCheckIns = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getWorkspaceCheckIns(repoName, activeType);
        setCheckIns(data);
        // Auto-expand the first one
        if (data.length > 0) {
          setExpandedId(data[0].date);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load check-ins');
      } finally {
        setLoading(false);
      }
    };

    loadCheckIns();
  }, [repoName, activeType]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
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

  const typeLabels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Check-ins</h3>
          </div>

          {/* Type tabs */}
          <div className="flex bg-gray-100 rounded-lg p-0.5">
            {(['daily', 'weekly', 'monthly'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setActiveType(type)}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  activeType === type
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {typeLabels[type]}
              </button>
            ))}
          </div>
        </div>

        {checkIns.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No {activeType} check-ins yet
          </p>
        ) : (
          <div className="space-y-2">
            {checkIns.map((checkIn) => {
              const isExpanded = expandedId === checkIn.date;

              return (
                <div
                  key={checkIn.date}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : checkIn.date)}
                    className="w-full flex items-center justify-between p-3 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-purple-400"></div>
                      <span className="text-sm font-medium text-gray-900">
                        {checkIn.date}
                      </span>
                      {/* Show first non-empty human section as preview */}
                      {!isExpanded && checkIn.sections['what happened today'] && (
                        <span className="text-xs text-gray-500 truncate max-w-[200px]">
                          {checkIn.sections['what happened today'].replace(/^[-*]\s*/gm, '').split('\n')[0]}
                        </span>
                      )}
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="border-t border-gray-200 p-4">
                      <div className="prose prose-sm max-w-none">
                        {/* Render sections */}
                        {Object.entries(checkIn.sections).map(([section, content]) => {
                          if (!content.trim()) return null;

                          const isAgentSection = section.toLowerCase().includes('agent');

                          return (
                            <div key={section} className="mb-3">
                              <h4 className={`text-xs font-semibold uppercase tracking-wide mb-1 ${
                                isAgentSection ? 'text-blue-600' : 'text-gray-500'
                              }`}>
                                {section}
                              </h4>
                              <div className={`text-sm whitespace-pre-wrap ${
                                isAgentSection
                                  ? 'text-blue-700 bg-blue-50 p-2 rounded'
                                  : 'text-gray-700'
                              }`}>
                                {content}
                              </div>
                            </div>
                          );
                        })}

                        {Object.keys(checkIn.sections).length === 0 && (
                          <p className="text-xs text-gray-400">
                            Empty check-in — fill it in!
                          </p>
                        )}
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
