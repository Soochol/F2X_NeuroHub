/**
 * Tests for useFormState hook
 */

import { renderHook, act } from '@testing-library/react';
import { useFormState } from '../useFormState';

interface TestForm {
  name: string;
  email: string;
  age: number;
  isActive: boolean;
}

describe('useFormState', () => {
  const initialValues: TestForm = {
    name: '',
    email: '',
    age: 0,
    isActive: true,
  };

  it('should initialize with provided initial values', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    expect(result.current.formData).toEqual(initialValues);
  });

  it('should update single field with setField', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    act(() => {
      result.current.setField('name', 'John Doe');
    });

    expect(result.current.formData.name).toBe('John Doe');
    expect(result.current.formData.email).toBe('');
    expect(result.current.formData.age).toBe(0);
  });

  it('should update different field types correctly', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    act(() => {
      result.current.setField('name', 'Jane');
      result.current.setField('email', 'jane@example.com');
      result.current.setField('age', 25);
      result.current.setField('isActive', false);
    });

    expect(result.current.formData).toEqual({
      name: 'Jane',
      email: 'jane@example.com',
      age: 25,
      isActive: false,
    });
  });

  it('should reset form to initial values', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    act(() => {
      result.current.setField('name', 'Changed Name');
      result.current.setField('email', 'changed@email.com');
    });

    expect(result.current.formData.name).toBe('Changed Name');

    act(() => {
      result.current.resetForm();
    });

    expect(result.current.formData).toEqual(initialValues);
  });

  it('should allow setting entire form data with setFormData', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    const newFormData: TestForm = {
      name: 'New User',
      email: 'new@user.com',
      age: 30,
      isActive: false,
    };

    act(() => {
      result.current.setFormData(newFormData);
    });

    expect(result.current.formData).toEqual(newFormData);
  });

  it('should support functional updates with setFormData', () => {
    const { result } = renderHook(() => useFormState(initialValues));

    act(() => {
      result.current.setFormData(prev => ({
        ...prev,
        name: 'Functional Update',
        age: prev.age + 10,
      }));
    });

    expect(result.current.formData.name).toBe('Functional Update');
    expect(result.current.formData.age).toBe(10);
  });

  it('should maintain referential equality of setField callback', () => {
    const { result, rerender } = renderHook(() => useFormState(initialValues));

    const setFieldRef = result.current.setField;

    rerender();

    expect(result.current.setField).toBe(setFieldRef);
  });

  it('should handle nested objects', () => {
    interface NestedForm {
      user: {
        name: string;
        profile: {
          bio: string;
        };
      };
    }

    const nestedInitial: NestedForm = {
      user: {
        name: 'Initial',
        profile: {
          bio: 'Initial bio',
        },
      },
    };

    const { result } = renderHook(() => useFormState(nestedInitial));

    act(() => {
      result.current.setField('user', {
        name: 'Updated',
        profile: { bio: 'Updated bio' },
      });
    });

    expect(result.current.formData.user.name).toBe('Updated');
    expect(result.current.formData.user.profile.bio).toBe('Updated bio');
  });

  it('should handle arrays', () => {
    interface ArrayForm {
      items: string[];
      tags: number[];
    }

    const arrayInitial: ArrayForm = {
      items: ['a', 'b'],
      tags: [1, 2, 3],
    };

    const { result } = renderHook(() => useFormState(arrayInitial));

    act(() => {
      result.current.setField('items', [...result.current.formData.items, 'c']);
    });

    expect(result.current.formData.items).toEqual(['a', 'b', 'c']);
    expect(result.current.formData.tags).toEqual([1, 2, 3]);
  });
});
