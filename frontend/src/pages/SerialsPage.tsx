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
      setError(getErrorMessage(err, `Serial 번호 "${serialNumber}"를 찾을 수 없습니다`));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
        Serial Tracking & Traceability
      </h1>

      {/* Search Section */}
      <SerialSearch onSearch={handleSearch} isLoading={isLoading} />

      {/* Loading State */}
      {isLoading && (
        <Card style={{ marginTop: '20px' }}>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <Search size={18} /> 검색 중...
            </div>
            <div style={{ fontSize: '14px' }}>Serial 번호를 조회하고 있습니다.</div>
          </div>
        </Card>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <Card style={{ marginTop: '20px' }}>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
            <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
              <XCircle size={18} /> {error}
            </div>
            <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
              Serial 번호를 확인하고 다시 시도하세요.
            </div>
          </div>
        </Card>
      )}

      {/* Trace Results */}
      {trace && !isLoading && !error && (
        <div style={{ marginTop: '20px' }}>
          <SerialTraceView trace={trace} />
        </div>
      )}

      {/* Empty State (Initial) */}
      {!trace && !isLoading && !error && (
        <Card style={{ marginTop: '20px' }}>
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            <div style={{ marginBottom: '15px' }}>
              <Search size={48} />
            </div>
            <div style={{ fontSize: '16px', marginBottom: '10px' }}>
              Serial 번호를 입력하여 공정 이력을 조회하세요
            </div>
            <div style={{ fontSize: '14px' }}>
              각 제품의 전체 공정 이력, 측정 데이터, 불량 코드 등을 확인할 수 있습니다.
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
