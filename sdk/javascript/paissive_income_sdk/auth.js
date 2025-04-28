/**
 * Authentication classes for the pAIssive Income SDK.
 * 
 * This module provides authentication classes for the pAIssive Income API.
 */

/**
 * Base authentication class.
 */
class Auth {
  /**
   * Get authentication headers.
   * 
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return {};
  }
}

/**
 * API key authentication.
 * @extends Auth
 */
class APIKeyAuth extends Auth {
  /**
   * Initialize API key authentication.
   * 
   * @param {string} apiKey - API key
   */
  constructor(apiKey) {
    super();
    this.apiKey = apiKey;
  }

  /**
   * Get authentication headers.
   * 
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return { "X-API-Key": this.apiKey };
  }
}

/**
 * JWT authentication.
 * @extends Auth
 */
class JWTAuth extends Auth {
  /**
   * Initialize JWT authentication.
   * 
   * @param {string} token - JWT token
   */
  constructor(token) {
    super();
    this.token = token;
  }

  /**
   * Get authentication headers.
   * 
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return { "Authorization": `Bearer ${this.token}` };
  }
}

/**
 * No authentication.
 * @extends Auth
 */
class NoAuth extends Auth {
  /**
   * Get authentication headers.
   * 
   * @returns {Object} Empty headers
   */
  getHeaders() {
    return {};
  }
}

module.exports = {
  Auth,
  APIKeyAuth,
  JWTAuth,
  NoAuth
};