import { useState, useEffect, useCallback } from 'react';

/**
 * Interface for form values
 */
interface FormValues {
  [key: string]: any;
}

/**
 * Interface for validation function result
 */
import { ValidationResult } from './validators';

/**
 * Interface for form validation schema
 */
type ValidationSchema<T extends FormValues> = {
  [K in keyof T]?: (value: T[K], allValues?: T) => ValidationResult;
};

/**
 * Interface for form validation state
 */
type FormState<T extends FormValues> = {
  values: T;
  errors: Partial<Record<keyof T, string | null>>;
  touched: Partial<Record<keyof T, boolean>>;
  dirty: boolean;
  isValid: boolean;
};

/**
 * Interface for form validation utilities
 */
interface FormValidation<T extends FormValues> extends FormState<T> {
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
  handleSubmit: (onSubmit: (values: T) => void) => (e: React.FormEvent) => void;
  setFieldValue: (field: keyof T, value: T[keyof T]) => void;
  resetForm: () => void;
  validateForm: () => boolean;
  setValues: React.Dispatch<React.SetStateAction<T>>;
}

/**
 * A hook for form validation
 *
 * @param initialValues - Initial form values
 * @param validationSchema - Schema defining validation rules for each field
 * @returns Form validation state and utilities
 */
const useFormValidation = <T extends FormValues>(
  initialValues: T,
  validationSchema: ValidationSchema<T>
): FormValidation<T> => {
  // Form values state
  const [values, setValues] = useState<T>(initialValues);

  // Initialize errors by validating all fields
  const validateField = useCallback((fieldName: keyof T, value: T[keyof T], allValues: T) => {
    // Get validation function for field
    const fieldSchema = validationSchema[fieldName];

    // If no validation for this field, it's valid
    if (!fieldSchema) {
      return null;
    }

    // Run validation
    const result = fieldSchema(value, allValues);

    // Return error message if invalid, null otherwise
    return result.valid ? null : result.error;
  }, [validationSchema]);

  const getInitialErrors = useCallback(() => {
    const errors: Partial<Record<keyof T, string | null>> = {};
    Object.keys(validationSchema).forEach(fieldName => {
      const error = validateField(fieldName as keyof T, initialValues[fieldName as keyof T], initialValues);
      if (error) {
        errors[fieldName as keyof T] = error;
      }
    });
    return errors;
  }, [validationSchema, initialValues, validateField]);

  // Errors state - object with field name as key and error message as value
  const [errors, setErrors] = useState<Partial<Record<keyof T, string | null>>>(getInitialErrors);

  // Touched state - object with field name as key and boolean as value
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  // Dirty state - whether any field has been changed
  const [dirty, setDirty] = useState(false);

  // Form validity state
  const [isValid, setIsValid] = useState(Object.keys(getInitialErrors()).length === 0);

  /**
   * Validate all fields and update errors state
   * @returns {boolean} Whether the form is valid
   */
  const validateForm = useCallback(() => {
    const newErrors: Partial<Record<keyof T, string | null>> = {};
    let hasErrors = false;

    // Validate each field
    Object.keys(validationSchema).forEach(fieldName => {
      const error = validateField(fieldName as keyof T, values[fieldName as keyof T], values);
      if (error) {
        newErrors[fieldName as keyof T] = error;
        hasErrors = true;
      }
    });

    // Update errors state
    setErrors(newErrors);

    // Return form validity
    return !hasErrors;
  }, [validateField, validationSchema, values]);

  /**
   * Handler for input changes
   */  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const target = e.target;
    const fieldName = target.name as keyof T;
    const fieldValue = target.type === 'checkbox' ? (target as HTMLInputElement).checked : target.value;

    // Update values state
    setValues(prevValues => {
      const newValues = {
        ...prevValues,
        [fieldName]: fieldValue
      };

      // Validate the field if it's been touched
      if (touched[fieldName]) {
        const error = validateField(fieldName, newValues[fieldName], newValues);
        setErrors(prevErrors => ({
          ...prevErrors,
          [fieldName]: error
        }));
      }

      return newValues;
    });

    // Mark form as dirty
    setDirty(true);
  }, [touched, validateField]);

  /**
   * Handler for input blur
   */
  const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const target = e.target;
    const fieldName = target.name as keyof T;

    // Mark field as touched
    setTouched(prevTouched => ({
      ...prevTouched,
      [fieldName]: true
    }));

    // Validate the field
    const error = validateField(fieldName, values[fieldName], values);
    setErrors(prevErrors => ({
      ...prevErrors,
      [fieldName]: error
    }));
  }, [validateField, values]);

  /**
   * Set a field value programmatically
   */
  const setFieldValue = useCallback((field: keyof T, value: T[keyof T]) => {
    // Update values state
    setValues(prevValues => {
      const newValues = {
        ...prevValues,
        [field]: value
      };

      // Mark form as dirty
      setDirty(true);

      // Validate the field if it's been touched
      if (touched[field]) {
        const error = validateField(field, value, newValues);
        setErrors(prevErrors => ({
          ...prevErrors,
          [field]: error
        }));
      }

      return newValues;
    });
  }, [touched, validateField]);

  /**
   * Reset the form to its initial state
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors(getInitialErrors());
    setTouched({});
    setDirty(false);
  }, [initialValues, getInitialErrors]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback((onSubmit: (values: T) => void) => {
    return (e: React.FormEvent) => {
      // Prevent default form submission
      e.preventDefault();

      // Mark all fields as touched
      const allTouched = Object.keys(validationSchema).reduce((acc, field) => {
        acc[field as keyof T] = true;
        return acc;
      }, {} as Partial<Record<keyof T, boolean>>);
      setTouched(allTouched);

      // Validate the form
      const formIsValid = validateForm();

      // If valid, call the submit handler
      if (formIsValid) {
        onSubmit(values);
      }
    };
  }, [validateForm, validationSchema, values]);

  // Validate the form when values change
  useEffect(() => {
    const formIsValid = validateForm();
    setIsValid(formIsValid);
  }, [values, validateForm]);

  return {
    values,
    errors,
    touched,
    dirty,
    isValid,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    resetForm,
    validateForm,
    setValues,
  };
};

export default useFormValidation;
