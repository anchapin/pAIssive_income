/**
 * Unit tests for useFormValidation hook
 */
import { act, renderHook } from '@testing-library/react';
import useFormValidation from './useFormValidation';

const requiredString = (value) =>
  value && value.length > 2
    ? { valid: true, error: null }
    : { valid: false, error: 'Too short' };

const alwaysValid = () => ({ valid: true, error: null });

const schema = {
  foo: requiredString,
  bar: alwaysValid
};

describe('useFormValidation', () => {
  it('initializes values, errors, touched, dirty, isValid', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    expect(result.current.values).toEqual({ foo: '', bar: '' });
    expect(result.current.errors).toEqual({ foo: 'Too short' });
    expect(result.current.touched).toEqual({});
    expect(result.current.dirty).toBe(false);
    expect(result.current.isValid).toBe(false);
  });

  it('handleChange updates value, dirty, and errors on touched', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    act(() => {
      result.current.handleBlur({ target: { name: 'foo', value: '' } });
    });
    expect(result.current.touched.foo).toBe(true);

    act(() => {
      result.current.handleChange({ target: { name: 'foo', value: 'abc', type: 'text' } });
    });
    expect(result.current.values.foo).toBe('abc');
    expect(result.current.dirty).toBe(true);
    expect(result.current.errors.foo).toBe(null);
  });

  it('handleBlur marks touched and updates error', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    act(() => {
      result.current.handleBlur({ target: { name: 'foo', value: '' } });
    });
    expect(result.current.touched.foo).toBe(true);
    expect(result.current.errors.foo).toBe('Too short');
  });

  it('setFieldValue programmatically sets value and error', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    act(() => {
      result.current.handleBlur({ target: { name: 'foo', value: '' } });
    });
    act(() => {
      result.current.setFieldValue('foo', 'abc');
    });
    expect(result.current.values.foo).toBe('abc');
    expect(result.current.errors.foo).toBe(null);
  });

  it('resetForm restores initial state', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    act(() => {
      result.current.setFieldValue('foo', 'hello');
      result.current.handleBlur({ target: { name: 'foo', value: 'hello' } });
    });
    act(() => {
      result.current.resetForm();
    });
    expect(result.current.values.foo).toBe('');
    expect(result.current.dirty).toBe(false);
    expect(result.current.touched).toEqual({});
  });

  it('handleSubmit calls onSubmit if valid and sets touched', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    const onSubmit = jest.fn();
    // Make the field valid
    act(() => {
      result.current.setFieldValue('foo', 'abc');
    });
    act(() => {
      result.current.handleBlur({ target: { name: 'foo', value: 'abc' } });
    });
    // Simulate submit event
    const event = { preventDefault: jest.fn() };
    act(() => {
      result.current.handleSubmit(onSubmit)(event);
    });
    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ foo: 'abc', bar: '' }));
    expect(result.current.touched.foo).toBe(true);
    expect(result.current.isValid).toBe(true);
  });

  it('handleSubmit does not call onSubmit if invalid', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    const onSubmit = jest.fn();
    const event = { preventDefault: jest.fn() };
    act(() => {
      result.current.handleSubmit(onSubmit)(event);
    });
    expect(onSubmit).not.toHaveBeenCalled();
    expect(result.current.touched.foo).toBe(true);
    expect(result.current.isValid).toBe(false);
  });

  it('validateForm returns correct validity', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    expect(result.current.validateForm()).toBe(false);
    act(() => {
      result.current.setFieldValue('foo', 'abcd');
    });
    expect(result.current.validateForm()).toBe(true);
  });

  it('setValues directly sets all values', () => {
    const { result } = renderHook(() =>
      useFormValidation({ foo: '', bar: '' }, schema)
    );
    act(() => {
      result.current.setValues({ foo: 'abc', bar: 'b' });
    });
    expect(result.current.values).toEqual({ foo: 'abc', bar: 'b' });
  });
});