/**
 * WIP Input Modal
 *
 * WIP ID 입력 모달 - 스캔 또는 수동 입력
 * 태블릿 터치 최적화
 */
import { useState, useEffect, useRef } from 'react';
import { Camera, Keyboard, X, QrCode } from 'lucide-react';
import { Modal, Button, Input } from '@/components/ui';
import { cn } from '@/lib/cn';

type InputMode = 'start' | 'complete-pass' | 'complete-fail';

interface WipInputModalProps {
  isOpen: boolean;
  mode: InputMode | null;
  onClose: () => void;
  onManualSubmit: (wipId: string) => void;
  onScanClick: () => void;
  isLoading?: boolean;
}

const MODE_CONFIG = {
  start: {
    title: '착공',
    subtitle: 'WIP ID를 입력하거나 스캔하세요',
    color: 'primary',
    icon: QrCode,
  },
  'complete-pass': {
    title: '완공 (합격)',
    subtitle: '합격 처리할 WIP를 입력하세요',
    color: 'success',
    icon: QrCode,
  },
  'complete-fail': {
    title: '완공 (불량)',
    subtitle: '불량 처리할 WIP를 입력하세요',
    color: 'danger',
    icon: QrCode,
  },
} as const;

export const WipInputModal: React.FC<WipInputModalProps> = ({
  isOpen,
  mode,
  onClose,
  onManualSubmit,
  onScanClick,
  isLoading = false,
}) => {
  const [wipInput, setWipInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Reset and focus on open
  useEffect(() => {
    if (isOpen) {
      setWipInput('');
      // Focus after modal animation
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const config = mode ? MODE_CONFIG[mode] : null;

  const handleSubmit = () => {
    if (wipInput.trim()) {
      onManualSubmit(wipInput.trim());
      setWipInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && wipInput.trim()) {
      handleSubmit();
    }
  };

  if (!config) return null;

  const colorClasses = {
    primary: {
      bg: 'bg-primary-500',
      bgLight: 'bg-primary-50',
      border: 'border-primary-200',
      text: 'text-primary-600',
    },
    success: {
      bg: 'bg-success-500',
      bgLight: 'bg-success-50',
      border: 'border-success-200',
      text: 'text-success-600',
    },
    danger: {
      bg: 'bg-danger-500',
      bgLight: 'bg-danger-50',
      border: 'border-danger-200',
      text: 'text-danger-600',
    },
  }[config.color];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="" size="md">
      <div className="space-y-5">
        {/* Header */}
        <div className="text-center">
          <div
            className={cn(
              'w-14 h-14 rounded-2xl mx-auto mb-3',
              'flex items-center justify-center',
              colorClasses.bg
            )}
          >
            <config.icon className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-xl font-bold text-neutral-800">{config.title}</h2>
          <p className="text-sm text-neutral-500 mt-1">{config.subtitle}</p>
        </div>

        {/* Manual Input Section */}
        <div
          className={cn(
            'p-4 rounded-xl border-2',
            colorClasses.bgLight,
            colorClasses.border
          )}
        >
          <div className="flex items-center gap-2 mb-3">
            <Keyboard className={cn('w-4 h-4', colorClasses.text)} />
            <span className={cn('text-sm font-medium', colorClasses.text)}>
              직접 입력
            </span>
          </div>

          <div className="flex gap-2">
            <Input
              ref={inputRef}
              type="text"
              value={wipInput}
              onChange={(e) => setWipInput(e.target.value.toUpperCase())}
              onKeyDown={handleKeyDown}
              placeholder="WIP-XXXXXXXX-XXX"
              className="flex-1 font-mono text-base"
              disabled={isLoading}
            />
            <Button
              variant="primary"
              onClick={handleSubmit}
              disabled={!wipInput.trim() || isLoading}
              className="px-5"
            >
              확인
            </Button>
          </div>

          {/* Input Hint */}
          <p className="text-xs text-neutral-400 mt-2">
            예: WIP-KR02PSA251202-001
          </p>
        </div>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center">
            <span className="px-4 bg-white text-sm text-neutral-400">또는</span>
          </div>
        </div>

        {/* Camera Scan Button */}
        <button
          onClick={onScanClick}
          disabled={isLoading}
          className={cn(
            'w-full flex items-center justify-center gap-3',
            'py-4 px-6 rounded-xl',
            'border-2 border-dashed border-neutral-300',
            'bg-neutral-50 hover:bg-neutral-100',
            'text-neutral-700 font-medium',
            'transition-all duration-200',
            'active:scale-[0.98]',
            isLoading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <Camera className="w-5 h-5" />
          <span>카메라로 QR 스캔</span>
        </button>

        {/* Cancel Button */}
        <Button
          variant="ghost"
          onClick={onClose}
          className="w-full"
          disabled={isLoading}
        >
          <X className="w-4 h-4 mr-2" />
          취소
        </Button>
      </div>
    </Modal>
  );
};
