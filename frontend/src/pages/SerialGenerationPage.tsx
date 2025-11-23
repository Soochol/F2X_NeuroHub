/**
 * Serial Generation Page
 * Generate serials from WIP ID
 */

import { useState, useRef, useEffect } from 'react';
import { Card, Button } from '@/components/common';
import { serialsApi } from '@/api';
import { getErrorMessage, type Serial } from '@/types/api';
import { CheckCircle, QrCode, History, AlertCircle, Package } from 'lucide-react';
import { notify } from '@/utils/toast';

export const SerialGenerationPage = () => {
  const [wipId, setWipId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [lastGeneratedSerial, setLastGeneratedSerial] = useState<Serial | null>(null);
  const [printLabel, setPrintLabel] = useState(true);
  const [recentSerials, setRecentSerials] = useState<Serial[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [lastGeneratedSerial]);

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!wipId.trim()) {
      setError('Please enter a WIP ID');
      return;
    }

    setIsGenerating(true);
    setError('');
    setLastGeneratedSerial(null);

    try {
      const serial = await serialsApi.generateFromWip(wipId.trim(), printLabel);

      setLastGeneratedSerial(serial);
      setRecentSerials(prev => [serial, ...prev].slice(0, 10));
      setWipId('');

      notify.success({
        title: 'Serial Generated',
        description: `${serial.serial_number}`
      });
    } catch (err: unknown) {
      const errorMsg = getErrorMessage(err, 'Failed to generate serial');
      setError(errorMsg);
      notify.error({
        title: 'Generation Failed',
        description: errorMsg
      });
    } finally {
      setIsGenerating(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Fixed Header Section - Title and Input */}
      <div style={{
        flexShrink: 0,
        marginBottom: '20px',
        backgroundColor: 'var(--color-bg-secondary)',
        position: 'sticky',
        top: '-20px',
        zIndex: 10,
        paddingTop: '20px',
        paddingBottom: '20px',
        marginTop: '-20px',
        paddingLeft: '20px',
        paddingRight: '20px',
        marginLeft: '-20px',
        marginRight: '-20px',
        borderBottom: '2px solid var(--color-border)'
      }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
          Serial Generation
        </h1>

        <Card>
          <form onSubmit={handleGenerate}>
            <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <label
                  htmlFor="wipId"
                  style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'var(--color-text-primary)'
                  }}
                >
                  Scan WIP ID
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
                    id="wipId"
                    type="text"
                    value={wipId}
                    onChange={(e) => setWipId(e.target.value)}
                    placeholder="e.g., WIP-KR01PSA2511-001"
                    disabled={isGenerating}
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
                {error && (
                  <div style={{
                    marginTop: '6px',
                    color: 'var(--color-error)',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <AlertCircle size={14} />
                    {error}
                  </div>
                )}
              </div>
              <Button
                type="submit"
                disabled={isGenerating || !wipId.trim()}
                size="lg"
              >
                {isGenerating ? 'Generating...' : 'Generate Serial'}
              </Button>
            </div>

            <div
              style={{
                marginTop: '15px',
                padding: '12px',
                backgroundColor: 'var(--color-bg-tertiary)',
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '13px',
              }}
            >
              <input
                type="checkbox"
                id="printLabel"
                checked={printLabel}
                onChange={(e) => setPrintLabel(e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              <label htmlFor="printLabel" style={{ cursor: 'pointer', userSelect: 'none' }}>
                Auto-print label after generation
              </label>
            </div>
          </form>
        </Card>
      </div>

      {/* Scrollable Content Section - Results and History */}
      <div>
        {lastGeneratedSerial && !isGenerating && (
          <Card>
            <div style={{ textAlign: 'center', padding: '30px' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                backgroundColor: 'var(--color-success-bg)',
                marginBottom: '15px'
              }}>
                <CheckCircle size={32} style={{ color: 'var(--color-success)' }} />
              </div>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                Serial Number Generated
              </div>
              <div style={{
                fontSize: '24px',
                fontWeight: 'bold',
                fontFamily: 'var(--font-mono)',
                letterSpacing: '1px',
                color: 'var(--color-brand)',
                marginBottom: '15px'
              }}>
                {lastGeneratedSerial.serial_number}
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px',
                maxWidth: '400px',
                margin: '0 auto',
                fontSize: '13px',
                textAlign: 'left'
              }}>
                <div>
                  <span style={{ color: 'var(--color-text-secondary)' }}>LOT ID: </span>
                  <span style={{ fontWeight: '500' }}>{lastGeneratedSerial.lot_id}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-secondary)' }}>Sequence: </span>
                  <span style={{ fontWeight: '500' }}>{lastGeneratedSerial.sequence_in_lot}</span>
                </div>
              </div>
            </div>
          </Card>
        )}

        {recentSerials.length > 0 && (
          <Card style={{ marginTop: '20px' }} title={
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <History size={18} />
              <span>Recently Generated ({recentSerials.length})</span>
            </div>
          }>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recentSerials.map((serial, index) => (
                <div
                  key={serial.id}
                  style={{
                    padding: '12px',
                    backgroundColor: index === 0 ? 'var(--color-success-bg)' : 'var(--color-bg-tertiary)',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: '14px',
                    border: index === 0 ? '1px solid var(--color-success)' : 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Package size={16} style={{ color: 'var(--color-text-secondary)' }} />
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: index === 0 ? '600' : '500',
                      color: index === 0 ? 'var(--color-success)' : 'var(--color-text-primary)'
                    }}>
                      {serial.serial_number}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    Seq: {serial.sequence_in_lot}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {!lastGeneratedSerial && !isGenerating && recentSerials.length === 0 && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              <div style={{ marginBottom: '15px' }}>
                <QrCode size={48} />
              </div>
              <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                Ready to Generate Serial Numbers
              </div>
              <div style={{ fontSize: '14px' }}>
                Scan or enter a WIP ID to generate a serial number and optionally print a label.
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
