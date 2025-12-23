/**
 * Action Buttons Component
 *
 * Start/Complete buttons with result selection
 * Modern styling with Lucide icons
 */
import { useState } from 'react';
import { Play, CheckCircle, X, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui';
import { cn } from '@/lib/cn';
import type { ProcessResult } from '@/types';

interface ActionButtonsProps {
  canStart: boolean;
  canComplete: boolean;
  isLoading: boolean;
  onStart: () => void;
  onComplete: (result: ProcessResult, notes?: string) => void;
  disabled?: boolean;
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  canStart,
  canComplete,
  isLoading,
  onStart,
  onComplete,
  disabled = false,
}) => {
  const [showCompleteOptions, setShowCompleteOptions] = useState(false);

  const handleComplete = (result: ProcessResult) => {
    onComplete(result);
    setShowCompleteOptions(false);
  };

  // Show result selection UI
  if (showCompleteOptions) {
    return (
      <div className="w-full space-y-3">
        {/* Result selection header */}
        <div className="text-sm text-neutral-600 font-medium">
          검사 결과를 선택하세요
        </div>

        {/* Pass/Fail buttons */}
        <div className="flex gap-3">
          <Button
            variant="success"
            size="lg"
            fullWidth
            isLoading={isLoading}
            disabled={disabled}
            onClick={() => handleComplete('PASS')}
            leftIcon={<ThumbsUp className="w-5 h-5" />}
          >
            합격 (PASS)
          </Button>
          <Button
            variant="danger"
            size="lg"
            fullWidth
            isLoading={isLoading}
            disabled={disabled}
            onClick={() => handleComplete('FAIL')}
            leftIcon={<ThumbsDown className="w-5 h-5" />}
          >
            불량 (FAIL)
          </Button>
        </div>

        {/* Cancel button */}
        <Button
          variant="ghost"
          size="md"
          fullWidth
          onClick={() => setShowCompleteOptions(false)}
          leftIcon={<X className="w-4 h-4" />}
        >
          취소
        </Button>
      </div>
    );
  }

  // Default view - Start/Complete buttons
  return (
    <div className="flex gap-3 w-full">
      {/* Start button */}
      <Button
        variant="primary"
        size="lg"
        fullWidth
        isLoading={isLoading}
        disabled={!canStart || disabled}
        onClick={onStart}
        leftIcon={<Play className="w-5 h-5" />}
        className={cn(
          !canStart && 'opacity-50 cursor-not-allowed'
        )}
      >
        착공
      </Button>

      {/* Complete button */}
      <Button
        variant="success"
        size="lg"
        fullWidth
        disabled={!canComplete || disabled}
        onClick={() => setShowCompleteOptions(true)}
        leftIcon={<CheckCircle className="w-5 h-5" />}
        className={cn(
          !canComplete && 'opacity-50 cursor-not-allowed'
        )}
      >
        완공
      </Button>
    </div>
  );
};
