/**
 * Validation utilities index
 *
 * This file exports all validation utilities to make them easier to import.
 */

// Import validators to use in the schemas
import {
  validateString,
  validateEmail,
  validatePassword,
  validateNumber,
  validateArray,
  type ValidationResult
} from './validators';

// Export all validators and types
export * from './validators';

// Export the form validation hook
export { default as useFormValidation } from './useFormValidation';

// Validation schema interfaces
interface ValidationSchema<T> {
  [key: string]: (value: any, allValues?: T) => ValidationResult;
}

// Form validation schemas 
export const validationSchemas = {
  /**
   * Login form validation schema
   */
  login: {
    username: (value: string) => validateString(value, {
      required: true,
      minLength: 3,
      maxLength: 50
    }),

    credentials: (value: string) => validateString(value, {
      required: true,
      minLength: 6,
      maxLength: 100
    })
  } as ValidationSchema<{username: string; credentials: string}>,

  /**
   * Registration form validation schema
   */
  register: {
    username: (value: string) => validateString(value, {
      required: true,
      minLength: 3,
      maxLength: 50
    }),

    email: (value: string) => validateEmail(value, {
      required: true
    }),

    authCredential: (value: string) => validatePassword(value, {
      required: true,
      minLength: 8,
      requireNumber: true
    }),

    confirmCredential: (value: string, values?: {authCredential: string}) => {
      const baseValidation = validateString(value, { required: true });

      if (!baseValidation.valid) {
        return baseValidation;
      }

      return value === values?.authCredential
        ? { valid: true, error: null }
        : { valid: false, error: 'Credentials must match' };
    },

    name: (value: string) => validateString(value, {
      required: true,
      minLength: 1,
      maxLength: 100
    })
  } as ValidationSchema<{
    username: string;
    email: string;
    authCredential: string;
    confirmCredential: string;
    name: string;
  }>,

  /**
   * Profile update form validation schema
   */
  profile: {
    email: (value: string) => validateEmail(value, { required: true }),
    name: (value: string) => validateString(value, {
      required: true,
      minLength: 1,
      maxLength: 100
    })
  } as ValidationSchema<{email: string; name: string}>,

  /**
   * Solution generation form validation schema
   */
  solution: {
    nicheId: (value: number) => validateNumber(value, {
      required: true,
      integer: true
    }),

    templateId: (value: number) => validateNumber(value, {
      required: true,
      integer: true
    })
  } as ValidationSchema<{nicheId: number; templateId: number}>,

  /**
   * Monetization strategy form validation schema
   */
  monetizationStrategy: {
    solutionId: (value: number) => validateNumber(value, {
      required: true,
      integer: true
    }),

    basePrice: (value: number) => validateNumber(value, {
      required: true,
      min: 0
    })
  } as ValidationSchema<{solutionId: number; basePrice: number}>,

  /**
   * Marketing campaign form validation schema
   */
  marketingCampaign: {
    solutionId: (value: number) => validateNumber(value, {
      required: true,
      integer: true
    }),

    audienceIds: (value: number[]) => validateArray(value, {
      required: true,
      minLength: 1
    }),

    channelIds: (value: number[]) => validateArray(value, {
      required: true,
      minLength: 1
    })
  } as ValidationSchema<{solutionId: number; audienceIds: number[]; channelIds: number[]}>
};
