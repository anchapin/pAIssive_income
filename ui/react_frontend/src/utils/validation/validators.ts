/**
 * Client-side validation utilities
 *
 * These validation functions mirror the server-side validation to ensure
 * consistent validation behavior across the application.
 */

// Type for validation result
export type ValidationResult = {
  valid: boolean;
  error: string | null;
}

// Type for validation options
interface BaseValidationOptions {
  required?: boolean;
}

interface StringValidationOptions extends BaseValidationOptions {
  minLength?: number;
  maxLength?: number;
  trim?: boolean;
}

interface EmailValidationOptions extends BaseValidationOptions {}

interface CredentialValidationOptions extends BaseValidationOptions {
  minLength?: number;
  maxLength?: number;
  requireLowercase?: boolean;
  requireUppercase?: boolean;
  requireNumber?: boolean;
  requireSpecial?: boolean;
}

interface NumberValidationOptions extends BaseValidationOptions {
  min?: number;
  max?: number;
  integer?: boolean;
}

interface ArrayValidationOptions extends BaseValidationOptions {
  minLength?: number;
  maxLength?: number;
  itemValidator?: (item: any) => ValidationResult;
}

interface URLValidationOptions extends BaseValidationOptions {
  requireProtocol?: boolean;
}

/**
 * Validate a string value
 * @param value - The string to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateString = (
  value: any,
  {
    minLength,
    maxLength,
    required = false,
    trim = true
  }: StringValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null || value === '')) {
    return { valid: false, error: 'This field is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null || value === '')) {
    return { valid: true, error: null };
  }

  // Check if value is a string
  if (typeof value !== 'string') {
    return { valid: false, error: 'Value must be a string' };
  }

  const processedValue = trim ? value.trim() : value;

  // Check minimum length
  if (minLength !== undefined && processedValue.length < minLength) {
    return {
      valid: false,
      error: `Must be at least ${minLength} characters long`
    };
  }

  // Check maximum length
  if (maxLength !== undefined && processedValue.length > maxLength) {
    return {
      valid: false,
      error: `Must be no more than ${maxLength} characters long`
    };
  }

  return { valid: true, error: null };
};

/**
 * Validate an email address
 * @param value - The email address to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateEmail = (
  value: any,
  { required = false }: EmailValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null || value === '')) {
    return { valid: false, error: 'Email is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null || value === '')) {
    return { valid: true, error: null };
  }

  // Check if value is a string
  if (typeof value !== 'string') {
    return { valid: false, error: 'Email must be a string' };
  }

  // Use regex to validate email format
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(value)) {
    return { valid: false, error: 'Invalid email format' };
  }

  return { valid: true, error: null };
};

/**
 * Validate an authentication credential
 * @param value - The credential to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateCredential = (
  value: any,
  {
    required = true,
    minLength = 8,
    maxLength = 100,
    requireLowercase = false,
    requireUppercase = false,
    requireNumber = false,
    requireSpecial = false
  }: CredentialValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null || value === '')) {
    return { valid: false, error: 'Authentication credential is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null || value === '')) {
    return { valid: true, error: null };
  }

  // Check if value is a string
  if (typeof value !== 'string') {
    return { valid: false, error: 'Credential must be a string' };
  }

  // Check length
  if (value.length < minLength) {
    return {
      valid: false,
      error: `Must be at least ${minLength} characters long`
    };
  }

  if (value.length > maxLength) {
    return {
      valid: false,
      error: `Must be no more than ${maxLength} characters long`
    };
  }

  // Check for lowercase letter
  if (requireLowercase && !/[a-z]/.test(value)) {
    return {
      valid: false,
      error: 'Must include at least one lowercase letter'
    };
  }

  // Check for uppercase letter
  if (requireUppercase && !/[A-Z]/.test(value)) {
    return {
      valid: false,
      error: 'Must include at least one uppercase letter'
    };
  }

  // Check for number
  if (requireNumber && !/[0-9]/.test(value)) {
    return {
      valid: false,
      error: 'Must include at least one number'
    };
  }

  // Check for special character
  if (requireSpecial && !/[^A-Za-z0-9]/.test(value)) {
    return {
      valid: false,
      error: 'Must include at least one special character'
    };
  }

  return { valid: true, error: null };
};

// For backward compatibility, export the old function name as an alias to the new function
export const validatePassword = validateCredential;

/**
 * Validate a number
 * @param value - The number to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateNumber = (
  value: any,
  {
    required = false,
    min,
    max,
    integer = false
  }: NumberValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null || value === '')) {
    return { valid: false, error: 'This field is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null || value === '')) {
    return { valid: true, error: null };
  }

  // Convert to number if it's a string
  if (typeof value === 'string') {
    value = Number(value);
  }

  // Check if value is a number
  if (typeof value !== 'number' || isNaN(value)) {
    return { valid: false, error: 'Value must be a number' };
  }

  // Check for integer if required
  if (integer && !Number.isInteger(value)) {
    return { valid: false, error: 'Value must be an integer' };
  }

  // Check minimum value
  if (min !== undefined && value < min) {
    return { valid: false, error: `Value must be at least ${min}` };
  }

  // Check maximum value
  if (max !== undefined && value > max) {
    return { valid: false, error: `Value must be at most ${max}` };
  }

  return { valid: true, error: null };
};

/**
 * Validate a list/array
 * @param value - The array to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateArray = (
  value: any,
  {
    required = false,
    minLength,
    maxLength,
    itemValidator
  }: ArrayValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null)) {
    return { valid: false, error: 'This field is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null)) {
    return { valid: true, error: null };
  }

  // Check if value is an array
  if (!Array.isArray(value)) {
    return { valid: false, error: 'Value must be an array' };
  }

  // Check minimum length
  if (minLength !== undefined && value.length < minLength) {
    return {
      valid: false,
      error: `Must have at least ${minLength} items`
    };
  }

  // Check maximum length
  if (maxLength !== undefined && value.length > maxLength) {
    return {
      valid: false,
      error: `Must have no more than ${maxLength} items`
    };
  }

  // Validate each item if a validator is provided
  if (itemValidator && typeof itemValidator === 'function') {
    for (let i = 0; i < value.length; i++) {
      const itemResult = itemValidator(value[i]);
      if (!itemResult.valid) {
        return {
          valid: false,
          error: `Item at index ${i} is invalid: ${itemResult.error}`
        };
      }
    }
  }

  return { valid: true, error: null };
};

/**
 * Validate a URL
 * @param value - The URL to validate
 * @param options - Validation options
 * @returns Validation result { valid: boolean, error: string|null }
 */
export const validateURL = (
  value: any,
  {
    required = false,
    requireProtocol = true
  }: URLValidationOptions = {}
): ValidationResult => {
  // Check if value is required and missing
  if (required && (value === undefined || value === null || value === '')) {
    return { valid: false, error: 'URL is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === undefined || value === null || value === '')) {
    return { valid: true, error: null };
  }

  // Check if value is a string
  if (typeof value !== 'string') {
    return { valid: false, error: 'URL must be a string' };
  }

  try {
    const url = new URL(value);

    // Check protocol if required
    if (requireProtocol && !['http:', 'https:'].includes(url.protocol)) {
      return {
        valid: false,
        error: 'URL must begin with http:// or https://'
      };
    }

    return { valid: true, error: null };
  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
};
