/**
 * Validation utilities index
 * 
 * This file exports all validation utilities to make them easier to import.
 */

// Export all validators
export * from './validators';

// Export the form validation hook
export { default as useFormValidation } from './useFormValidation';

// Export common validation schemas
export const validationSchemas = {
  /**
   * Login form validation schema
   */
  login: {
    username: (value) => validateString(value, { 
      required: true, 
      minLength: 3, 
      maxLength: 50 
    }),
    
    password: (value) => validateString(value, { 
      required: true, 
      minLength: 6,
      maxLength: 100 
    })
  },
  
  /**
   * Registration form validation schema
   */
  register: {
    username: (value) => validateString(value, { 
      required: true, 
      minLength: 3, 
      maxLength: 50 
    }),
    
    email: (value) => validateEmail(value, { 
      required: true 
    }),
    
    password: (value) => validatePassword(value, { 
      required: true, 
      minLength: 8, 
      requireNumber: true
    }),
    
    confirmPassword: (value, values) => {
      const baseValidation = validateString(value, { required: true });
      
      if (!baseValidation.valid) {
        return baseValidation;
      }
      
      return value === values.password 
        ? { valid: true, error: null }
        : { valid: false, error: 'Passwords must match' };
    },
    
    name: (value) => validateString(value, { 
      required: true, 
      minLength: 1, 
      maxLength: 100 
    })
  },
  
  /**
   * Profile update form validation schema
   */
  profile: {
    email: (value) => validateEmail(value, { required: true }),
    name: (value) => validateString(value, { 
      required: true, 
      minLength: 1, 
      maxLength: 100 
    })
  },
  
  /**
   * Solution generation form validation schema
   */
  solution: {
    nicheId: (value) => validateNumber(value, { 
      required: true, 
      integer: true 
    }),
    
    templateId: (value) => validateNumber(value, { 
      required: true, 
      integer: true 
    })
  },
  
  /**
   * Monetization strategy form validation schema
   */
  monetizationStrategy: {
    solutionId: (value) => validateNumber(value, { 
      required: true, 
      integer: true 
    }),
    
    basePrice: (value) => validateNumber(value, { 
      required: true, 
      min: 0 
    })
  },
  
  /**
   * Marketing campaign form validation schema
   */
  marketingCampaign: {
    solutionId: (value) => validateNumber(value, { 
      required: true, 
      integer: true 
    }),
    
    audienceIds: (value) => validateArray(value, { 
      required: true, 
      minLength: 1 
    }),
    
    channelIds: (value) => validateArray(value, { 
      required: true, 
      minLength: 1 
    })
  }
};

// Import validators to use in the schemas above
import { 
  validateString, 
  validateEmail, 
  validatePassword, 
  validateNumber, 
  validateArray 
} from './validators';