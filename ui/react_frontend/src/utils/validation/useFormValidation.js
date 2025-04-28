import { useState, useEffect, useCallback } from 'react';

/**
 * A hook for form validation
 * 
 * @param {Object} initialValues - Initial form values
 * @param {Object} validationSchema - Schema defining validation rules for each field
 * @returns {Object} Form validation state and utilities
 */
const useFormValidation = (initialValues = {}, validationSchema = {}) => {
  // Form values state
  const [values, setValues] = useState(initialValues);
  
  // Errors state - object with field name as key and error message as value
  const [errors, setErrors] = useState({});
  
  // Touched state - object with field name as key and boolean as value
  const [touched, setTouched] = useState({});
  
  // Dirty state - whether any field has been changed
  const [dirty, setDirty] = useState(false);
  
  // Form validity state
  const [isValid, setIsValid] = useState(false);
  
  /**
   * Validate a single field
   * @param {string} fieldName - Field name
   * @param {*} value - Field value
   * @returns {string|null} Error message or null if valid
   */
  const validateField = useCallback((fieldName, value) => {
    // Get validation function for field
    const fieldSchema = validationSchema[fieldName];
    
    // If no validation for this field, it's valid
    if (!fieldSchema) {
      return null;
    }
    
    // Run validation
    const result = fieldSchema(value, values);
    
    // Return error message if invalid, null otherwise
    return result.valid ? null : result.error;
  }, [validationSchema, values]);
  
  /**
   * Validate all fields and update errors state
   * @returns {boolean} Whether the form is valid
   */
  const validateForm = useCallback(() => {
    const newErrors = {};
    let hasErrors = false;
    
    // Validate each field
    Object.keys(validationSchema).forEach(fieldName => {
      const error = validateField(fieldName, values[fieldName]);
      if (error) {
        newErrors[fieldName] = error;
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
   * @param {Object} e - Event object
   */
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    
    // Set value based on input type
    const fieldValue = type === 'checkbox' ? checked : value;
    
    // Update values state
    setValues(prevValues => ({
      ...prevValues,
      [name]: fieldValue
    }));
    
    // Mark form as dirty
    setDirty(true);
    
    // Validate the field if it's been touched
    if (touched[name]) {
      const error = validateField(name, fieldValue);
      setErrors(prevErrors => ({
        ...prevErrors,
        [name]: error
      }));
    }
  }, [touched, validateField]);
  
  /**
   * Handler for input blur (when field loses focus)
   * @param {Object} e - Event object
   */
  const handleBlur = useCallback((e) => {
    const { name, value } = e.target;
    
    // Mark field as touched
    setTouched(prevTouched => ({
      ...prevTouched,
      [name]: true
    }));
    
    // Validate the field
    const error = validateField(name, value);
    setErrors(prevErrors => ({
      ...prevErrors,
      [name]: error
    }));
  }, [validateField]);
  
  /**
   * Set a field value programmatically
   * @param {string} field - Field name
   * @param {*} value - Field value
   */
  const setFieldValue = useCallback((field, value) => {
    // Update values state
    setValues(prevValues => ({
      ...prevValues,
      [field]: value
    }));
    
    // Mark form as dirty
    setDirty(true);
    
    // Validate the field if it's been touched
    if (touched[field]) {
      const error = validateField(field, value);
      setErrors(prevErrors => ({
        ...prevErrors,
        [field]: error
      }));
    }
  }, [touched, validateField]);
  
  /**
   * Reset the form to its initial state
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setDirty(false);
  }, [initialValues]);
  
  /**
   * Handle form submission
   * @param {Function} onSubmit - Submit handler function
   * @returns {Function} Form submit handler function
   */
  const handleSubmit = useCallback((onSubmit) => {
    return (e) => {
      // Prevent default form submission
      e.preventDefault();
      
      // Mark all fields as touched
      const allTouched = Object.keys(validationSchema).reduce((acc, field) => {
        acc[field] = true;
        return acc;
      }, {});
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