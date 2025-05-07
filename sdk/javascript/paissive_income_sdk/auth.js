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
   * @param {string} accessToken - API access token
   */
  constructor(accessToken) {
    super();
    // Don't store the access token directly as a property that could be exposed
    // Instead use a symbol as a private key to store the credential
    const tokenSymbol = Symbol('accessToken');
    this[tokenSymbol] = accessToken;

    // Store only a reference to indicate we have a credential
    this.hasCredential = true;

    // Method to safely access the token when needed
    this.getCredential = () => this[tokenSymbol];
  }

  /**
   * Get authentication headers.
   *
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return { "X-API-Key": this.getCredential() };
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
   * @param {string} token - JWT authentication token
   */
  constructor(token) {
    super();
    // Use similar private field approach to store the token securely
    const tokenSymbol = Symbol('authToken');
    this[tokenSymbol] = token;

    // Store only a reference to indicate we have an auth token
    this.hasToken = true;

    // Method to safely access the token when needed
    this.getToken = () => this[tokenSymbol];
  }

  /**
   * Get authentication headers.
   *
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    return { "Authorization": `Bearer ${this.getToken()}` };
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
