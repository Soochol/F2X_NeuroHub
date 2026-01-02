/**
 * Serial List by LOT Page
 * Search for a LOT by number and list all associated Serial items
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/common';
import { ArrowRight, AlertCircle, QrCode, Calendar, CheckCircle, XCircle, Clock, Hash } from 'lucide-react';
import { serialsApi } from '@/api';
import type { Lot, Serial } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { useLotSearch, getStatusColor, getStatusBgColor, getLotStatusStyle } from '@/hooks';
import { format } from 'date-fns';
import styles from './LotSearchPage.module.css';

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

export const SerialByLotPage = () => {
  const navigate = useNavigate();
  const [serials, setSerials] = useState<Serial[]>([]);

  const {
    lotNumber,
    setLotNumber,
    inputRef,
    lot,
    setLot,
    isLoading,
    error,
    setError,
    activeLots,
    isLoadingLots,
    fetchActiveLots,
    searchLot,
    resetSearch,
  } = useLotSearch({ parseSerialNumber: true });

  const handleLotCardClick = async (selectedLot: Lot) => {
    setLotNumber(selectedLot.lot_number);
    setLot(selectedLot);
    setError('');

    try {
      const serialList = await serialsApi.getSerialsByLot(selectedLot.id);
      setSerials(serialList);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load Serial items'));
    }
  };

  const handleSearch = async () => {
    setSerials([]);
    const foundLot = await searchLot();

    if (foundLot) {
      try {
        const serialList = await serialsApi.getSerialsByLot(foundLot.id);
        setSerials(serialList);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Failed to load Serial items'));
      }
    }
  };

  const handleSerialClick = (serialNumber: string) => {
    navigate(`/serials/tracking?serial=${serialNumber}`);
  };

  const handleReset = () => {
    resetSearch();
    setSerials([]);
  };

  return (
    <div className={styles.pageContainer}>
      {/* Fixed Header Section */}
      <div className={styles.headerSection}>
        <div className={styles.headerContent}>
          <h1 className={styles.pageTitle}>Serial List by LOT</h1>
          <p className={styles.pageSubtitle}>
            Search for a LOT to view all associated Serial items and their status
          </p>
        </div>

        <Card>
          <div className={styles.searchForm}>
            <div className={styles.searchInputWrapper}>
              <label htmlFor="lotNumber" className={styles.searchLabel}>
                LOT Number or Serial Number
              </label>
              <div className={styles.searchInputContainer}>
                <QrCode size={18} className={styles.searchIcon} />
                <input
                  ref={inputRef}
                  id="lotNumber"
                  type="text"
                  placeholder="Enter LOT Number or Serial Number (e.g., DT01A10251101 or DT01A10251101-001)"
                  value={lotNumber}
                  onChange={(e) => setLotNumber(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className={styles.searchInput}
                />
              </div>
            </div>
            <Button onClick={handleSearch} disabled={!lotNumber.trim() || isLoading} className={styles.searchButton}>
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
        {/* Active LOT Cards */}
        {!lot && (
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

        {/* Selected LOT Details */}
        {lot && (
          <div className={styles.contentSection}>
            <Button variant="ghost" size="sm" onClick={handleReset} className={styles.backButton}>
              ← Back to LOT List
            </Button>

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

            {serials.length === 0 ? (
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
          </div>
        )}
      </div>
    </div>
  );
};
