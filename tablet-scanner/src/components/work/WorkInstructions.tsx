/**
 * Work Instructions
 *
 * 사용 방법 안내 카드 (접을 수 있음)
 */
import { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from '@/components/ui';
import { cn } from '@/lib/cn';

interface WorkInstructionsProps {
  className?: string;
  defaultExpanded?: boolean;
}

const INSTRUCTIONS = [
  { step: 1, text: '위에서 현재 작업 공정을 선택합니다' },
  { step: 2, text: '착공 버튼 → WIP QR 스캔 또는 직접 입력' },
  { step: 3, text: '착공 완료 후 완공 버튼이 활성화됩니다' },
  { step: 4, text: '완공 (합격/불량) 버튼으로 작업 완료' },
];

export const WorkInstructions: React.FC<WorkInstructionsProps> = ({
  className,
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* Header - Clickable */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          'w-full flex items-center justify-between',
          'py-3 px-4 -m-4',
          'text-left',
          'hover:bg-neutral-50 transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset'
        )}
      >
        <div className="flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-neutral-400" />
          <span className="text-sm font-medium text-neutral-600">사용 방법</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-neutral-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-neutral-400" />
        )}
      </button>

      {/* Content - Collapsible */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-200',
          isExpanded ? 'max-h-48 opacity-100 mt-4' : 'max-h-0 opacity-0'
        )}
      >
        <ol className="space-y-2">
          {INSTRUCTIONS.map(({ step, text }) => (
            <li key={step} className="flex items-start gap-3">
              <span
                className={cn(
                  'flex-shrink-0 w-5 h-5 rounded-full',
                  'bg-neutral-100 text-neutral-500',
                  'flex items-center justify-center',
                  'text-xs font-medium'
                )}
              >
                {step}
              </span>
              <span className="text-sm text-neutral-600">{text}</span>
            </li>
          ))}
        </ol>
      </div>
    </Card>
  );
};
