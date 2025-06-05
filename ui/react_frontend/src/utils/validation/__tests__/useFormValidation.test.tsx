import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useFormValidation from '../useFormValidation';
import { validateString, validateEmail, validateNumber } from '../validators';

// Types for form values and return type
interface FormValues {
  name?: string;
  email?: string;
  age?: string;
  accepted?: boolean;
  password?: string;
  confirmPassword?: string;
}

interface ValidationResult {
  valid: boolean;
  error: string | null;
}

type ValidationSchema<T> = {
  [K in keyof T]?: (value: T[K], allValues?: T) => ValidationResult;
};

describe('useFormValidation hook', () => {
  const initialValues: FormValues = {
    name: '',
    email: '',
    age: ''
  };
  const validationSchema: ValidationSchema<FormValues> = {
    name: (value?: string) => validateString(value || '', { required: true, minLength: 2 }),
    email: (value?: string) => validateEmail(value || '', { required: true }),
    age: (value?: string) => validateNumber(value || '', { required: true, min: 18 })
  };

  it('should initialize with initial values and validation errors', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({
      name: 'This field is required',
      email: 'Email is required',
      age: 'This field is required'
    });
    expect(result.current.touched).toEqual({});
    expect(result.current.dirty).toBe(false);
    expect(result.current.isValid).toBe(false);
  });

  it('should handle field changes correctly', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    act(() => {
      result.current.handleChange({ target: { name: 'name', value: 'John' } } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.values.name).toBe('John');
    expect(result.current.dirty).toBe(true);
    expect(result.current.errors.name).toBeUndefined();
  });

  it('should validate fields on blur', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    act(() => {
      result.current.handleBlur({ target: { name: 'name', value: 'J' } } as React.FocusEvent<HTMLInputElement>);
    });

    expect(result.current.errors.name).toBe('This field is required');
    expect(result.current.touched.name).toBe(true);
  });
  it('should validate form on submit', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));
    const onSubmit = vi.fn();

    act(() => {
      const mockFormEvent = {
        preventDefault: vi.fn(),
        nativeEvent: {} as Event,
        currentTarget: document.createElement('form'),
        target: document.createElement('form'),
        bubbles: true,
        cancelable: true,
        defaultPrevented: false,
        eventPhase: 0,
        isTrusted: true,
        timeStamp: Date.now(),
        type: 'submit'
      } as React.FormEvent;
      result.current.handleSubmit(onSubmit)(mockFormEvent);
    });

    expect(result.current.errors.name).toBe('This field is required');
    expect(result.current.errors.email).toBe('Email is required');
    expect(result.current.errors.age).toBe('This field is required');
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should call onSubmit when form is valid', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));
    const onSubmit = vi.fn();
    const validData = {
      name: 'John Doe',
      email: 'john@example.com',
      age: '25'
    };

    act(() => {
      // Set values one by one to trigger proper validation
      result.current.handleChange({ target: { name: 'name', value: 'John Doe' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'email', value: 'john@example.com' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'age', value: '25' } } as React.ChangeEvent<HTMLInputElement>);
    });

    act(() => {
      const mockFormEvent = {
        preventDefault: vi.fn(),
        nativeEvent: {} as Event,
        currentTarget: document.createElement('form'),
        target: document.createElement('form'),
        bubbles: true,
        cancelable: true,
        defaultPrevented: false,
        eventPhase: 0,
        isTrusted: true,
        timeStamp: Date.now(),
        type: 'submit'
      } as React.FormEvent;
      result.current.handleSubmit(onSubmit)(mockFormEvent);
    });

    expect(onSubmit).toHaveBeenCalledWith(validData);
    expect(result.current.isValid).toBe(true);
  });

  it('should handle setFieldValue correctly', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    act(() => {
      result.current.setFieldValue('name', 'John');
      result.current.handleBlur({ target: { name: 'name', value: 'John' } } as React.FocusEvent<HTMLInputElement>);
    });

    expect(result.current.values.name).toBe('John');
    expect(result.current.errors.name).toBeUndefined();
    expect(result.current.touched.name).toBe(true);
  });

  it('should reset form state correctly', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    act(() => {
      result.current.handleChange({ target: { name: 'name', value: 'John' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'email', value: 'john@example.com' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'age', value: '25' } } as React.ChangeEvent<HTMLInputElement>);
    });

    act(() => {
      result.current.resetForm();
    });

    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({
      name: 'This field is required',
      email: 'Email is required',
      age: 'This field is required'
    });
    expect(result.current.touched).toEqual({});
    expect(result.current.dirty).toBe(false);
  });

  it('should track form validity correctly', () => {
    const { result } = renderHook(() => useFormValidation<FormValues>(initialValues, validationSchema));

    expect(result.current.isValid).toBe(false);

    act(() => {
      result.current.handleChange({ target: { name: 'name', value: 'John' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'email', value: 'john@example.com' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'age', value: '25' } } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.isValid).toBe(true);
  });

  it('should validate checkbox inputs correctly', () => {
    const checkboxValidationSchema: ValidationSchema<{ accepted?: boolean }> = {
      accepted: (value?: boolean) => value ? { valid: true, error: null } : { valid: false, error: 'Must be accepted' }
    };

    const { result } = renderHook(() => useFormValidation<FormValues>({ accepted: false }, checkboxValidationSchema));

    act(() => {
      result.current.handleChange({ target: { name: 'accepted', type: 'checkbox', checked: true } } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.values.accepted).toBe(true);
    expect(result.current.errors.accepted).toBeUndefined();
  });

  it('should validate dependent fields correctly', () => {
    interface PasswordFormValues {
      password?: string;
      confirmPassword?: string;
    }

    const dependentValidationSchema: ValidationSchema<PasswordFormValues> = {
      password: (value?: string) => validateString(value || '', { required: true, minLength: 6 }),
      confirmPassword: (value?: string, allValues?: PasswordFormValues) => {
        const baseValidation = validateString(value || '', { required: true });
        if (!baseValidation.valid) return baseValidation;
        return value === allValues?.password
          ? { valid: true, error: null }
          : { valid: false, error: 'Passwords must match' };
      }
    };

    const { result } = renderHook(() => 
      useFormValidation<FormValues>({ password: '', confirmPassword: '' }, dependentValidationSchema)
    );

    act(() => {
      result.current.handleChange({ target: { name: 'password', value: 'secret123' } } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({ target: { name: 'confirmPassword', value: 'secret124' } } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.errors.confirmPassword).toBe('Passwords must match');

    act(() => {
      result.current.handleChange({ target: { name: 'confirmPassword', value: 'secret123' } } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.errors.confirmPassword).toBeUndefined();
  });
});
