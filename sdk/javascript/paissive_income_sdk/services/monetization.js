/**
 * Monetization service for the pAIssive Income API.
 * 
 * This module provides a service for interacting with the monetization endpoints.
 */

const BaseService = require('./base');

/**
 * Monetization service.
 * @extends BaseService
 */
class MonetizationService extends BaseService {
  /**
   * Get all solutions available for monetization.
   * 
   * @returns {Promise<Object>} List of solutions
   */
  async getSolutions() {
    return this._get('monetization/solutions');
  }
  
  /**
   * Create a subscription model.
   * 
   * @param {Object} data - Subscription model data
   * @param {string} data.name - Name of the subscription model
   * @param {string} data.description - Description of the subscription model
   * @param {Array} data.tiers - List of pricing tiers
   * @param {Array} data.features - List of features
   * @returns {Promise<Object>} Created subscription model
   */
  async createSubscriptionModel(data) {
    return this._post('monetization/subscription-models', data);
  }
  
  /**
   * Get all subscription models.
   * 
   * @returns {Promise<Object>} List of subscription models
   */
  async getSubscriptionModels() {
    return this._get('monetization/subscription-models');
  }
  
  /**
   * Get a specific subscription model.
   * 
   * @param {string} modelId - Subscription model ID
   * @returns {Promise<Object>} Subscription model details
   */
  async getSubscriptionModel(modelId) {
    return this._get(`monetization/subscription-models/${modelId}`);
  }
  
  /**
   * Update a subscription model.
   * 
   * @param {string} modelId - Subscription model ID
   * @param {Object} data - Updated subscription model data
   * @returns {Promise<Object>} Updated subscription model
   */
  async updateSubscriptionModel(modelId, data) {
    return this._put(`monetization/subscription-models/${modelId}`, data);
  }
  
  /**
   * Delete a subscription model.
   * 
   * @param {string} modelId - Subscription model ID
   * @returns {Promise<Object>} Result of the deletion
   */
  async deleteSubscriptionModel(modelId) {
    return this._delete(`monetization/subscription-models/${modelId}`);
  }
  
  /**
   * Create a revenue projection.
   * 
   * @param {Object} data - Revenue projection data
   * @param {string} data.solution_id - Solution ID
   * @param {string} data.subscription_model_id - Subscription model ID
   * @param {number} data.timeframe_months - Number of months to project
   * @param {number} data.initial_subscribers - Initial number of subscribers
   * @param {number} data.growth_rate - Monthly growth rate
   * @returns {Promise<Object>} Revenue projection
   */
  async createRevenueProjection(data) {
    return this._post('monetization/revenue-projections', data);
  }
  
  /**
   * Get all revenue projections.
   * 
   * @returns {Promise<Object>} List of revenue projections
   */
  async getRevenueProjections() {
    return this._get('monetization/revenue-projections');
  }
  
  /**
   * Get a specific revenue projection.
   * 
   * @param {string} projectionId - Revenue projection ID
   * @returns {Promise<Object>} Revenue projection details
   */
  async getRevenueProjection(projectionId) {
    return this._get(`monetization/revenue-projections/${projectionId}`);
  }
}

module.exports = MonetizationService;