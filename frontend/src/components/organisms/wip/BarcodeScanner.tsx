/**
 * Barcode Scanner Component
 *
 * Supports:
 * - USB/BLE barcode scanners (keyboard input capture)
 * - Manual input fallback
 * - Real-time validation
 * - Serial number formatting
 */

import { useState, useEffect, useRef, useCallback, type ChangeEvent, type KeyboardEvent } from 'react';
import { Input, Button } from '@/components/common';
import { validateSerialNumberV1, formatSerialNumberV1 } from '@/utils/serialNumber';

interface BarcodeScannerProps {
  onScan: (serialNumber: string) => void;
  isScanning?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export const BarcodeScanner: React.FC<BarcodeScannerProps> = ({
  onScan,
  isScanning = false,
  placeholder = 'Scan or enter serial number (14 chars)',
  autoFocus = true,
}) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const [scanBuffer, setScanBuffer] = useState('');
  const [lastKeyTime, setLastKeyTime] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Define handleScanComplete before useEffect that uses it
  const handleScanComplete = useCallback((serialNumber: string) => {
    const normalized = serialNumber.toUpperCase().trim();

    if (!validateSerialNumberV1(normalized)) {
      setError('Invalid serial number format. Expected 14 characters (e.g., KR01PSA2511001)');
      return;
    }

    setError('');
    setInput('');
    onScan(normalized);
  }, [onScan]);

  // Reset input when isScanning prop changes to false
  // This is intentional state sync with prop - not an anti-pattern
  /* eslint-disable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */
  useEffect(() => {
    if (!isScanning) {
      setInput('');
      setError('');
    }
  }, [isScanning]);
  /* eslint-enable react-hooks/set-state-in-effect, react-hooks/exhaustive-deps */

  // Auto-focus input on mount
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  // Handle barcode scanner input (rapid keystrokes)
  useEffect(() => {
    const handleKeyPress = (e: globalThis.KeyboardEvent) => {
      const currentTime = Date.now();
      const timeDiff = currentTime - lastKeyTime;

      // If keys are pressed rapidly (< 50ms apart), it's likely a scanner
      if (timeDiff < 50 && scanBuffer.length > 0) {
        const newBuffer = scanBuffer + e.key;
        setScanBuffer(newBuffer);

        // Check if buffer matches serial number length
        if (newBuffer.length === 14 && validateSerialNumberV1(newBuffer)) {
          handleScanComplete(newBuffer);
          setScanBuffer('');
        }
      } else {
        // Reset buffer if too slow (manual typing)
        setScanBuffer(e.key);
      }

      setLastKeyTime(currentTime);
    };

    // Only attach listener when not focused on input (scanner mode)
    if (document.activeElement !== inputRef.current) {
      window.addEventListener('keypress', handleKeyPress);
      return () => window.removeEventListener('keypress', handleKeyPress);
    }
  }, [scanBuffer, lastKeyTime, handleScanComplete]);

  const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    setInput(value);

    if (value.length > 0 && value.length < 14) {
      setError('Serial number must be 14 characters');
    } else if (value.length === 14 && !validateSerialNumberV1(value)) {
      setError('Invalid serial number format');
    } else {
      setError('');
    }
  }, []);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && input.length === 14) {
      e.preventDefault();
      handleScanComplete(input);
    }
  }, [input, handleScanComplete]);

  const handleManualSubmit = useCallback(() => {
    if (input.length === 14) {
      handleScanComplete(input);
    }
  }, [input, handleScanComplete]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-3)',
      }}
    >
      {/* Scanner Status Indicator */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
          padding: 'var(--spacing-3)',
          backgroundColor: isScanning ? 'var(--color-info-bg, rgba(52, 152, 219, 0.1))' : 'var(--color-bg-secondary)',
          borderRadius: 'var(--radius-base)',
          border: '1px solid var(--color-border-default)',
        }}
      >
        <div
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: isScanning ? 'var(--color-brand-400)' : 'var(--color-gray-500)',
            animation: isScanning ? 'pulse 2s infinite' : 'none',
          }}
        />
        <span style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
          {isScanning ? 'Processing...' : 'Ready to scan'}
        </span>
      </div>

      {/* Input Field */}
      <div style={{ display: 'flex', gap: 'var(--spacing-2)', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <Input
            ref={inputRef}
            label="Serial Number"
            type="text"
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            error={error}
            disabled={isScanning}
            maxLength={14}
            autoComplete="off"
            wrapperStyle={{ marginBottom: 0 }}
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '16px',
              letterSpacing: '0.5px',
            }}
          />
          {input.length === 14 && !error && (
            <div
              style={{
                marginTop: 'var(--spacing-1)',
                fontSize: '12px',
                color: 'var(--color-text-secondary)',
                fontFamily: 'var(--font-mono)',
              }}
            >
              Formatted: {formatSerialNumberV1(input)}
            </div>
          )}
        </div>
        <Button
          onClick={handleManualSubmit}
          disabled={isScanning || input.length !== 14 || !!error}
          style={{ marginTop: '26px' }}
        >
          Scan
        </Button>
      </div>

      {/* Instructions */}
      <div
        style={{
          fontSize: '13px',
          color: 'var(--color-text-secondary)',
          padding: 'var(--spacing-2)',
          backgroundColor: 'var(--color-bg-tertiary)',
          borderRadius: 'var(--radius-base)',
          border: '1px solid var(--color-border-subtle)',
        }}
      >
        <strong>Instructions:</strong>
        <ul style={{ marginTop: 'var(--spacing-1)', paddingLeft: 'var(--spacing-4)' }}>
          <li>Use barcode scanner to scan serial number automatically</li>
          <li>Or manually enter 14-character serial number (e.g., KR01PSA2511001)</li>
          <li>Press Enter or click Scan button to submit</li>
        </ul>
      </div>

      {/* Inline CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.3;
          }
        }
      `}</style>
    </div>
  );
};
