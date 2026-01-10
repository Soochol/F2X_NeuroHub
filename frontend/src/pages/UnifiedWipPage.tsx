/**
 * Unified WIP Page
 * Combines WIP tracking and WIP list functionality into a single page
 * with auto-detection of search input type (WIP ID or LOT number)
 */

import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/common';
import { WipTraceView } from '@/components/organisms/wip/WipTraceView';
import { wipItemsApi } from '@/api';
import type { Lot, WIPItem, WipTrace } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { useLotSearch, getStatusColor, getStatusBgColor, getLotStatusStyle } from '@/hooks';
import { detectSearchType, getWipProcessDisplayText } from '@/utils/wip';
import { format } from 'date-fns';
import {
  Search,
  ArrowLeft,
  AlertCircle,
  QrCode,
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  Package,
  ArrowRight,
} from 'lucide-react';
import styles from './LotSearchPage.module.css';

type ViewMode = 'idle' | 'lot_list' | 'wip_detail';

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'COMPLETED': return <CheckCircle size={14} />;
    case 'FAILED': return <XCircle size={14} />;
    case 'IN_PROGRESS': return <Clock size={14} />;
    default: return <Package size={14} />;
  }
};

export const UnifiedWipPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inputRef = useRef<HTMLInputElement>(null);

  // View state
  const [viewMode, setViewMode] = useState<ViewMode>('idle');
  const [searchInput, setSearchInput] = useState('');
  const [detectedType, setDetectedType] = useState<'wip' | 'lot' | 'unknown'>('unknown');

  // WIP detail state
  const [trace, setTrace] = useState<WipTrace | null>(null);
  const [isLoadingTrace, setIsLoadingTrace] = useState(false);

  // WIP list state
  const [wipItems, setWipItems] = useState<WIPItem[]>([]);
  const [isLoadingWips, setIsLoadingWips] = useState(false);

  // Error state
  const [error, setError] = useState('');

  // LOT search hook
  const {
    lot,
    setLot,
    activeLots,
    isLoadingLots,
    fetchActiveLots,
  } = useLotSearch({ parseWipId: true });

  // Detect search type on input change
  useEffect(() => {
    setDetectedType(detectSearchType(searchInput));
  }, [searchInput]);

  // Handle URL parameters on mount and change
  useEffect(() => {
    const wipId = searchParams.get('wip_id');
    const lotNumber = searchParams.get('lot');

    if (wipId) {
      setSearchInput(wipId);
      loadWipTrace(wipId);
    } else if (lotNumber) {
      setSearchInput(lotNumber);
      loadLotWipItems(lotNumber);
    } else {
      // Reset to idle state
      setViewMode('idle');
      setTrace(null);
      setWipItems([]);
      setLot(null);
    }
  }, [searchParams]);

  const loadWipTrace = async (wipId: string) => {
    setIsLoadingTrace(true);
    setError('');
    setTrace(null);
    setViewMode('wip_detail');

    try {
      const data = await wipItemsApi.getTrace(wipId);
      setTrace(data);
    } catch (err: unknown) {
      setError(getErrorMessage(err, `WIP ID "${wipId}" not found`));
    } finally {
      setIsLoadingTrace(false);
    }
  };

  const loadLotWipItems = async (lotNumber: string) => {
    setIsLoadingWips(true);
    setError('');
    setWipItems([]);
    setViewMode('lot_list');

    try {
      // First, get LOT info
      const { lotsApi } = await import('@/api');
      const lotData = await lotsApi.getLotByNumber(lotNumber);
      setLot(lotData);

      // Then, get WIP items for this LOT
      const wips = await wipItemsApi.getWIPItems({ lot_id: lotData.id });
      setWipItems(wips);
    } catch (err: unknown) {
      setError(getErrorMessage(err, `LOT "${lotNumber}" not found`));
      setViewMode('idle');
    } finally {
      setIsLoadingWips(false);
    }
  };

  const handleSearch = async () => {
    const trimmed = searchInput.trim();
    if (!trimmed) return;

    const type = detectSearchType(trimmed);

    if (type === 'wip') {
      navigate(`/wip/search?wip_id=${encodeURIComponent(trimmed)}`);
    } else if (type === 'lot') {
      navigate(`/wip/search?lot=${encodeURIComponent(trimmed)}`);
    } else {
      // Try as WIP first, fallback to LOT
      setIsLoadingTrace(true);
      setError('');
      try {
        const data = await wipItemsApi.getTrace(trimmed);
        setTrace(data);
        setViewMode('wip_detail');
        navigate(`/wip/search?wip_id=${encodeURIComponent(trimmed)}`, { replace: true });
      } catch {
        // Try as LOT
        try {
          const { lotsApi } = await import('@/api');
          const lotData = await lotsApi.getLotByNumber(trimmed);
          setLot(lotData);
          const wips = await wipItemsApi.getWIPItems({ lot_id: lotData.id });
          setWipItems(wips);
          setViewMode('lot_list');
          navigate(`/wip/search?lot=${encodeURIComponent(trimmed)}`, { replace: true });
        } catch (err: unknown) {
          setError(getErrorMessage(err, `"${trimmed}" not found as WIP ID or LOT number`));
        }
      } finally {
        setIsLoadingTrace(false);
      }
    }
  };

  const handleLotCardClick = async (selectedLot: Lot) => {
    navigate(`/wip/search?lot=${encodeURIComponent(selectedLot.lot_number)}`);
  };

  const handleWipClick = (wipId: string) => {
    navigate(`/wip/search?wip_id=${encodeURIComponent(wipId)}`);
  };

  const handleBack = () => {
    if (viewMode === 'wip_detail' && lot) {
      // Go back to LOT list
      navigate(`/wip/search?lot=${encodeURIComponent(lot.lot_number)}`);
    } else {
      // Go back to idle
      navigate('/wip');
      setSearchInput('');
    }
  };

  const isLoading = isLoadingTrace || isLoadingWips;

  return (
    <div className={styles.pageContainer}>
      {/* Fixed Header Section */}
      <div className={styles.headerSection}>
        <div className={styles.headerContent}>
          <h1 className={styles.pageTitle}>WIP Management</h1>
          <p className={styles.pageSubtitle}>
            Search for WIP by ID or LOT number (auto-detect)
          </p>
        </div>

        <Card>
          <div className={styles.searchForm}>
            <div className={styles.searchInputWrapper}>
              <label htmlFor="searchInput" className={styles.searchLabel}>
                WIP ID or LOT Number
                {searchInput && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    {detectedType === 'wip' && '(WIP ID detected)'}
                    {detectedType === 'lot' && '(LOT number detected)'}
                    {detectedType === 'unknown' && searchInput.length > 0 && '(auto-detect on search)'}
                  </span>
                )}
              </label>
              <div className={styles.searchInputContainer}>
                <QrCode size={18} className={styles.searchIcon} />
                <input
                  ref={inputRef}
                  id="searchInput"
                  type="text"
                  placeholder="Enter WIP ID (e.g., WIP-DT01A10251101-001) or LOT number (e.g., DT01A10251101)"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className={styles.searchInput}
                />
              </div>
            </div>
            <Button onClick={handleSearch} disabled={!searchInput.trim() || isLoading} className={styles.searchButton}>
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </div>

          {error && (
            <div className={styles.errorMessage}>
              <AlertCircle size={18} />
              {error}
            </div>
          )}
        </Card>
      </div>

      {/* Scrollable Content Section */}
      <div>
        {/* Idle State: Show Active LOTs */}
        {viewMode === 'idle' && !isLoading && (
          <Card>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Active LOTs</h2>
              <Button variant="secondary" size="sm" onClick={fetchActiveLots}>Refresh</Button>
            </div>
            {isLoadingLots ? (
              <div className={styles.loadingText}>Loading LOTs...</div>
            ) : activeLots.length === 0 ? (
              <div className={styles.emptyText}>No active LOTs found.</div>
            ) : (
              <div className={styles.lotCardsGrid}>
                {activeLots.map((activeLot) => (
                  <div
                    key={activeLot.id}
                    onClick={() => handleLotCardClick(activeLot)}
                    className={styles.lotCard}
                  >
                    <div className={styles.lotCardHeader}>
                      <div>
                        <div className={styles.lotTitleRow}>
                          <span className={styles.lotNumber}>{activeLot.lot_number}</span>
                          <span className={styles.statusBadge} style={getLotStatusStyle(activeLot.status)}>
                            {activeLot.status}
                          </span>
                        </div>
                        {activeLot.product_model && (
                          <div className={styles.productInfo}>
                            <strong>{activeLot.product_model.model_code}</strong> - {activeLot.product_model.model_name}
                          </div>
                        )}
                      </div>
                      <div className={styles.targetQuantity}>
                        <div className={styles.targetValue}>{activeLot.target_quantity} Units</div>
                        <div className={styles.targetLabel}>Target</div>
                      </div>
                    </div>
                    <div className={styles.lotMetaGrid}>
                      <div className={styles.metaItem}>
                        <Calendar size={14} />
                        {format(new Date(activeLot.production_date), 'yyyy-MM-dd')}
                      </div>
                      <div className={styles.metaItem}>
                        <Package size={14} />
                        WIP Count: <strong className={styles.metaHighlight}>{activeLot.wip_count ?? 0}</strong> / {activeLot.target_quantity}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* LOT List State: Show WIP items for selected LOT */}
        {viewMode === 'lot_list' && (
          <div className={styles.contentSection}>
            <Button variant="ghost" size="sm" onClick={handleBack} className={styles.backButton}>
              <ArrowLeft size={16} /> Back to LOT List
            </Button>

            {lot && (
              <>
                <Card>
                  <div className={styles.lotCardSelected}>
                    <div className={styles.lotCardHeader}>
                      <div>
                        <div className={styles.lotTitleRow}>
                          <span className={styles.lotNumber}>{lot.lot_number}</span>
                          <span className={styles.statusBadge} style={getLotStatusStyle(lot.status)}>
                            {lot.status}
                          </span>
                        </div>
                        {lot.product_model && (
                          <div className={styles.productInfo}>
                            <strong>{lot.product_model.model_code}</strong> - {lot.product_model.model_name}
                          </div>
                        )}
                      </div>
                      <div className={styles.targetQuantity}>
                        <div className={styles.targetValue}>{lot.target_quantity} Units</div>
                        <div className={styles.targetLabel}>Target</div>
                      </div>
                    </div>
                    <div className={styles.lotMetaGridCompact}>
                      <div className={styles.metaItem}>
                        <Calendar size={14} />
                        {format(new Date(lot.production_date), 'yyyy-MM-dd')}
                      </div>
                      <div className={styles.metaItem}>
                        <Package size={14} />
                        WIP Count: <strong className={styles.metaHighlight}>{wipItems.length}</strong> / {lot.target_quantity}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* WIP Items Header */}
                <div className={styles.itemsHeader}>
                  <h2 className={styles.itemsTitle}>WIP Items</h2>
                  <div className={styles.itemsCount}>
                    <Package size={16} />
                    <span>Total: <strong>{wipItems.length}</strong></span>
                  </div>
                </div>

                {isLoadingWips ? (
                  <Card>
                    <div className={styles.loadingText}>Loading WIP items...</div>
                  </Card>
                ) : wipItems.length === 0 ? (
                  <Card>
                    <div className={styles.emptyItemsContainer}>
                      <Package size={48} className={styles.emptyIcon} />
                      <div className={styles.emptyMessage}>No WIP items found for this LOT.</div>
                    </div>
                  </Card>
                ) : (
                  <div className={styles.itemsList}>
                    {wipItems.map((wip) => (
                      <div
                        key={wip.id}
                        onClick={() => handleWipClick(wip.wip_id)}
                        className={styles.itemCard}
                      >
                        <div className={styles.itemCardHeader}>
                          <div className={styles.itemId}>{wip.wip_id}</div>
                          <div
                            className={styles.itemStatusBadge}
                            style={{ backgroundColor: getStatusBgColor(wip.status), color: getStatusColor(wip.status) }}
                          >
                            {getStatusIcon(wip.status)}
                            {wip.status}
                          </div>
                        </div>
                        <div className={styles.itemInfoSection}>
                          <div className={styles.itemInfoLabel}>Current Process</div>
                          <div className={styles.itemInfoValue}>
                            {getWipProcessDisplayText(wip)}
                          </div>
                        </div>
                        <div className={styles.itemCardFooter}>
                          <div className={styles.itemDate}>
                            <Calendar size={12} />
                            {format(new Date(wip.created_at), 'yyyy-MM-dd')}
                          </div>
                          <div className={styles.viewTraceLink}>
                            View Trace <ArrowRight size={14} className={styles.viewTraceLinkIcon} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* WIP Detail State: Show trace view */}
        {viewMode === 'wip_detail' && (
          <div>
            <Button variant="ghost" size="sm" onClick={handleBack} className={styles.backButton}>
              <ArrowLeft size={16} /> {lot ? 'Back to WIP List' : 'Back'}
            </Button>

            {isLoadingTrace && (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                  <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <Search size={18} /> Searching...
                  </div>
                  <div style={{ fontSize: '14px' }}>Looking up WIP ID.</div>
                </div>
              </Card>
            )}

            {trace && !isLoadingTrace && (
              <WipTraceView trace={trace} />
            )}

            {!trace && !isLoadingTrace && !error && (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                  <div style={{ marginBottom: '15px' }}>
                    <Search size={48} />
                  </div>
                  <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                    Enter a WIP ID to view process history
                  </div>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Loading State for initial search */}
        {isLoading && viewMode === 'idle' && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
              <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <Search size={18} /> Searching...
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
