/**
 * Unified Serial Page
 * Combines Serial tracking and Serial list functionality into a single page
 * with auto-detection of search input type (Serial Number or LOT number)
 */

import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/common';
import { SerialTraceView } from '@/components/organisms/serials';
import { serialsApi } from '@/api';
import type { Lot, Serial, SerialTrace } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { useLotSearch, getStatusColor, getStatusBgColor, getLotStatusStyle } from '@/hooks';
import { detectSerialSearchType } from '@/utils/serialNumber';
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
  Hash,
  ArrowRight,
} from 'lucide-react';
import styles from './LotSearchPage.module.css';

type ViewMode = 'idle' | 'lot_list' | 'serial_detail';

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'PASSED': return <CheckCircle size={14} />;
    case 'FAILED': return <XCircle size={14} />;
    case 'IN_PROGRESS': return <Clock size={14} />;
    default: return <Hash size={14} />;
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'PASSED': return 'PASS';
    case 'FAILED': return 'FAIL';
    default: return status;
  }
};

export const UnifiedSerialPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inputRef = useRef<HTMLInputElement>(null);

  // View state
  const [viewMode, setViewMode] = useState<ViewMode>('idle');
  const [searchInput, setSearchInput] = useState('');
  const [detectedType, setDetectedType] = useState<'serial' | 'lot' | 'unknown'>('unknown');

  // Serial detail state
  const [trace, setTrace] = useState<SerialTrace | null>(null);
  const [isLoadingTrace, setIsLoadingTrace] = useState(false);

  // Serial list state
  const [serials, setSerials] = useState<Serial[]>([]);
  const [isLoadingSerials, setIsLoadingSerials] = useState(false);

  // Error state
  const [error, setError] = useState('');

  // LOT search hook
  const {
    lot,
    setLot,
    activeLots,
    isLoadingLots,
    fetchActiveLots,
  } = useLotSearch({ parseSerialNumber: true });

  // Detect search type on input change
  useEffect(() => {
    setDetectedType(detectSerialSearchType(searchInput));
  }, [searchInput]);

  // Handle URL parameters on mount and change
  useEffect(() => {
    const serial = searchParams.get('serial');
    const lotNumber = searchParams.get('lot');

    if (serial) {
      setSearchInput(serial);
      loadSerialTrace(serial);
    } else if (lotNumber) {
      setSearchInput(lotNumber);
      loadLotSerials(lotNumber);
    } else {
      // Reset to idle state
      setViewMode('idle');
      setTrace(null);
      setSerials([]);
      setLot(null);
    }
  }, [searchParams]);

  const loadSerialTrace = async (serialNumber: string) => {
    setIsLoadingTrace(true);
    setError('');
    setTrace(null);
    setViewMode('serial_detail');

    try {
      const data = await serialsApi.getTrace(serialNumber);
      setTrace(data);
    } catch (err: unknown) {
      setError(getErrorMessage(err, `Serial number "${serialNumber}" not found`));
    } finally {
      setIsLoadingTrace(false);
    }
  };

  const loadLotSerials = async (lotNumber: string) => {
    setIsLoadingSerials(true);
    setError('');
    setSerials([]);
    setViewMode('lot_list');

    try {
      // First, get LOT info
      const { lotsApi } = await import('@/api');
      const lotData = await lotsApi.getLotByNumber(lotNumber);
      setLot(lotData);

      // Then, get Serial items for this LOT
      const serialList = await serialsApi.getSerialsByLot(lotData.id);
      setSerials(serialList);
    } catch (err: unknown) {
      setError(getErrorMessage(err, `LOT "${lotNumber}" not found`));
      setViewMode('idle');
    } finally {
      setIsLoadingSerials(false);
    }
  };

  const handleSearch = async () => {
    const trimmed = searchInput.trim();
    if (!trimmed) return;

    const type = detectSerialSearchType(trimmed);

    if (type === 'serial') {
      navigate(`/serials/search?serial=${encodeURIComponent(trimmed)}`);
    } else if (type === 'lot') {
      navigate(`/serials/search?lot=${encodeURIComponent(trimmed)}`);
    } else {
      // Try as Serial first, fallback to LOT
      setIsLoadingTrace(true);
      setError('');
      try {
        const data = await serialsApi.getTrace(trimmed);
        setTrace(data);
        setViewMode('serial_detail');
        navigate(`/serials/search?serial=${encodeURIComponent(trimmed)}`, { replace: true });
      } catch {
        // Try as LOT
        try {
          const { lotsApi } = await import('@/api');
          const lotData = await lotsApi.getLotByNumber(trimmed);
          setLot(lotData);
          const serialList = await serialsApi.getSerialsByLot(lotData.id);
          setSerials(serialList);
          setViewMode('lot_list');
          navigate(`/serials/search?lot=${encodeURIComponent(trimmed)}`, { replace: true });
        } catch (err: unknown) {
          setError(getErrorMessage(err, `"${trimmed}" not found as Serial number or LOT number`));
        }
      } finally {
        setIsLoadingTrace(false);
      }
    }
  };

  const handleLotCardClick = async (selectedLot: Lot) => {
    navigate(`/serials/search?lot=${encodeURIComponent(selectedLot.lot_number)}`);
  };

  const handleSerialClick = (serialNumber: string) => {
    navigate(`/serials/search?serial=${encodeURIComponent(serialNumber)}`);
  };

  const handleBack = () => {
    if (viewMode === 'serial_detail' && lot) {
      // Go back to LOT list
      navigate(`/serials/search?lot=${encodeURIComponent(lot.lot_number)}`);
    } else {
      // Go back to idle
      navigate('/serials/search');
      setSearchInput('');
    }
  };

  const isLoading = isLoadingTrace || isLoadingSerials;

  return (
    <div className={styles.pageContainer}>
      {/* Fixed Header Section */}
      <div className={styles.headerSection}>
        <div className={styles.headerContent}>
          <h1 className={styles.pageTitle}>Serial Management</h1>
          <p className={styles.pageSubtitle}>
            Search for Serial by number or LOT number (auto-detect)
          </p>
        </div>

        <Card>
          <div className={styles.searchForm}>
            <div className={styles.searchInputWrapper}>
              <label htmlFor="searchInput" className={styles.searchLabel}>
                Serial Number or LOT Number
                {searchInput && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    {detectedType === 'serial' && '(Serial number detected)'}
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
                  placeholder="Enter Serial Number (e.g., KR01PSA251101001) or LOT number (e.g., DT01A10251101)"
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
                        <Hash size={14} />
                        Serial Count: <strong className={styles.metaHighlight}>{activeLot.serial_count ?? 0}</strong> / {activeLot.target_quantity}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {/* LOT List State: Show Serial items for selected LOT */}
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
                        <Hash size={14} />
                        Serial Count: <strong className={styles.metaHighlight}>{serials.length}</strong> / {lot.target_quantity}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Serial Items Header */}
                <div className={styles.itemsHeader}>
                  <h2 className={styles.itemsTitle}>Serial Items</h2>
                  <div className={styles.itemsCount}>
                    <Hash size={16} />
                    <span>Total: <strong>{serials.length}</strong></span>
                  </div>
                </div>

                {isLoadingSerials ? (
                  <Card>
                    <div className={styles.loadingText}>Loading Serial items...</div>
                  </Card>
                ) : serials.length === 0 ? (
                  <Card>
                    <div className={styles.emptyItemsContainer}>
                      <Hash size={48} className={styles.emptyIcon} />
                      <div className={styles.emptyMessage}>No Serial items found for this LOT.</div>
                    </div>
                  </Card>
                ) : (
                  <div className={styles.itemsList}>
                    {serials.map((serial) => (
                      <div
                        key={serial.id}
                        onClick={() => handleSerialClick(serial.serial_number)}
                        className={styles.itemCard}
                      >
                        <div className={styles.itemCardHeader}>
                          <div className={styles.itemId}>{serial.serial_number}</div>
                          <div
                            className={styles.itemStatusBadge}
                            style={{ backgroundColor: getStatusBgColor(serial.status), color: getStatusColor(serial.status) }}
                          >
                            {getStatusIcon(serial.status)}
                            {getStatusLabel(serial.status)}
                          </div>
                        </div>
                        <div className={styles.itemInfoSection}>
                          <div className={styles.itemInfoLabel}>Sequence in LOT</div>
                          <div className={styles.itemInfoValue}>
                            #{serial.sequence_in_lot}
                            {serial.rework_count > 0 && (
                              <span className={styles.reworkBadge}>(Rework: {serial.rework_count})</span>
                            )}
                          </div>
                        </div>
                        <div className={styles.itemCardFooter}>
                          <div className={styles.itemDate}>
                            <Calendar size={12} />
                            {format(new Date(serial.created_at), 'yyyy-MM-dd HH:mm')}
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

        {/* Serial Detail State: Show trace view */}
        {viewMode === 'serial_detail' && (
          <div>
            <Button variant="ghost" size="sm" onClick={handleBack} className={styles.backButton}>
              <ArrowLeft size={16} /> {lot ? 'Back to Serial List' : 'Back'}
            </Button>

            {isLoadingTrace && (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                  <div style={{ fontSize: '18px', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    <Search size={18} /> Searching...
                  </div>
                  <div style={{ fontSize: '14px' }}>Looking up Serial number.</div>
                </div>
              </Card>
            )}

            {trace && !isLoadingTrace && (
              <SerialTraceView trace={trace} />
            )}

            {!trace && !isLoadingTrace && !error && (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
                  <div style={{ marginBottom: '15px' }}>
                    <Search size={48} />
                  </div>
                  <div style={{ fontSize: '16px', marginBottom: '10px' }}>
                    Enter a Serial number to view process history
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
