/**
 * Utility functions for safely logging potentially untrusted data
 * to prevent log injection vulnerabilities.
 */

/**
 * Sanitizes a value for safe logging to prevent log injection attacks.
 * 
 * @param {any} value - The value to sanitize
 * @returns {string} - A sanitized string representation of the value
 */
function sanitizeForLog(value) {
  if (value === null || value === undefined) {
    return String(value);
  }

  if (typeof value === 'string') {
    // Replace newlines, carriage returns and other control characters
    return value
      .replace(/[\n\r\t\v\f\b]/g, ' ')
      .replace(/[\x00-\x1F\x7F-\x9F]/g, '')
      .replace(/[^\x20-\x7E]/g, '?');
  }

  if (typeof value === 'object') {
    try {
      // For objects, we sanitize the JSON string representation
      const stringified = JSON.stringify(value);
      return sanitizeForLog(stringified);
    } catch (error) {
      return '[Object sanitization failed]';
    }
  }

  // For other types (number, boolean), convert to string
  return String(value);
}

/**
 * Safely logs a message with sanitized values
 * 
 * @param {string} message - The message template
 * @param {any} value - The value to sanitize and include in the log
 * @returns {void}
 */
function safeLog(message, value) {
  console.log(message, sanitizeForLog(value));
}

/**
 * Safely logs an error with sanitized values
 * 
 * @param {string} message - The message template
 * @param {any} value - The value to sanitize and include in the log
 * @returns {void}
 */
function safeErrorLog(message, value) {
  console.error(message, sanitizeForLog(value));
}

module.exports = {
  sanitizeForLog,
  safeLog,
  safeErrorLog
};
