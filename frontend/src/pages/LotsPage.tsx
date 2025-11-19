/**
 * LOTs Management Page
 */

import { useState, useEffect } from 'react';
import { Button, Select, Input, Card } from '@/components/common';
import { LotCreateModal, LotDetailModal } from '@/components/lots';
import { lotsApi } from '@/api';
import apiClient from '@/api/client';
import { LotStatus, type Lot, type ProductModel, getErrorMessage } from '@/types/api';
import { format } from 'date-fns';

export const LotsPage = () => {
  const [lots, setLots] = useState<Lot[]>([]);
  const [productModels, setProductModels] = useState<ProductModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState<LotStatus | ''>('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedLotId, setSelectedLotId] = useState<number | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(0);
  const [totalLots, setTotalLots] = useState(0);
  const lotsPerPage = 20;

  useEffect(() => {
    fetchProductModels();
    fetchLots();
  }, [statusFilter, currentPage]);

  const fetchProductModels = async () => {
    try {
      const response = await apiClient.get<ProductModel[]>('/product-models/');
      setProductModels(response.data);
    } catch (err: unknown) {
      console.error('Failed to fetch product models:', err);
    }
  };

  const fetchLots = async () => {
    setIsLoading(true);
    setError('');
    try {
      const params: { skip?: number; limit?: number; status?: LotStatus } = {
        skip: currentPage * lotsPerPage,
        limit: lotsPerPage,
      };
      if (statusFilter) {
        params.status = statusFilter;
      }

      const response = await lotsApi.getLots(params);
      // 백엔드는 배열을 직접 반환하거나 PaginatedResponse를 반환
      if (Array.isArray(response)) {
        setLots(response);
        setTotalLots(response.length);
      } else {
        setLots(response.items);
        setTotalLots(response.total);
      }
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'LOT 목록을 불러오지 못했습니다'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSuccess = () => {
    fetchLots();
    setCurrentPage(0);
  };

  const handleLotClick = (lotId: number) => {
    setSelectedLotId(lotId);
  };

  const filteredLots = lots.filter((lot) => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        lot.lot_number.toLowerCase().includes(query) ||
        lot.product_model?.name.toLowerCase().includes(query)
      );
    }
    return true;
  });

  const totalPages = Math.ceil(totalLots / lotsPerPage);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>LOT Management</h1>
        <Button onClick={() => setIsCreateModalOpen(true)}>+ 새 LOT 생성</Button>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <Input
              label="검색"
              placeholder="LOT 번호 또는 제품 모델 이름 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div style={{ width: '200px' }}>
            <Select
              label="상태 필터"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as LotStatus | '');
                setCurrentPage(0);
              }}
              options={[
                { value: '', label: '전체' },
                { value: LotStatus.CREATED, label: '생성됨' },
                { value: LotStatus.IN_PROGRESS, label: '진행중' },
                { value: LotStatus.COMPLETED, label: '완료' },
                { value: LotStatus.CLOSED, label: '종료' },
              ]}
            />
          </div>
          <Button variant="secondary" onClick={() => { setSearchQuery(''); setStatusFilter(''); setCurrentPage(0); fetchLots(); }}>
            초기화
          </Button>
        </div>
      </Card>

      {/* LOTs Table */}
      <Card>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            로딩 중...
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-error)' }}>
            {error}
          </div>
        ) : filteredLots.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            LOT가 없습니다. 새 LOT를 생성하세요.
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-border-strong)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>LOT 번호</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>제품 모델</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>상태</th>
                    <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>목표 수량</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>생산 날짜</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>시프트</th>
                    <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>생성일시</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLots.map((lot) => (
                    <tr
                      key={lot.id}
                      onClick={() => handleLotClick(lot.id)}
                      style={{
                        borderBottom: '1px solid var(--color-border)',
                        cursor: 'pointer',
                        transition: 'background-color 0.2s',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '12px', fontWeight: '500' }}>{lot.lot_number}</td>
                      <td style={{ padding: '12px' }}>
                        {lot.product_model ? (
                          <div>
                            <div style={{ fontWeight: '500' }}>{lot.product_model.code}</div>
                            <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{lot.product_model.name}</div>
                          </div>
                        ) : (
                          'N/A'
                        )}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span
                          style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            backgroundColor:
                              lot.status === LotStatus.COMPLETED
                                ? 'var(--color-success-bg, rgba(39, 174, 96, 0.15))'
                                : lot.status === LotStatus.IN_PROGRESS
                                ? 'var(--color-info-bg, rgba(52, 152, 219, 0.15))'
                                : lot.status === LotStatus.CLOSED
                                ? 'var(--color-bg-tertiary)'
                                : 'var(--color-warning-bg, rgba(243, 156, 18, 0.15))',
                            color:
                              lot.status === LotStatus.COMPLETED
                                ? 'var(--color-success)'
                                : lot.status === LotStatus.IN_PROGRESS
                                ? 'var(--color-info, var(--color-brand))'
                                : lot.status === LotStatus.CLOSED
                                ? 'var(--color-text-tertiary)'
                                : 'var(--color-warning)',
                          }}
                        >
                          {lot.status}
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>{lot.target_quantity}</td>
                      <td style={{ padding: '12px' }}>
                        {format(new Date(lot.production_date), 'yyyy-MM-dd')}
                      </td>
                      <td style={{ padding: '12px' }}>{lot.shift}</td>
                      <td style={{ padding: '12px', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
                        {format(new Date(lot.created_at), 'yyyy-MM-dd HH:mm')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div
                style={{
                  marginTop: '20px',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  gap: '10px',
                }}
              >
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 0}
                >
                  이전
                </Button>
                <span style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                  {currentPage + 1} / {totalPages}
                </span>
                <Button
                  variant="secondary"
                  size="small"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage >= totalPages - 1}
                >
                  다음
                </Button>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Modals */}
      <LotCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handleCreateSuccess}
        productModels={productModels}
      />

      {selectedLotId && (
        <LotDetailModal
          isOpen={!!selectedLotId}
          onClose={() => setSelectedLotId(null)}
          lotId={selectedLotId}
          onUpdate={fetchLots}
        />
      )}
    </div>
  );
};
