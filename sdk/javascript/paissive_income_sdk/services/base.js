/**
 * Base service class for the pAIssive Income API.
 *
 * This module provides a base service class that all other service classes inherit from.
 */

/**
 * Base service class.
 */
class BaseService {
  /**
   * Initialize the service.
   *
   * @param {Object} client - API client
   */
  constructor(client) {
    this.client = client;
  }

  /**
   * Make a GET request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response data
   */
  async _get(endpoint, params) {
    return this.client.get(endpoint, params);
  }

  /**
   * Make a POST request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async _post(endpoint, data) {
    return this.client.post(endpoint, data);
  }

  /**
   * Make a PUT request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async _put(endpoint, data) {
    return this.client.put(endpoint, data);
  }

  /**
   * Make a DELETE request.
   *
   * @param {string} endpoint - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async _delete(endpoint) {
    return this.client.delete(endpoint);
  }
}

module.exports = BaseService;
