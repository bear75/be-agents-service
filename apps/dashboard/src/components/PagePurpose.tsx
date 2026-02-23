/**
 * PagePurpose - "How this page works" info block
 * Shows purpose and usage for each page (best practice: no overlap, clear purpose)
 */
import { Info } from 'lucide-react';

interface PagePurposeProps {
  /** One-line purpose statement */
  purpose: string;
  /** 1-3 sentences how to use this page */
  how: string;
  /** Optional quick tip */
  tip?: string;
}

export function PagePurpose({ purpose, how, tip }: PagePurposeProps) {
  return (
    <div className="rounded-lg bg-blue-50 border border-blue-100 p-4 text-sm">
      <div className="flex gap-3">
        <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-medium text-blue-900">{purpose}</p>
          <p className="text-blue-800 mt-1">{how}</p>
          {tip && (
            <p className="text-blue-700 mt-2 italic">{tip}</p>
          )}
        </div>
      </div>
    </div>
  );
}
