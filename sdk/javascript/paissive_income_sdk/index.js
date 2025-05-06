/**
 * pAIssive Income SDK for JavaScript
 *
 * This package provides a JavaScript client for the pAIssive Income API.
 */

const Client = require('./client');
const auth = require('./auth');

// Import services
const NicheAnalysisService = require('./services/niche-analysis');
const MonetizationService = require('./services/monetization');
const MarketingService = require('./services/marketing');
const AIModelsService = require('./services/ai-models');
const AgentTeamService = require('./services/agent-team');
const UserService = require('./services/user');
const DashboardService = require('./services/dashboard');
const APIKeyService = require('./services/api-key');

module.exports = {
  Client,
  auth,
  NicheAnalysisService,
  MonetizationService,
  MarketingService,
  AIModelsService,
  AgentTeamService,
  UserService,
  DashboardService,
  APIKeyService
};
