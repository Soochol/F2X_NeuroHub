/**
 * Serial Search Component
 */

import { useState, type FormEvent, useRef, useEffect } from 'react';
import { Button } from '@/components/atoms';
import { Card } from '@/components/molecules';
import { QrCode, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { validateSerialNumber, detectSerialVersion } from '@/utils/serialNumber';

interface SerialSearchProps {
  onSearch: (serialNumber: string) => void;
  isLoading?: boolean;
  initialValue?: string;
}

export const SerialSearch = ({ onSearch, isLoading, initialValue = '' }: SerialSearchProps) => {
  const [serialNumber, setSerialNumber] = useState(initialValue);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    setSerialNumber(initialValue);
  }, [initialValue]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!serialNumber.trim()) {
      setError('Please enter a serial number');
      return;
    }
    setError('');
    onSearch(serialNumber.trim());
  };

  const isValid = serialNumber.trim() ? validateSerialNumber(serialNumber) : null;

  return (
    <Card>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label
              htmlFor="serialNumber"
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'var(--color-text-primary)'
              }}
            >
              Search Serial Number
            </label>
            <div style={{ position: 'relative' }}>
              <QrCode
                size={18}
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--color-text-secondary)'
                }}
              />
              <input
                ref={inputRef}
                id="serialNumber"
                type="text"
                value={serialNumber}
                onChange={(e) => {
                  setSerialNumber(e.target.value);
                  setError('');
                }}
                placeholder="e.g., KR01PSA2511001"
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '12px 12px 12px 40px',
                  border: error ? '1px solid var(--color-error)' : '1px solid var(--color-border)',
                  borderRadius: '6px',
                  fontSize: '15px',
                  backgroundColor: 'var(--color-bg-primary)',
                  color: 'var(--color-text-primary)',
                }}
              />
            </div>
            {/* Absolute positioned container to prevent layout shift */}
            <div style={{ position: 'relative' }}>
              {(isValid !== null || error) && (
                <div style={{
                  position: 'absolute',
                  top: '6px',
                  left: 0,
                  right: 0,
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  color: error ? 'var(--color-error)' : (isValid ? 'var(--color-success)' : 'var(--color-error)')
                }}>
                  {error ? (
                    <>
                      <AlertCircle size={14} />
                      {error}
                    </>
                  ) : isValid ? (
                    <>
                      <CheckCircle2 size={14} />
                      <span>
                        Valid {detectSerialVersion(serialNumber) === 1 ? 'V1' : 'V0'} format
                      </span>
                    </>
                  ) : (
                    <>
                      <XCircle size={14} />
                      <span>Invalid serial format</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
          <Button
            type="submit"
            disabled={isLoading || !serialNumber.trim()}
            size="lg"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </Button>
        </div>
      </form>
    </Card>
  );
};
