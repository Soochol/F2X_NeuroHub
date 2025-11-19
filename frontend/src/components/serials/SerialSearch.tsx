/**
 * Serial Search Component
 */

import { useState, type FormEvent } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Card } from '../common/Card';

interface SerialSearchProps {
  onSearch: (serialNumber: string) => void;
  isLoading?: boolean;
}

export const SerialSearch = ({ onSearch, isLoading }: SerialSearchProps) => {
  const [serialNumber, setSerialNumber] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (serialNumber.trim()) {
      onSearch(serialNumber.trim());
    }
  };

  return (
    <Card>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <Input
              label="Serial 번호 검색"
              placeholder="WF-KR-YYMMDDX-nnn-nnnn (예: WF-KR-250118A-001-0001)"
              value={serialNumber}
              onChange={(e) => setSerialNumber(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={isLoading || !serialNumber.trim()}>
            {isLoading ? '검색 중...' : '🔍 검색'}
          </Button>
        </div>
        <div style={{ marginTop: '10px', fontSize: '13px', color: '#7f8c8d' }}>
          💡 팁: Serial 번호를 입력하면 해당 제품의 전체 공정 이력을 확인할 수 있습니다.
        </div>
      </form>
    </Card>
  );
};
