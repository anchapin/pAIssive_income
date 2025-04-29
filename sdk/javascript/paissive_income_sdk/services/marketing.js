/**
 * Marketing service for the pAIssive Income API.
 * 
 * This module provides a service for interacting with the marketing endpoints.
 */

const BaseService = require('./base');

/**
 * Marketing service.
 * @extends BaseService
 */
class MarketingService extends BaseService {
  /**
   * Get all solutions available for marketing.
   * 
   * @returns {Promise<Object>} List of solutions
   */
  async getSolutions() {
    return this._get('marketing/solutions');
  }
  
  /**
   * Create a marketing strategy.
   * 
   * @param {Object} data - Marketing strategy data
   * @param {string} data.solution_id - Solution ID
   * @param {Array<string>} data.audience_ids - List of target audience IDs
   * @param {Array<string>} data.channel_ids - List of marketing channel IDs
   * @param {Object} data.budget - Budget information
   * @param {Object} data.timeframe - Timeframe information
   * @returns {Promise<Object>} Created marketing strategy
   */
  async createMarketingStrategy(data) {
    return this._post('marketing/strategies', data);
  }
  
  /**
   * Get all marketing strategies.
   * 
   * @returns {Promise<Object>} List of marketing strategies
   */
  async getMarketingStrategies() {
    return this._get('marketing/strategies');
  }
  
  /**
   * Get a specific marketing strategy.
   * 
   * @param {string} strategyId - Marketing strategy ID
   * @returns {Promise<Object>} Marketing strategy details
   */
  async getMarketingStrategy(strategyId) {
    return this._get(`marketing/strategies/${strategyId}`);
  }
  
  /**
   * Update a marketing strategy.
   * 
   * @param {string} strategyId - Marketing strategy ID
   * @param {Object} data - Updated marketing strategy data
   * @returns {Promise<Object>} Updated marketing strategy
   */
  async updateMarketingStrategy(strategyId, data) {
    return this._put(`marketing/strategies/${strategyId}`, data);
  }
  
  /**
   * Delete a marketing strategy.
   * 
   * @param {string} strategyId - Marketing strategy ID
   * @returns {Promise<Object>} Result of the deletion
   */
  async deleteMarketingStrategy(strategyId) {
    return this._delete(`marketing/strategies/${strategyId}`);
  }
  
  /**
   * Get all user personas.
   * 
   * @returns {Promise<Object>} List of user personas
   */
  async getUserPersonas() {
    return this._get('marketing/personas');
  }
  
  /**
   * Create a user persona.
   * 
   * @param {Object} data - User persona data
   * @returns {Promise<Object>} Created user persona
   */
  async createUserPersona(data) {
    return this._post('marketing/personas', data);
  }
  
  /**
   * Get all marketing channels.
   * 
   * @returns {Promise<Object>} List of marketing channels
   */
  async getMarketingChannels() {
    return this._get('marketing/channels');
  }
  
  /**
   * Generate marketing content.
   * 
   * @param {Object} data - Content generation data
   * @param {string} data.strategy_id - Marketing strategy ID
   * @param {string} data.content_type - Type of content to generate
   * @returns {Promise<Object>} Generated content
   */
  async generateContent(data) {
    return this._post('marketing/content', data);
  }
  
  /**
   * Create a content calendar.
   * 
   * @param {Object} data - Content calendar data
   * @param {string} data.strategy_id - Marketing strategy ID
   * @param {string} data.start_date - Start date
   * @param {string} data.end_date - End date
   * @returns {Promise<Object>} Content calendar
   */
  async createContentCalendar(data) {
    return this._post('marketing/content-calendars', data);
  }
}

module.exports = MarketingService;