/**
 * Niche Analysis service for the pAIssive Income API.
 * 
 * This module provides a service for interacting with the niche analysis endpoints.
 */

const BaseService = require('./base');

/**
 * Niche Analysis service.
 * @extends BaseService
 */
class NicheAnalysisService extends BaseService {
  /**
   * Get all market segments.
   * 
   * @returns {Promise<Object>} List of market segments
   */
  async getMarketSegments() {
    return this._get('niche-analysis/segments');
  }
  
  /**
   * Analyze niches for the given market segments.
   * 
   * @param {Array<string>} segments - List of market segment IDs
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeNiches(segments) {
    return this._post('niche-analysis/analyze', { segments });
  }
  
  /**
   * Get results for a specific analysis.
   * 
   * @param {string} analysisId - Analysis ID
   * @returns {Promise<Object>} Analysis results
   */
  async getAnalysisResults(analysisId) {
    return this._get(`niche-analysis/results/${analysisId}`);
  }
  
  /**
   * Get all analysis results.
   * 
   * @returns {Promise<Object>} List of analysis results
   */
  async getAllResults() {
    return this._get('niche-analysis/results');
  }
  
  /**
   * Get problems for a specific niche.
   * 
   * @param {string} nicheId - Niche ID
   * @returns {Promise<Object>} List of problems
   */
  async getProblems(nicheId) {
    return this._get(`niche-analysis/niches/${nicheId}/problems`);
  }
  
  /**
   * Get opportunities for a specific niche.
   * 
   * @param {string} nicheId - Niche ID
   * @returns {Promise<Object>} List of opportunities
   */
  async getOpportunities(nicheId) {
    return this._get(`niche-analysis/niches/${nicheId}/opportunities`);
  }
  
  /**
   * Compare multiple opportunities.
   * 
   * @param {Array<string>} opportunityIds - List of opportunity IDs
   * @returns {Promise<Object>} Comparison results
   */
  async compareOpportunities(opportunityIds) {
    return this._post('niche-analysis/opportunities/compare', { opportunity_ids: opportunityIds });
  }
}

module.exports = NicheAnalysisService;