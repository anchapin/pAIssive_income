/**
 * Agent Team service for the pAIssive Income API.
 * 
 * This module provides a service for interacting with the agent team endpoints.
 */

const BaseService = require('./base');

/**
 * Agent Team service.
 * @extends BaseService
 */
class AgentTeamService extends BaseService {
  /**
   * Create an agent team.
   * 
   * @param {Object} data - Team creation data
   * @param {string} data.name - Team name
   * @param {string} data.description - Team description
   * @param {Array} data.agents - List of agent IDs or configurations
   * @returns {Promise<Object>} Created team
   */
  async createTeam(data) {
    return this._post('agent-team/teams', data);
  }
  
  /**
   * Get all agent teams.
   * 
   * @returns {Promise<Object>} List of agent teams
   */
  async getTeams() {
    return this._get('agent-team/teams');
  }
  
  /**
   * Get details for a specific agent team.
   * 
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Team details
   */
  async getTeam(teamId) {
    return this._get(`agent-team/teams/${teamId}`);
  }
  
  /**
   * Update an agent team.
   * 
   * @param {string} teamId - Team ID
   * @param {Object} data - Updated team data
   * @returns {Promise<Object>} Updated team
   */
  async updateTeam(teamId, data) {
    return this._put(`agent-team/teams/${teamId}`, data);
  }
  
  /**
   * Delete an agent team.
   * 
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Result of the deletion
   */
  async deleteTeam(teamId) {
    return this._delete(`agent-team/teams/${teamId}`);
  }
  
  /**
   * Get all available agents.
   * 
   * @returns {Promise<Object>} List of agents
   */
  async getAgents() {
    return this._get('agent-team/agents');
  }
  
  /**
   * Get details for a specific agent.
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent details
   */
  async getAgent(agentId) {
    return this._get(`agent-team/agents/${agentId}`);
  }
  
  /**
   * Get all available workflows.
   * 
   * @returns {Promise<Object>} List of workflows
   */
  async getWorkflows() {
    return this._get('agent-team/workflows');
  }
  
  /**
   * Run a workflow with an agent team.
   * 
   * @param {Object} data - Workflow execution data
   * @param {string} data.team_id - Team ID
   * @param {string} data.workflow_id - Workflow ID
   * @param {Object} data.inputs - Workflow inputs
   * @returns {Promise<Object>} Workflow execution results
   */
  async runWorkflow(data) {
    return this._post('agent-team/workflows/run', data);
  }
}

module.exports = AgentTeamService;