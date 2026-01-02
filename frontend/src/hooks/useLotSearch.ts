/**
 * useLotSearch Hook
 *
 * Shared hook for LOT search functionality used by:
 * - WipByLotPage: Search LOT and display WIP items
 * - SerialByLotPage: Search LOT and display Serial items
 *
 * Provides:
 * - Active LOTs loading
 * - LOT number input parsing (supports WIP ID and Serial number formats)
 * - Search state management
 * - Status styling utilities
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { lotsApi } from '@/api';
import type { Lot } from '@/types/api';
import { getErrorMessage } from '@/types/api';

// ============================================================================
// Types
// ============================================================================

export interface UseLotSearchOptions {
  /** Parse input as WIP ID format (WIP-{LOT}-{SEQ}) */
  parseWipId?: boolean;
  /** Parse input as Serial number format ({LOT}-{SEQ}) */
  parseSerialNumber?: boolean;
}

export interface UseLotSearchReturn {
  // Input state
  lotNumber: string;
  setLotNumber: (value: string) => void;
  inputRef: React.RefObject<HTMLInputElement | null>;

  // Selected LOT state
  lot: Lot | null;
  setLot: (lot: Lot | null) => void;

  // Loading/Error state
  isLoading: boolean;
  error: string;
  setError: (error: string) => void;

  // Active LOTs
  activeLots: Lot[];
  isLoadingLots: boolean;
  fetchActiveLots: () => Promise<void>;

  // Actions
  searchLot: () => Promise<Lot | null>;
  resetSearch: () => void;

  // Utilities
  parseLotNumber: (input: string) => string;
}

// ============================================================================
// Status Styling Utilities
// ============================================================================

/**
 * Get text color for status
 * Works with both WIP and Serial statuses
 */
export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'COMPLETED':
    case 'PASSED':
      return 'var(--color-success)';
    case 'FAILED':
      return 'var(--color-error)';
    case 'IN_PROGRESS':
      return 'var(--color-info)';
    case 'CREATED':
      return 'var(--color-warning)';
    default:
      return 'var(--color-text-secondary)';
  }
};

/**
 * Get background color for status badge
 * Works with both WIP and Serial statuses
 */
export const getStatusBgColor = (status: string): string => {
  switch (status) {
    case 'COMPLETED':
    case 'PASSED':
      return 'var(--color-bg-success)';
    case 'FAILED':
      return 'var(--color-bg-error)';
    case 'IN_PROGRESS':
      return 'var(--color-bg-info)';
    case 'CREATED':
      return 'var(--color-warning-bg)';
    default:
      return 'var(--color-bg-secondary)';
  }
};

/**
 * Get LOT status styling (for active LOT cards)
 */
export const getLotStatusStyle = (status: string) => ({
  backgroundColor: status === 'IN_PROGRESS' ? 'var(--color-bg-info)' : 'var(--color-warning-bg)',
  color: status === 'IN_PROGRESS' ? 'var(--color-info)' : 'var(--color-warning)',
});

// ============================================================================
// Hook Implementation
// ============================================================================

export const useLotSearch = (options: UseLotSearchOptions = {}): UseLotSearchReturn => {
  const { parseWipId = false, parseSerialNumber = false } = options;

  // Input state
  const [lotNumber, setLotNumber] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Selected LOT state
  const [lot, setLot] = useState<Lot | null>(null);

  // Loading/Error state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Active LOTs state
  const [activeLots, setActiveLots] = useState<Lot[]>([]);
  const [isLoadingLots, setIsLoadingLots] = useState(true);

  // Focus input on mount and load active LOTs
  useEffect(() => {
    inputRef.current?.focus();
    fetchActiveLots();
  }, []);

  /**
   * Parse LOT number from various input formats
   * - WIP ID: WIP-{LOT}-{SEQ} → {LOT}
   * - Serial: {LOT}-{SEQ} → {LOT}
   */
  const parseLotNumber = useCallback(
    (input: string): string => {
      let parsed = input.trim();

      // Parse WIP ID format: WIP-{LOT}-{SEQ}
      if (parseWipId && parsed.startsWith('WIP-')) {
        const parts = parsed.substring(4).split('-');
        if (parts.length >= 2) {
          // Join all parts except the last one (sequence number)
          parsed = parts.slice(0, -1).join('-');
        }
      }

      // Parse Serial number format: {LOT}-{SEQ}
      if (parseSerialNumber && !parsed.startsWith('WIP-')) {
        const serialMatch = parsed.match(/^(.+)-(\d{3,})$/);
        if (serialMatch) {
          parsed = serialMatch[1];
        }
      }

      return parsed;
    },
    [parseWipId, parseSerialNumber]
  );

  /**
   * Fetch active LOTs from API
   */
  const fetchActiveLots = useCallback(async () => {
    setIsLoadingLots(true);
    try {
      const response = await lotsApi.getActiveLots();
      setActiveLots(response);
    } catch (err) {
      console.error('Failed to load active LOTs:', err);
    } finally {
      setIsLoadingLots(false);
    }
  }, []);

  /**
   * Search for LOT by number
   * Returns the found LOT or null
   */
  const searchLot = useCallback(async (): Promise<Lot | null> => {
    if (!lotNumber.trim()) return null;

    setIsLoading(true);
    setError('');
    setLot(null);

    try {
      const parsedLotNumber = parseLotNumber(lotNumber);
      const lotData = await lotsApi.getLotByNumber(parsedLotNumber);
      setLot(lotData);
      return lotData;
    } catch (err: unknown) {
      setError(getErrorMessage(err, `LOT "${lotNumber}" not found`));
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [lotNumber, parseLotNumber]);

  /**
   * Reset search state
   */
  const resetSearch = useCallback(() => {
    setLot(null);
    setLotNumber('');
    setError('');
  }, []);

  return {
    // Input state
    lotNumber,
    setLotNumber,
    inputRef,

    // Selected LOT state
    lot,
    setLot,

    // Loading/Error state
    isLoading,
    error,
    setError,

    // Active LOTs
    activeLots,
    isLoadingLots,
    fetchActiveLots,

    // Actions
    searchLot,
    resetSearch,

    // Utilities
    parseLotNumber,
  };
};
