/**
 * AI Models service for the pAIssive Income API.
 * 
 * This module provides a service for interacting with the AI model endpoints.
 */

const BaseService = require('./base');

/**
 * AI Models service.
 * @extends BaseService
 */
class AIModelsService extends BaseService {
  /**
   * Get all available AI models.
   * 
   * @returns {Promise<Object>} List of AI models
   */
  async getModels() {
    return this._get('ai-models/models');
  }
  
  /**
   * Get details for a specific AI model.
   * 
   * @param {string} modelId - Model ID
   * @returns {Promise<Object>} Model details
   */
  async getModel(modelId) {
    return this._get(`ai-models/models/${modelId}`);
  }
  
  /**
   * Run inference on an AI model.
   * 
   * @param {Object} data - Inference request data
   * @param {string} data.model_id - Model ID
   * @param {Object} data.inputs - Input data for the model
   * @param {Object} data.parameters - Inference parameters
   * @returns {Promise<Object>} Inference results
   */
  async runInference(data) {
    return this._post('ai-models/inference', data);
  }
  
  /**
   * Download or register an AI model.
   * 
   * @param {Object} data - Model download data
   * @param {string} data.name - Model name
   * @param {string} data.source - Model source
   * @param {string} data.version - Model version
   * @returns {Promise<Object>} Download status
   */
  async downloadModel(data) {
    return this._post('ai-models/models/download', data);
  }
  
  /**
   * Get performance metrics for a specific AI model.
   * 
   * @param {string} modelId - Model ID
   * @returns {Promise<Object>} Performance metrics
   */
  async getModelPerformance(modelId) {
    return this._get(`ai-models/models/${modelId}/performance`);
  }
  
  /**
   * Compare multiple AI models.
   * 
   * @param {Object} data - Model comparison data
   * @param {Array<string>} data.model_ids - List of model IDs to compare
   * @param {Array<string>} data.metrics - List of metrics to compare
   * @param {Object} data.test_data - Optional test data for evaluation
   * @returns {Promise<Object>} Comparison results
   */
  async compareModels(data) {
    return this._post('ai-models/models/compare', data);
  }
  
  /**
   * Create a new version of an AI model.
   * 
   * @param {string} modelId - Model ID
   * @param {Object} data - Version creation data
   * @param {string} data.version - Version name
   * @param {string} data.changes - Description of changes
   * @param {Object} data.parameters - Model parameters
   * @returns {Promise<Object>} Created model version
   */
  async createModelVersion(modelId, data) {
    return this._post(`ai-models/models/${modelId}/versions`, data);
  }
}

module.exports = AIModelsService;