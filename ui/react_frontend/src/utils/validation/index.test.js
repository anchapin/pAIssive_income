/**
 * Integration tests for validationSchemas in index.js
 */

import { validationSchemas } from './index';

describe('validationSchemas.login', () => {
  const schema = validationSchemas.login;
  it('validates correct data', () => {
    expect(schema.username('validuser')).toEqual({ valid: true, error: null });
    expect(schema.credentials('abcdef')).toEqual({ valid: true, error: null });
  });
  it('catches invalid username and credentials', () => {
    expect(schema.username('')).toEqual({ valid: false, error: expect.stringMatching(/required|at least/i) });
    expect(schema.username('ab')).toEqual({ valid: false, error: expect.stringMatching(/at least 3/) });
    expect(schema.credentials('123')).toEqual({ valid: false, error: expect.stringMatching(/at least 6/) });
  });
});

describe('validationSchemas.register', () => {
  const schema = validationSchemas.register;
  it('validates correct data', () => {
    expect(schema.username('valid')).toEqual({ valid: true, error: null });
    expect(schema.email('foo@bar.com')).toEqual({ valid: true, error: null });
    expect(schema.authCredential('abc12345')).toEqual({ valid: true, error: null });
    expect(schema.confirmCredential('abc12345', { authCredential: 'abc12345' })).toEqual({ valid: true, error: null });
    expect(schema.name('John')).toEqual({ valid: true, error: null });
  });
  it('catches invalid registration fields', () => {
    expect(schema.username('')).toEqual({ valid: false, error: expect.stringMatching(/required/) });
    expect(schema.email('bad')).toEqual({ valid: false, error: expect.stringMatching(/format/) });
    expect(schema.authCredential('abc')).toEqual({ valid: false, error: expect.stringMatching(/at least 8/) });
    expect(schema.confirmCredential('abc', { authCredential: 'xyz' })).toEqual({ valid: false, error: expect.stringMatching(/match/) });
    expect(schema.name('')).toEqual({ valid: false, error: expect.stringMatching(/required/) });
  });
});

describe('validationSchemas.profile', () => {
  const schema = validationSchemas.profile;
  it('validates correct data', () => {
    expect(schema.email('foo@bar.com')).toEqual({ valid: true, error: null });
    expect(schema.name('Jane')).toEqual({ valid: true, error: null });
  });
  it('catches invalid profile fields', () => {
    expect(schema.email('bar')).toEqual({ valid: false, error: expect.stringMatching(/format/) });
    expect(schema.name('')).toEqual({ valid: false, error: expect.stringMatching(/required/) });
  });
});

describe('validationSchemas.solution', () => {
  const schema = validationSchemas.solution;
  it('validates correct data', () => {
    expect(schema.nicheId(1)).toEqual({ valid: true, error: null });
    expect(schema.templateId(2)).toEqual({ valid: true, error: null });
  });
  it('catches invalid solution fields', () => {
    expect(schema.nicheId('foo')).toEqual({ valid: false, error: expect.any(String) });
    expect(schema.templateId()).toEqual({ valid: false, error: expect.any(String) });
  });
});

describe('validationSchemas.marketingCampaign', () => {
  const schema = validationSchemas.marketingCampaign;
  it('validates correct data', () => {
    expect(schema.solutionId(1)).toEqual({ valid: true, error: null });
    expect(schema.audienceIds([1, 2])).toEqual({ valid: true, error: null });
    expect(schema.channelIds([3, 4])).toEqual({ valid: true, error: null });
  });
  it('catches invalid marketing campaign fields', () => {
    expect(schema.solutionId('')).toEqual({ valid: false, error: expect.any(String) });
    expect(schema.audienceIds([])).toEqual({ valid: false, error: expect.stringMatching(/at least 1/) });
    expect(schema.channelIds(undefined)).toEqual({ valid: false, error: expect.any(String) });
  });
});