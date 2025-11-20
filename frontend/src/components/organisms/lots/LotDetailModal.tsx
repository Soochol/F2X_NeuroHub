/**
 * LOT Detail Modal Component
 */

import { useState, useEffect } from 'react';
import { Button, Select, Input } from '../../atoms';
import { Modal } from '../../molecules';
import { lotsApi } from '@/api';
import { LotStatus, type Lot, type LotUpdate, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';

interface LotDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  lotId: number;
  onUpdate: () => void;
}

export const LotDetailModal = ({ isOpen, onClose, lotId, onUpdate }: LotDetailModalProps) => {
  const [lot, setLot] = useState<Lot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<LotUpdate>({});
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && lotId) {
      fetchLot();
    }
  }, [isOpen, lotId]);

  const fetchLot = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await lotsApi.getLot(lotId);
      setLot(data);
      setEditData({
        status: data.status,
        busbar_lot: data.busbar_lot,
        sma_spring_lot: data.sma_spring_lot,
        pin_lot: data.pin_lot,
        hsg_lot: data.hsg_lot,
      });
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'LOT 정보를 불러오지 못했습니다'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await lotsApi.updateLot(lotId, editData);
      setIsEditing(false);
      await fetchLot();
      onUpdate();
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'LOT 업데이트 실패'));
    }
  };

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="LOT 상세 정보">
        <div style={{ textAlign: 'center', padding: '20px' }}>로딩 중...</div>
      </Modal>
    );
  }

  if (error && !lot) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="LOT 상세 정보">
        <div style={{ color: 'var(--color-error)', padding: '20px' }}>{error}</div>
      </Modal>
    );
  }

  if (!lot) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`LOT 상세: ${lot.lot_number}`}
      width="800px"
      footer={
        <>
          {isEditing ? (
            <>
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                취소
              </Button>
              <Button onClick={handleUpdate}>저장</Button>
            </>
          ) : (
            <>
              <Button variant="secondary" onClick={onClose}>
                닫기
              </Button>
              <Button onClick={() => setIsEditing(true)}>수정</Button>
            </>
          )}
        </>
      }
    >
      <div>
        {/* Basic Info */}
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '15px' }}>기본 정보</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>LOT 번호</div>
              <div style={{ fontWeight: 'bold' }}>{lot.lot_number}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>제품 모델</div>
              <div style={{ fontWeight: 'bold' }}>
                {lot.product_model ? `${lot.product_model.model_code} - ${lot.product_model.model_name}` : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>목표 수량</div>
              <div style={{ fontWeight: 'bold' }}>{lot.target_quantity}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>생산 날짜</div>
              <div style={{ fontWeight: 'bold' }}>
                {format(new Date(lot.production_date), 'yyyy-MM-dd')}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>시프트</div>
              <div style={{ fontWeight: 'bold' }}>{lot.shift}</div>
            </div>
            <div>
              {isEditing ? (
                <Select
                  label="상태"
                  value={editData.status || lot.status}
                  onChange={(e) => setEditData({ ...editData, status: e.target.value as LotStatus })}
                  options={[
                    { value: LotStatus.CREATED, label: '생성됨' },
                    { value: LotStatus.IN_PROGRESS, label: '진행중' },
                    { value: LotStatus.COMPLETED, label: '완료' },
                    { value: LotStatus.CLOSED, label: '종료' },
                  ]}
                />
              ) : (
                <>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>상태</div>
                  <div>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        backgroundColor:
                          lot.status === LotStatus.COMPLETED
                            ? 'var(--color-success-bg)'
                            : lot.status === LotStatus.IN_PROGRESS
                            ? 'var(--color-info-bg)'
                            : 'var(--color-bg-tertiary)',
                        color:
                          lot.status === LotStatus.COMPLETED
                            ? 'var(--color-success)'
                            : lot.status === LotStatus.IN_PROGRESS
                            ? 'var(--color-info)'
                            : 'var(--color-text-secondary)',
                      }}
                    >
                      {lot.status}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Component LOTs */}
        <div style={{ marginBottom: '20px', paddingTop: '20px', borderTop: '1px solid var(--color-border)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '15px' }}>구성품 LOT</h3>
          {isEditing ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <Input
                label="Busbar LOT"
                value={editData.busbar_lot || ''}
                onChange={(e) => setEditData({ ...editData, busbar_lot: e.target.value })}
              />
              <Input
                label="SMA Spring LOT"
                value={editData.sma_spring_lot || ''}
                onChange={(e) => setEditData({ ...editData, sma_spring_lot: e.target.value })}
              />
              <Input
                label="Pin LOT"
                value={editData.pin_lot || ''}
                onChange={(e) => setEditData({ ...editData, pin_lot: e.target.value })}
              />
              <Input
                label="Housing LOT"
                value={editData.hsg_lot || ''}
                onChange={(e) => setEditData({ ...editData, hsg_lot: e.target.value })}
              />
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Busbar</div>
                <div>{lot.busbar_lot || 'N/A'}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>SMA Spring</div>
                <div>{lot.sma_spring_lot || 'N/A'}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Pin</div>
                <div>{lot.pin_lot || 'N/A'}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '5px' }}>Housing</div>
                <div>{lot.hsg_lot || 'N/A'}</div>
              </div>
            </div>
          )}
        </div>

        {/* Timestamps */}
        <div style={{ paddingTop: '20px', borderTop: '1px solid var(--color-border)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '15px' }}>타임스탬프</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', fontSize: '13px' }}>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>생성일시</div>
              <div>{format(new Date(lot.created_at), 'yyyy-MM-dd HH:mm:ss')}</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>수정일시</div>
              <div>{format(new Date(lot.updated_at), 'yyyy-MM-dd HH:mm:ss')}</div>
            </div>
            {lot.completed_at && (
              <div>
                <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>완료일시</div>
                <div>{format(new Date(lot.completed_at), 'yyyy-MM-dd HH:mm:ss')}</div>
              </div>
            )}
            {lot.closed_at && (
              <div>
                <div style={{ color: 'var(--color-text-secondary)', marginBottom: '5px' }}>종료일시</div>
                <div>{format(new Date(lot.closed_at), 'yyyy-MM-dd HH:mm:ss')}</div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div
            style={{
              marginTop: '15px',
              padding: '10px',
              backgroundColor: 'var(--color-error-bg)',
              color: 'var(--color-error)',
              borderRadius: '4px',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
};
