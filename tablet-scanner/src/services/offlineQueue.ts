/**
 * Offline Queue Service
 *
 * Stores pending operations when offline and syncs when connection restored
 * Uses IndexedDB via idb-keyval for persistence
 */
import { get, set, del, keys } from 'idb-keyval';
import type { ProcessStartRequest, ProcessCompleteRequest } from '@/types';

// Queue item types
interface QueueItemBase {
  id: string;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

interface StartQueueItem extends QueueItemBase {
  type: 'start';
  data: ProcessStartRequest;
}

interface CompleteQueueItem extends QueueItemBase {
  type: 'complete';
  data: ProcessCompleteRequest;
}

type QueueItem = StartQueueItem | CompleteQueueItem;

// Queue storage key prefix
const QUEUE_PREFIX = 'offline-queue-';

// Generate unique ID
const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Add item to offline queue
 */
export const addToQueue = async (
  type: 'start' | 'complete',
  data: ProcessStartRequest | ProcessCompleteRequest
): Promise<string> => {
  const id = generateId();
  const item: QueueItem = {
    id,
    type,
    data,
    timestamp: Date.now(),
    retryCount: 0,
    maxRetries: 5,
  } as QueueItem;

  await set(`${QUEUE_PREFIX}${id}`, item);
  console.log(`[OfflineQueue] Added item: ${id}, type: ${type}`);

  return id;
};

/**
 * Get all queued items
 */
export const getQueuedItems = async (): Promise<QueueItem[]> => {
  const allKeys = await keys();
  const queueKeys = allKeys.filter(
    (key) => typeof key === 'string' && key.startsWith(QUEUE_PREFIX)
  );

  const items: QueueItem[] = [];
  for (const key of queueKeys) {
    const item = await get<QueueItem>(key as string);
    if (item) {
      items.push(item);
    }
  }

  // Sort by timestamp (oldest first)
  return items.sort((a, b) => a.timestamp - b.timestamp);
};

/**
 * Get queue count
 */
export const getQueueCount = async (): Promise<number> => {
  const items = await getQueuedItems();
  return items.length;
};

/**
 * Remove item from queue
 */
export const removeFromQueue = async (id: string): Promise<void> => {
  await del(`${QUEUE_PREFIX}${id}`);
  console.log(`[OfflineQueue] Removed item: ${id}`);
};

/**
 * Update item retry count
 */
export const incrementRetryCount = async (id: string): Promise<boolean> => {
  const item = await get<QueueItem>(`${QUEUE_PREFIX}${id}`);
  if (!item) return false;

  item.retryCount += 1;

  if (item.retryCount >= item.maxRetries) {
    // Move to failed queue or remove
    await del(`${QUEUE_PREFIX}${id}`);
    console.log(`[OfflineQueue] Item ${id} exceeded max retries, removed`);
    return false;
  }

  await set(`${QUEUE_PREFIX}${id}`, item);
  return true;
};

/**
 * Process queue - called when online
 */
export const processQueue = async (
  onStart: (data: ProcessStartRequest) => Promise<boolean>,
  onComplete: (data: ProcessCompleteRequest) => Promise<boolean>,
  onProgress?: (current: number, total: number) => void
): Promise<{ success: number; failed: number }> => {
  const items = await getQueuedItems();
  let success = 0;
  let failed = 0;

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    onProgress?.(i + 1, items.length);

    try {
      let result = false;

      if (item.type === 'start') {
        result = await onStart(item.data as ProcessStartRequest);
      } else if (item.type === 'complete') {
        result = await onComplete(item.data as ProcessCompleteRequest);
      }

      if (result) {
        await removeFromQueue(item.id);
        success++;
      } else {
        const canRetry = await incrementRetryCount(item.id);
        if (!canRetry) failed++;
      }
    } catch (error) {
      console.error(`[OfflineQueue] Failed to process item ${item.id}:`, error);
      const canRetry = await incrementRetryCount(item.id);
      if (!canRetry) failed++;
    }
  }

  return { success, failed };
};

/**
 * Clear entire queue
 */
export const clearQueue = async (): Promise<void> => {
  const allKeys = await keys();
  const queueKeys = allKeys.filter(
    (key) => typeof key === 'string' && key.startsWith(QUEUE_PREFIX)
  );

  for (const key of queueKeys) {
    await del(key as string);
  }

  console.log(`[OfflineQueue] Cleared ${queueKeys.length} items`);
};

/**
 * Check if we're online
 */
export const isOnline = (): boolean => {
  return navigator.onLine;
};

/**
 * Online/Offline event listeners
 */
export const setupNetworkListeners = (
  onOnline: () => void,
  onOffline: () => void
): (() => void) => {
  window.addEventListener('online', onOnline);
  window.addEventListener('offline', onOffline);

  return () => {
    window.removeEventListener('online', onOnline);
    window.removeEventListener('offline', onOffline);
  };
};
