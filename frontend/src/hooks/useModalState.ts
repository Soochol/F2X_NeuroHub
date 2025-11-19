/**
 * Hook for managing modal open/close state with optional editing item
 */

import { useState, useCallback } from 'react';

interface UseModalStateReturn<T> {
  isOpen: boolean;
  editingItem: T | null;
  open: (item?: T) => void;
  close: () => void;
}

export function useModalState<T>(): UseModalStateReturn<T> {
  const [isOpen, setIsOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<T | null>(null);

  const open = useCallback((item?: T) => {
    setEditingItem(item || null);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setEditingItem(null);
  }, []);

  return {
    isOpen,
    editingItem,
    open,
    close,
  };
}

export default useModalState;
