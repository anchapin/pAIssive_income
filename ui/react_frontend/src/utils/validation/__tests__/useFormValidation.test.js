import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import useFormValidation from '../useFormValidation';

describe('useFormValidation', () => {
  const mockValidationSchema = {
    name: (value) => {
      if (!value) return { valid: false, error: 'Name is required' };
      if (value.length < 2) return { valid: false, error: 'Name too short' };
      return { valid: true, error: null };
    },
    email: (value) => {
      if (!value) return { valid: false, error: 'Email is required' };
      if (!value.includes('@')) return { valid: false, error: 'Invalid email' };
      return { valid: true, error: null };
    }
  };

  const initialValues = {
    name: '',
    email: ''
  };

  it('should initialize with validation errors for required fields', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));

    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({
      name: 'Name is required',
      email: 'Email is required'
    });
    expect(result.current.touched).toEqual({});
    expect(result.current.dirty).toBe(false);
    expect(result.current.isValid).toBe(false);
  });

  it('should handle field changes', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));

    act(() => {
      result.current.handleChange({ target: { name: 'name', value: 'John' } });
    });

    expect(result.current.values.name).toBe('John');
    expect(result.current.dirty).toBe(true);
    expect(result.current.errors.name).toBeNull();
  });

  it('should validate fields on blur', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));

    act(() => {
      result.current.handleBlur({ target: { name: 'name', value: '' } });
    });

    expect(result.current.touched.name).toBe(true);
    expect(result.current.errors.name).toBe('Name is required');
  });

  it('should validate on submit and prevent submission if invalid', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));
    let submitPrevented = false;

    act(() => {
      result.current.handleSubmit((values) => {
        // This should not be called
        throw new Error('Submit should not be called with invalid form');
      })({
        preventDefault: () => {
          submitPrevented = true;
        }
      });
    });

    expect(submitPrevented).toBe(true);
    expect(result.current.errors.name).toBe('Name is required');
    expect(result.current.errors.email).toBe('Email is required');
    expect(result.current.touched).toEqual({ name: true, email: true });
  });

  it('should allow submission when form is valid', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));
    let submittedValues = null;

    act(() => {
      // Fill out form with valid values
      result.current.handleChange({ target: { name: 'name', value: 'John' } });
      result.current.handleChange({ target: { name: 'email', value: 'john@example.com' } });
    });

    act(() => {
      result.current.handleSubmit((values) => {
        submittedValues = values;
      })({
        preventDefault: () => {}
      });
    });

    expect(submittedValues).toEqual({
      name: 'John',
      email: 'john@example.com'
    });
    expect(result.current.isValid).toBe(true);
    expect(result.current.errors).toEqual({});
  });

  it('should reset form state', () => {
    const { result } = renderHook(() => useFormValidation(initialValues, mockValidationSchema));

    act(() => {
      result.current.handleChange({ target: { name: 'name', value: 'John' } });
      result.current.handleChange({ target: { name: 'email', value: 'john@example.com' } });
      result.current.handleBlur({ target: { name: 'name', value: 'John' } });
    });

    act(() => {
      result.current.resetForm();
    });

    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({
      name: 'Name is required',
      email: 'Email is required'
    });
    expect(result.current.touched).toEqual({});
    expect(result.current.dirty).toBe(false);
  });
});
