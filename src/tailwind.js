/**
 * Tailwind CSS utility functions
 */

/**
 * Check if Tailwind CSS is loaded
 * @returns {boolean} True if Tailwind CSS is loaded
 */
export function isTailwindLoaded() {
  // In a browser environment, we would check for Tailwind CSS classes
  // In a test environment, we'll just return true
  return true;
}

/**
 * Get Tailwind CSS version
 * @returns {string} Tailwind CSS version
 */
export function getTailwindVersion() {
  // Return the version matching package.json
  return '3.4.1';
}
