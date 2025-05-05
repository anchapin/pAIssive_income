/**
 * Client for the pAIssive Income API.
 *
 * This module provides a client for making requests to the pAIssive Income API.
 */

const { NoAuth } = require('./auth');

/**
 * Client for the pAIssive Income API.
 */
class Client {
  /**
   * Initialize the client.
   *
   * @param {Object} options - Client options
   * @param {string} options.baseUrl - Base URL for the API
   * @param {Object} options.auth - Authentication method
   * @param {string} options.version - API version to use
   * @param {number} options.timeout - Request timeout in milliseconds
   */
  constructor(options = {}) {
    this.baseUrl = (options.baseUrl || 'http://localhost:8000/api').replace(/\/$/, '');
    this.auth = options.auth || new NoAuth();
    this.version = options.version || 'v1';
    this.timeout = options.timeout || 60000;

    // Initialize services
    const NicheAnalysisService = require('./services/niche-analysis');
    const MonetizationService = require('./services/monetization');
    const MarketingService = require('./services/marketing');
    const AIModelsService = require('./services/ai-models');
    const AgentTeamService = require('./services/agent-team');
    const UserService = require('./services/user');
    const DashboardService = require('./services/dashboard');
    const APIKeyService = require('./services/api-key');

    this.nicheAnalysis = new NicheAnalysisService(this);
    this.monetization = new MonetizationService(this);
    this.marketing = new MarketingService(this);
    this.aiModels = new AIModelsService(this);
    this.agentTeam = new AgentTeamService(this);
    this.user = new UserService(this);
    this.dashboard = new DashboardService(this);
    this.apiKeys = new APIKeyService(this);
  }

  /**
   * Make a request to the API.
   *
   * @param {string} method - HTTP method to use
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @param {Object} options.params - Query parameters
   * @param {Object} options.data - Request body
   * @param {Object} options.headers - Additional headers
   * @param {Object} options.files - Files to upload
   * @returns {Promise<Object>} Response data
   * @throws {Error} If the request fails
   */
  async request(method, endpoint, options = {}) {
    const url = new URL(`${this.baseUrl}/${this.version}/${endpoint.replace(/^\//, '')}`);

    // Add query parameters
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    // Prepare headers
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...this.auth.getHeaders(),
      ...(options.headers || {})
    };

    // Prepare request options
    const requestOptions = {
      method,
      headers,
      body: options.data ? JSON.stringify(options.data) : undefined,
    };

    // Add timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    requestOptions.signal = controller.signal;

    try {
      // Make request
      const response = await fetch(url.toString(), requestOptions);

      // Check for errors
      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.message || `Request failed with status ${response.status}`);
        } else {
          const errorText = await response.text();
          throw new Error(errorText || `Request failed with status ${response.status}`);
        }
      }

      // Parse response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return { data: await response.text() };
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error(`Request timed out after ${this.timeout}ms`);
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Make a GET request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Response data
   */
  async get(endpoint, params) {
    return this.request('GET', endpoint, { params });
  }

  /**
   * Make a POST request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async post(endpoint, data) {
    return this.request('POST', endpoint, { data });
  }

  /**
   * Make a PUT request.
   *
   * @param {string} endpoint - API endpoint
   * @param {Object} data - Request body
   * @returns {Promise<Object>} Response data
   */
  async put(endpoint, data) {
    return this.request('PUT', endpoint, { data });
  }

  /**
   * Make a DELETE request.
   *
   * @param {string} endpoint - API endpoint
   * @returns {Promise<Object>} Response data
   */
  async delete(endpoint) {
    return this.request('DELETE', endpoint);
  }
}

module.exports = Client;
