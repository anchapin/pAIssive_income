/**
 * API Key service for the pAIssive Income API.
 *
 * This module provides a service for managing API keys.
 */

const BaseService = require('./base');

/**
 * API Key service.
 * @extends BaseService
 */
class APIKeyService extends BaseService {
  /**
   * Create a new API key.
   *
   * @param {Object} data - API key creation data
   * @param {string} data.name - Name of the API key
   * @param {string} data.description - Description of the API key
   * @param {string} data.expires_at - Optional expiration date (ISO format)
   * @param {Array<string>} data.scopes - Optional list of permission scopes
   * @returns {Promise<Object>} Created API key data (including the actual key, which is only returned once)
   */
  async createApiKey(data) {
    return this._post('api-keys', data);
  }

  /**
   * Get all API keys for the current user.
   *
   * @returns {Promise<Object>} List of API keys
   */
  async getApiKeys() {
    return this._get('api-keys');
  }

  /**
   * Get details for a specific API key.
   *
   * @param {string} apiKeyId - API key ID
   * @returns {Promise<Object>} API key details (excluding the actual key)
   */
  async getApiKey(apiKeyId) {
    return this._get(`api-keys/${apiKeyId}`);
  }

  /**
   * Update an API key.
   *
   * @param {string} apiKeyId - API key ID
   * @param {Object} data - Updated API key data
   * @param {string} data.name - Name of the API key
   * @param {string} data.description - Description of the API key
   * @param {Array<string>} data.scopes - List of permission scopes
   * @returns {Promise<Object>} Updated API key details
   */
  async updateApiKey(apiKeyId, data) {
    return this._put(`api-keys/${apiKeyId}`, data);
  }

  /**
   * Delete an API key.
   *
   * @param {string} apiKeyId - API key ID
   * @returns {Promise<Object>} Result of the deletion
   */
  async deleteApiKey(apiKeyId) {
    return this._delete(`api-keys/${apiKeyId}`);
  }

  /**
   * Revoke an API key.
   *
   * @param {string} apiKeyId - API key ID
   * @returns {Promise<Object>} Result of the revocation
   */
  async revokeApiKey(apiKeyId) {
    return this._post(`api-keys/${apiKeyId}/revoke`, {});
  }

  /**
   * Get all available API key scopes.
   *
   * @returns {Promise<Object>} List of available scopes
   */
  async getApiKeyScopes() {
    return this._get('api-keys/scopes');
  }
}

module.exports = APIKeyService;
