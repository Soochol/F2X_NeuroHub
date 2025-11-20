/**
 * Serial Search Component
 */

import { useState, type FormEvent } from 'react';
import { Input, Button } from '../../atoms';
import { Card } from '../../molecules';
import { Search, Lightbulb } from 'lucide-react';

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
              label="Search Serial Number"
              placeholder="WF-KR-YYMMDDX-nnn-nnnn (e.g. WF-KR-250118A-001-0001)"
              value={serialNumber}
              onChange={(e) => setSerialNumber(e.target.value)}
              required
              wrapperStyle={{ marginBottom: 0 }}
            />
          </div>
          <Button type="submit" disabled={isLoading || !serialNumber.trim()}>
            {isLoading ? 'Searching...' : <><Search size={16} style={{ marginRight: '6px' }} />Search</>}
          </Button>
        </div>
        <div style={{ marginTop: '10px', fontSize: '13px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Lightbulb size={14} /> Tip: Enter a serial number to view complete process history for that product.
        </div>
      </form>
    </Card>
  );
};
