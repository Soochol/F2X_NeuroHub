/**
 * Result Feedback Card
 *
 * 작업 결과 피드백 카드
 * 성공/실패 상태를 시각적으로 표시
 */
import { CheckCircle, XCircle, X, Play, Package } from 'lucide-react';
import { Card, Button } from '@/components/ui';
import { cn } from '@/lib/cn';

interface ResultFeedbackCardProps {
  wipId: string;
  action: 'start' | 'complete';
  success: boolean;
  message?: string;
  onDismiss: () => void;
  className?: string;
}

export const ResultFeedbackCard: React.FC<ResultFeedbackCardProps> = ({
  wipId,
  action,
  success,
  message,
  onDismiss,
  className,
}) => {
  const actionText = action === 'start' ? '착공' : '완공';

  const config = success
    ? {
        bgColor: action === 'start' ? 'bg-primary-50' : 'bg-success-50',
        borderColor: action === 'start' ? 'border-primary-200' : 'border-success-200',
        iconBg: action === 'start' ? 'bg-primary-500' : 'bg-success-500',
        textColor: action === 'start' ? 'text-primary-700' : 'text-success-700',
        icon: CheckCircle,
        statusText: '성공',
      }
    : {
        bgColor: 'bg-danger-50',
        borderColor: 'border-danger-200',
        iconBg: 'bg-danger-500',
        textColor: 'text-danger-700',
        icon: XCircle,
        statusText: '실패',
      };

  const Icon = config.icon;

  return (
    <Card
      className={cn(
        'border-2 overflow-hidden',
        config.bgColor,
        config.borderColor,
        // Animation
        'animate-slide-up',
        className
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div
          className={cn(
            'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
            config.iconBg
          )}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Status */}
          <div className="flex items-center gap-2">
            <span className={cn('font-bold text-lg', config.textColor)}>
              {actionText} {config.statusText}
            </span>
            {action === 'start' && success && (
              <Play className="w-4 h-4 text-primary-500" fill="currentColor" />
            )}
          </div>

          {/* WIP ID */}
          <div className="flex items-center gap-1.5 mt-1">
            <Package className="w-3.5 h-3.5 text-neutral-400" />
            <span className="text-sm text-neutral-600 font-mono truncate">
              {wipId}
            </span>
          </div>

          {/* Message */}
          {message && (
            <p className="text-xs text-neutral-500 mt-1 line-clamp-1">
              {message}
            </p>
          )}
        </div>

        {/* Dismiss Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onDismiss}
          className="flex-shrink-0 -mr-2 -mt-1"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      {/* Progress Bar Animation (for success) */}
      {success && (
        <div className="mt-3 -mx-4 -mb-4 h-1 bg-neutral-200 overflow-hidden">
          <div
            className={cn(
              'h-full',
              action === 'start' ? 'bg-primary-500' : 'bg-success-500',
              'animate-progress-bar'
            )}
          />
        </div>
      )}
    </Card>
  );
};
