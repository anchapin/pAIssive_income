import { fetchAPI } from './apiClient';

/**
 * API Analytics endpoints
 */
const analyticsAPI = {
  /**
   * Get API usage summary
   * @param {number} days - Number of days to include
   * @returns {Promise<Object>} - Summary data
   */
  getSummary: (days = 30) => fetchAPI(`/api/v1/analytics/summary?days=${days}`),

  /**
   * Get detailed request statistics
   * @param {Object} params - Query parameters
   * @param {number} params.days - Number of days to include
   * @param {string} params.endpoint - Filter by endpoint
   * @param {string} params.version - Filter by API version
   * @param {string} params.user_id - Filter by user ID
   * @param {string} params.api_key_id - Filter by API key ID
   * @param {number} params.status_code - Filter by status code
   * @param {string} params.aggregate - Aggregate by (daily, hourly)
   * @param {number} params.limit - Maximum number of records to return
   * @param {number} params.offset - Number of records to skip
   * @returns {Promise<Object>} - Request statistics
   */
  getRequests: (params = {}) => {
    const queryParams = new URLSearchParams();

    // Add parameters to query string
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value);
      }
    });

    return fetchAPI(`/api/v1/analytics/requests?${queryParams.toString()}`);
  },

  /**
   * Get endpoint statistics
   * @param {number} days - Number of days to include
   * @returns {Promise<Array>} - Endpoint statistics
   */
  getEndpointStats: (days = 30) => fetchAPI(`/api/v1/analytics/endpoints?days=${days}`),

  /**
   * Get user statistics
   * @param {number} days - Number of days to include
   * @param {string} user_id - Filter by user ID
   * @returns {Promise<Array>} - User statistics
   */
  getUserStats: (days = 30, user_id = null) => {
    const url = user_id
      ? `/api/v1/analytics/users?days=${days}&user_id=${user_id}`
      : `/api/v1/analytics/users?days=${days}`;
    return fetchAPI(url);
  },

  /**
   * Get API key statistics
   * @param {number} days - Number of days to include
   * @param {string} api_key_id - Filter by API key ID
   * @returns {Promise<Array>} - API key statistics
   */
  getApiKeyStats: (days = 30, api_key_id = null) => {
    const url = api_key_id
      ? `/api/v1/analytics/api-keys?days=${days}&api_key_id=${api_key_id}`
      : `/api/v1/analytics/api-keys?days=${days}`;
    return fetchAPI(url);
  },

  /**
   * Export API requests to CSV
   * @param {Object} params - Query parameters
   * @returns {Promise<Blob>} - CSV file as blob
   */
  exportRequestsCSV: (params = {}) => {
    const queryParams = new URLSearchParams();

    // Add parameters to query string
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value);
      }
    });

    return fetchAPI(`/api/v1/analytics/export/requests?${queryParams.toString()}`, {
      responseType: 'blob'
    });
  }
};

export default analyticsAPI;
