/**
 * WIP List by LOT Page
 * Search for a LOT by number and list all associated WIP items
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '@/components/common';
import { ArrowRight, AlertCircle, QrCode, Calendar, CheckCircle, XCircle, Clock, Package } from 'lucide-react';
import { wipItemsApi } from '@/api';
import type { Lot, WIPItem } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { useLotSearch, getStatusColor, getStatusBgColor, getLotStatusStyle } from '@/hooks';
import { getWipProcessDisplayText } from '@/utils/wip';
import { format } from 'date-fns';
import styles from './LotSearchPage.module.css';

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'COMPLETED': return <CheckCircle size={14} />;
    case 'FAILED': return <XCircle size={14} />;
    case 'IN_PROGRESS': return <Clock size={14} />;
    default: return <Package size={14} />;
  }
};

export const WipByLotPage = () => {
  const navigate = useNavigate();
  const [wipItems, setWipItems] = useState<WIPItem[]>([]);

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
  } = useLotSearch({ parseWipId: true });

  const handleLotCardClick = async (selectedLot: Lot) => {
    setLotNumber(selectedLot.lot_number);
    setLot(selectedLot);
    setError('');

    try {
      const wips = await wipItemsApi.getWIPItems({ lot_id: selectedLot.id });
      setWipItems(wips);
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Failed to load WIP items'));
    }
  };

  const handleSearch = async () => {
    setWipItems([]);
    const foundLot = await searchLot();

    if (foundLot) {
      try {
        const wips = await wipItemsApi.getWIPItems({ lot_id: foundLot.id });
        setWipItems(wips);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Failed to load WIP items'));
      }
    }
  };

  const handleWipClick = (wipId: string) => {
    navigate(`/wip/tracking?wip_id=${wipId}`);
  };

  const handleReset = () => {
    resetSearch();
    setWipItems([]);
  };

  return (
    <div className={styles.pageContainer}>
      {/* Fixed Header Section */}
      <div className={styles.headerSection}>
        <div className={styles.headerContent}>
          <h1 className={styles.pageTitle}>WIP List by LOT</h1>
          <p className={styles.pageSubtitle}>
            Search for a LOT to view all associated WIP items and their status
          </p>
        </div>

        <Card>
          <div className={styles.searchForm}>
            <div className={styles.searchInputWrapper}>
              <label htmlFor="lotNumber" className={styles.searchLabel}>
                LOT Number or WIP ID
              </label>
              <div className={styles.searchInputContainer}>
                <QrCode size={18} className={styles.searchIcon} />
                <input
                  ref={inputRef}
                  id="lotNumber"
                  type="text"
                  placeholder="Enter LOT Number or WIP ID (e.g., DT01A10251101 or WIP-DT01A10251101-001)"
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

            {wipItems.length === 0 ? (
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
          </div>
        )}
      </div>
    </div>
  );
};
