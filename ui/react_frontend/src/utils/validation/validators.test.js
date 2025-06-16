/**
 * Unit tests for validation utilities in validators.js
 */

import {
  validateString,
  validateEmail,
  validateCredential,
  validatePassword,
  validateNumber,
  validateArray,
  validateURL
} from './validators';

describe('validateString', () => {
  it('validates required and optional', () => {
    expect(validateString('', { required: true })).toEqual({ valid: false, error: expect.stringMatching(/required/i) });
    expect(validateString('', { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates min/max length', () => {
    expect(validateString('abc', { minLength: 5 })).toEqual({ valid: false, error: expect.stringMatching(/at least 5/) });
    expect(validateString('abcdef', { maxLength: 3 })).toEqual({ valid: false, error: expect.stringMatching(/no more than 3/) });
    expect(validateString('abc', { minLength: 2, maxLength: 5 })).toEqual({ valid: true, error: null });
  });
  it('validates type is string', () => {
    expect(validateString(123, { required: true })).toEqual({ valid: false, error: expect.stringMatching(/must be a string/) });
  });
  it('trims by default', () => {
    expect(validateString('   abc  ', { minLength: 3 })).toEqual({ valid: true, error: null });
    expect(validateString('   ', { required: true })).toEqual({ valid: false, error: expect.any(String) });
    expect(validateString('   a ', { trim: false, minLength: 3 })).toEqual({ valid: false, error: expect.any(String) });
  });
});

describe('validateEmail', () => {
  it('validates required and optional', () => {
    expect(validateEmail('', { required: true })).toEqual({ valid: false, error: expect.stringMatching(/required/i) });
    expect(validateEmail('', { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates type is string', () => {
    expect(validateEmail({}, { required: true })).toEqual({ valid: false, error: expect.stringMatching(/must be a string/) });
  });
  it('validates email regex', () => {
    expect(validateEmail('foo@bar.com')).toEqual({ valid: true, error: null });
    expect(validateEmail('foo')).toEqual({ valid: false, error: expect.stringMatching(/format/) });
    expect(validateEmail('foo@bar')).toEqual({ valid: false, error: expect.any(String) });
    expect(validateEmail('foo@bar.x')).toEqual({ valid: false, error: expect.any(String) });
  });
});

describe('validateCredential / validatePassword', () => {
  it('validates required and optional', () => {
    expect(validateCredential('', { required: true })).toEqual({ valid: false, error: expect.any(String) });
    expect(validateCredential('', { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates min/max length', () => {
    expect(validateCredential('abc', { minLength: 5 })).toEqual({ valid: false, error: expect.stringMatching(/at least 5/) });
    expect(validateCredential('abcdefg123', { maxLength: 5 })).toEqual({ valid: false, error: expect.stringMatching(/no more than 5/) });
    expect(validateCredential('abcdefgh', { minLength: 8 })).toEqual({ valid: true, error: null });
  });
  it('validates lowercase, uppercase, number, special', () => {
    expect(validateCredential('ALLUPPER123!', { requireLowercase: true })).toEqual({ valid: false, error: expect.stringMatching(/lowercase/) });
    expect(validateCredential('alllower123!', { requireUppercase: true })).toEqual({ valid: false, error: expect.stringMatching(/uppercase/) });
    expect(validateCredential('Abcdefgh!', { requireNumber: true })).toEqual({ valid: false, error: expect.stringMatching(/number/) });
    expect(validateCredential('Abcdefgh1', { requireSpecial: true })).toEqual({ valid: false, error: expect.stringMatching(/special/) });
    expect(validateCredential('Abcd123!', { requireLowercase: true, requireUppercase: true, requireNumber: true, requireSpecial: true })).toEqual({ valid: true, error: null });
  });
  it('validates type is string', () => {
    expect(validateCredential(12345678)).toEqual({ valid: false, error: expect.stringMatching(/must be a string/) });
  });
  it('validatePassword alias works', () => {
    expect(validatePassword('abcdefgh')).toEqual(validateCredential('abcdefgh'));
  });
});

describe('validateNumber', () => {
  it('validates required and optional', () => {
    expect(validateNumber('', { required: true })).toEqual({ valid: false, error: expect.any(String) });
    expect(validateNumber('', { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates type and string conversion', () => {
    expect(validateNumber('42')).toEqual({ valid: true, error: null });
    expect(validateNumber('abc')).toEqual({ valid: false, error: expect.stringMatching(/must be a number/) });
    expect(validateNumber(42)).toEqual({ valid: true, error: null });
  });
  it('validates integer', () => {
    expect(validateNumber(4.5, { integer: true })).toEqual({ valid: false, error: expect.stringMatching(/integer/) });
    expect(validateNumber(5, { integer: true })).toEqual({ valid: true, error: null });
  });
  it('validates min/max', () => {
    expect(validateNumber(1, { min: 3 })).toEqual({ valid: false, error: expect.stringMatching(/at least 3/) });
    expect(validateNumber(10, { max: 5 })).toEqual({ valid: false, error: expect.stringMatching(/at most 5/) });
    expect(validateNumber(5, { min: 3, max: 7 })).toEqual({ valid: true, error: null });
  });
});

describe('validateArray', () => {
  it('validates required and optional', () => {
    expect(validateArray(undefined, { required: true })).toEqual({ valid: false, error: expect.stringMatching(/required/) });
    expect(validateArray(undefined, { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates type is array', () => {
    expect(validateArray({}, {})).toEqual({ valid: false, error: expect.stringMatching(/array/) });
    expect(validateArray([], {})).toEqual({ valid: true, error: null });
  });
  it('validates min/max length', () => {
    expect(validateArray([1], { minLength: 2 })).toEqual({ valid: false, error: expect.stringMatching(/at least 2/) });
    expect(validateArray([1, 2, 3], { maxLength: 2 })).toEqual({ valid: false, error: expect.stringMatching(/no more than 2/) });
    expect(validateArray([1, 2], { minLength: 2, maxLength: 2 })).toEqual({ valid: true, error: null });
  });
  it('validates itemValidator', () => {
    const itemValidator = v => typeof v === 'number' ? { valid: true, error: null } : { valid: false, error: 'not num' };
    expect(validateArray([1, 2, 3], { itemValidator })).toEqual({ valid: true, error: null });
    expect(validateArray([1, 'a', 3], { itemValidator })).toEqual({ valid: false, error: expect.stringMatching(/index 1.*not num/) });
  });
});

describe('validateURL', () => {
  it('validates required and optional', () => {
    expect(validateURL('', { required: true })).toEqual({ valid: false, error: expect.stringMatching(/required/) });
    expect(validateURL('', { required: false })).toEqual({ valid: true, error: null });
  });
  it('validates type is string', () => {
    expect(validateURL(1234)).toEqual({ valid: false, error: expect.stringMatching(/must be a string/) });
  });
  it('validates valid http/https URLs', () => {
    expect(validateURL('https://foo.com')).toEqual({ valid: true, error: null });
    expect(validateURL('http://foo.com')).toEqual({ valid: true, error: null });
  });
  it('rejects URLs without protocol if required', () => {
    expect(validateURL('foo.com')).toEqual({ valid: false, error: expect.stringMatching(/format/) });
    expect(validateURL('ftp://foo.com')).toEqual({ valid: false, error: expect.stringMatching(/http/) });
  });
  it('allows URLs without protocol if not required', () => {
    expect(validateURL('https://foo.com', { requireProtocol: false })).toEqual({ valid: true, error: null });
    expect(validateURL('foo.com', { requireProtocol: false })).toEqual({ valid: false, error: expect.stringMatching(/format/) });
  });
});