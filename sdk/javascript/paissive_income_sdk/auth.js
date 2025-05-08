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

    // Use a WeakMap for credential storage instead of Symbol property for enhanced security
    if (!APIKeyAuth._credentialStore) {
      APIKeyAuth._credentialStore = new WeakMap();
    }

    // Store credential in WeakMap with this instance as key
    // This prevents the token from being exposed in object serialization, console.log, or debuggers
    APIKeyAuth._credentialStore.set(this, accessToken);

    // Store only a reference to indicate we have a credential
    this.hasCredential = true;
  }

  /**
   * Get authentication headers.
   *
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    const credential = APIKeyAuth._credentialStore ? APIKeyAuth._credentialStore.get(this) : null;
    if (!credential) {
      console.warn('API credential not available');
      return {};
    }

    // Sanitize credential - don't log it or expose its actual value in dev tools
    // Credential is still securely stored in WeakMap and used in the header
    const sanitizedKey = credential.slice(0, 4) + '***' + credential.slice(-4);
    Object.defineProperty(this, '_lastUsedKey', {
      value: sanitizedKey,
      writable: true,
      enumerable: false // Don't expose in object enumeration
    });

    return { "X-API-Key": credential };
  }

  /**
   * Clear the credential from memory when not needed
   */
  clearCredential() {
    if (APIKeyAuth._credentialStore) {
      APIKeyAuth._credentialStore.delete(this);
    }
    this.hasCredential = false;
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
    // Use WeakMap for better security - tokens won't be exposed in debuggers or console.log
    if (!JWTAuth._tokenStore) {
      JWTAuth._tokenStore = new WeakMap();
    }

    // Store token in WeakMap with this instance as key
    JWTAuth._tokenStore.set(this, token);

    // Store only a reference to indicate we have an auth token
    this.hasToken = true;
  }

  /**
   * Get authentication headers.
   *
   * @returns {Object} Authentication headers
   */
  getHeaders() {
    const token = JWTAuth._tokenStore ? JWTAuth._tokenStore.get(this) : null;
    if (!token) {
      console.warn('Authentication token not available');
      return {};
    }
    return { "Authorization": `Bearer ${token}` };
  }

  /**
   * Clear the token from memory when not needed
   */
  clearToken() {
    if (JWTAuth._tokenStore) {
      JWTAuth._tokenStore.delete(this);
    }
    this.hasToken = false;
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
