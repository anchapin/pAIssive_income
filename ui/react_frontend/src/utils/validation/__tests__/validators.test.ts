import { describe, expect, test } from 'vitest';
import { validateString, validateEmail, type ValidationResult } from '../validators';

describe('validateString', () => {
  test('handles required fields correctly', () => {
    expect(validateString('', { required: true })).toEqual<ValidationResult>({
      valid: false,
      error: 'This field is required'
    });
    expect(validateString('test', { required: true })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('handles optional fields correctly', () => {
    expect(validateString('', { required: false })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
    expect(validateString(undefined, { required: false })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('validates string type', () => {
    expect(validateString(123)).toEqual<ValidationResult>({
      valid: false,
      error: 'Value must be a string'
    });
  });

  test('validates minimum length', () => {
    expect(validateString('ab', { minLength: 3 })).toEqual<ValidationResult>({
      valid: false,
      error: 'Must be at least 3 characters long'
    });
    expect(validateString('abc', { minLength: 3 })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('validates maximum length', () => {
    expect(validateString('abcd', { maxLength: 3 })).toEqual<ValidationResult>({
      valid: false,
      error: 'Must be no more than 3 characters long'
    });
    expect(validateString('abc', { maxLength: 3 })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });
});

describe('validateEmail', () => {
  test('handles required fields correctly', () => {
    expect(validateEmail('', { required: true })).toEqual<ValidationResult>({
      valid: false,
      error: 'Email is required'
    });
    expect(validateEmail('test@example.com', { required: true })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('handles optional fields correctly', () => {
    expect(validateEmail('', { required: false })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
    expect(validateEmail(undefined, { required: false })).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('validates email type', () => {
    expect(validateEmail(123)).toEqual<ValidationResult>({
      valid: false,
      error: 'Email must be a string'
    });
  });

  test('validates email format', () => {
    expect(validateEmail('notanemail')).toEqual<ValidationResult>({
      valid: false,
      error: 'Invalid email format'
    });
    expect(validateEmail('test@example')).toEqual<ValidationResult>({
      valid: false,
      error: 'Invalid email format'
    });
    expect(validateEmail('test@example.com')).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });

  test('validates complex email addresses', () => {
    expect(validateEmail('user.name+tag@example.co.uk')).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
    expect(validateEmail('user.name@subdomain.example.com')).toEqual<ValidationResult>({
      valid: true,
      error: null
    });
  });
});
