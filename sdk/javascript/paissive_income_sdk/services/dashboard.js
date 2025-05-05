/**
 * Dashboard service for the pAIssive Income API.
 *
 * This module provides a service for interacting with the dashboard endpoints.
 */

const BaseService = require('./base');

/**
 * Dashboard service.
 * @extends BaseService
 */
class DashboardService extends BaseService {
  /**
   * Get dashboard overview.
   *
   * @returns {Promise<Object>} Dashboard overview data
   */
  async getOverview() {
    return this._get('dashboard/overview');
  }

  /**
   * Get revenue statistics.
   *
   * @param {Object} params - Optional query parameters
   * @param {string} params.start_date - Start date for the statistics (ISO format)
   * @param {string} params.end_date - End date for the statistics (ISO format)
   * @param {string} params.interval - Time interval for data points (day, week, month)
   * @returns {Promise<Object>} Revenue statistics
   */
  async getRevenueStats(params) {
    return this._get('dashboard/revenue', params);
  }

  /**
   * Get subscriber statistics.
   *
   * @param {Object} params - Optional query parameters
   * @param {string} params.start_date - Start date for the statistics (ISO format)
   * @param {string} params.end_date - End date for the statistics (ISO format)
   * @param {string} params.interval - Time interval for data points (day, week, month)
   * @returns {Promise<Object>} Subscriber statistics
   */
  async getSubscriberStats(params) {
    return this._get('dashboard/subscribers', params);
  }

  /**
   * Get website traffic statistics.
   *
   * @param {Object} params - Optional query parameters
   * @param {string} params.start_date - Start date for the statistics (ISO format)
   * @param {string} params.end_date - End date for the statistics (ISO format)
   * @param {string} params.interval - Time interval for data points (day, week, month)
   * @returns {Promise<Object>} Traffic statistics
   */
  async getTrafficStats(params) {
    return this._get('dashboard/traffic', params);
  }

  /**
   * Get conversion statistics.
   *
   * @param {Object} params - Optional query parameters
   * @param {string} params.start_date - Start date for the statistics (ISO format)
   * @param {string} params.end_date - End date for the statistics (ISO format)
   * @param {string} params.interval - Time interval for data points (day, week, month)
   * @returns {Promise<Object>} Conversion statistics
   */
  async getConversionStats(params) {
    return this._get('dashboard/conversions', params);
  }

  /**
   * Get performance metrics.
   *
   * @returns {Promise<Object>} Performance metrics
   */
  async getPerformanceMetrics() {
    return this._get('dashboard/performance');
  }
}

module.exports = DashboardService;
