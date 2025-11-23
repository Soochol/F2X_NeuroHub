/**
 * Serial Tracking Page
 */

import { useState } from 'react';
import { SerialSearch, SerialTraceView } from '@/components/serials';
import { Card } from '@/components/common';
import { serialsApi } from '@/api';
import type { SerialTrace } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { Search, XCircle } from 'lucide-react';

export const SerialsPage = () => {
  const [trace, setTrace] = useState<SerialTrace | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (serialNumber: string) => {
    setIsLoading(true);
    setError('');
    setTrace(null);

    try {
      const data = await serialsApi.getTrace(serialNumber);
      setTrace(data);
    } catch (err: unknown) {
      setError(getErrorMessage(err, `Serial number "${serialNumber}" not found`));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Fixed Header Section - Title and Search */}
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
          Serial Tracking & Traceability
        </h1>

        <SerialSearch onSearch={handleSearch} isLoading={isLoading} />
      </div>

      {/* Scrollable Content Section */}
      <div>
        {isLoading && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <Search size={18} /> Searching...
              </div>
              <div style={{ fontSize: '14px' }}>Looking up serial number.</div>
            </div>
          </Card>
        )}

        {error && !isLoading && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
              <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <XCircle size={18} /> {error}
              </div>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                Please verify the serial number and try again.
              </div>
            </div>
          </Card>
        )}

        {trace && !isLoading && !error && (
          <div>
            <SerialTraceView trace={trace} />
          </div>
        )}

        {!trace && !isLoading && !error && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              <div style={{ marginBottom: '15px' }}>
                <Search size={48} />
              </div>
              <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                Enter a serial number to view process history
              </div>
              <div style={{ fontSize: '14px' }}>
                View complete process history, measurement data, and defect codes for each product.
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
