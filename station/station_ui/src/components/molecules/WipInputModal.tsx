/**
 * WIP ID Input Modal
 *
 * Modal for entering WIP (Work-In-Progress) ID before starting a sequence.
 * Used when workflow is enabled to support 착공/완공 (process start/complete) integration.
 */

import { useState, useRef, useEffect } from 'react';
import { Barcode, Loader2, Play } from 'lucide-react';
import { Modal } from '../atoms/Modal';
import { Button } from '../atoms/Button';

interface WipInputModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (wipId: string) => void;
  isLoading?: boolean;
  batchName?: string;
  errorMessage?: string | null;
}

const LAST_WIP_ID_KEY = 'station-ui-last-wip-id';

export function WipInputModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  batchName,
  errorMessage,
}: WipInputModalProps) {
  const [wipId, setWipId] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Combine local and external errors
  const error = errorMessage || localError;

  // Load last WIP ID when modal opens
  useEffect(() => {
    if (isOpen) {
      const lastWipId = localStorage.getItem(LAST_WIP_ID_KEY);
      if (lastWipId) {
        setWipId(lastWipId);
      }
      // Focus and select all text for easy replacement
      if (inputRef.current) {
        inputRef.current.focus();
        inputRef.current.select();
      }
    }
  }, [isOpen]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setWipId('');
      setLocalError(null);
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    const trimmedWipId = wipId.trim();
    if (!trimmedWipId) {
      setLocalError('WIP ID is required');
      return;
    }

    // Save to localStorage for next time
    localStorage.setItem(LAST_WIP_ID_KEY, trimmedWipId);
    onSubmit(trimmedWipId);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Enter WIP ID"
      size="sm"
      showCloseButton={!isLoading}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Description */}
        <p
          className="text-sm"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          {batchName && (
            <span className="block mb-1">
              Starting sequence: <strong style={{ color: 'var(--color-text-primary)' }}>{batchName}</strong>
            </span>
          )}
          Scan or enter the WIP barcode to start the process.
        </p>

        {/* WIP ID Input */}
        <div>
          <div className="relative">
            <Barcode
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5"
              style={{ color: 'var(--color-text-tertiary)' }}
            />
            <input
              ref={inputRef}
              type="text"
              value={wipId}
              onChange={(e) => setWipId(e.target.value)}
              placeholder="Enter or scan WIP ID"
              disabled={isLoading}
              className="w-full pl-11 pr-4 py-3 text-sm rounded-lg border outline-none transition-colors disabled:opacity-50"
              style={{
                backgroundColor: 'var(--color-bg-primary)',
                borderColor: error ? 'var(--color-status-error)' : 'var(--color-border-default)',
                color: 'var(--color-text-primary)',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--color-brand-500)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = error ? 'var(--color-status-error)' : 'var(--color-border-default)';
              }}
            />
          </div>
          {error && (
            <p
              className="mt-1 text-xs"
              style={{ color: 'var(--color-status-error)' }}
            >
              {error}
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button
            type="button"
            variant="secondary"
            size="md"
            onClick={onClose}
            disabled={isLoading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Starting...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
