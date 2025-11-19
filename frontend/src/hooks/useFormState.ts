/**
 * Hook for managing form state with reset and field update capabilities
 */

import { useState, useCallback } from 'react';

interface UseFormStateReturn<T> {
  formData: T;
  setFormData: React.Dispatch<React.SetStateAction<T>>;
  setField: <K extends keyof T>(key: K, value: T[K]) => void;
  resetForm: () => void;
}

export function useFormState<T extends object>(initialValues: T): UseFormStateReturn<T> {
  const [formData, setFormData] = useState<T>(initialValues);

  const setField = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData(initialValues);
  }, [initialValues]);

  return {
    formData,
    setFormData,
    setField,
    resetForm,
  };
}

export default useFormState;
