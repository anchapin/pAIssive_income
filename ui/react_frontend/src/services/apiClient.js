/**
 * API Client for pAIssive Income Framework
 * Handles communication with the backend API
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

// Token storage keys
const TOKEN_STORAGE_KEY = 'paissive_auth_token';
const TOKEN_EXPIRY_KEY = 'paissive_token_expiry';
const USER_STORAGE_KEY = 'paissive_user';

/**
 * Get stored authentication token
 * @returns {string|null} The stored token or null if not found
 */
export const getStoredToken = () => {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

/**
 * Get stored user data
 * @returns {Object|null} The stored user data or null if not found
 */
export const getStoredUser = () => {
  const userData = localStorage.getItem(USER_STORAGE_KEY);
  return userData ? JSON.parse(userData) : null;
};

/**
 * Check if the stored token is valid (exists and not expired)
 * @returns {boolean} True if the token is valid, false otherwise
 */
export const isTokenValid = () => {
  const token = getStoredToken();
  if (!token) return false;
  
  const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
  if (!expiry) return false;
  
  return new Date().getTime() < parseInt(expiry, 10);
};

/**
 * Store authentication data from a successful login/registration
 * @param {Object} authData - Authentication data containing token and user info
 */
export const storeAuthData = (authData) => {
  if (!authData || !authData.token) return;
  
  localStorage.setItem(TOKEN_STORAGE_KEY, authData.token);
  
  // Store token expiry time
  if (authData.expires_at) {
    const expiryTime = new Date(authData.expires_at).getTime();
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
  }
  
  // Store user data
  if (authData.user) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authData.user));
  }
};

/**
 * Clear stored authentication data on logout
 */
export const clearAuthData = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};

/**
 * Wrapper for fetch API with default options and authentication
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // Add authentication token if available
  const token = getStoredToken();
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, config);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      
      // Handle API error responses
      if (!response.ok) {
        // Handle authentication errors
        if (response.status === 401) {
          // Clear invalid authentication data
          clearAuthData();
          
          // Create a custom error with authentication status
          const authError = new Error(data.message || 'Authentication failed');
          authError.isAuthError = true;
          throw authError;
        }
        
        throw new Error(data.message || 'API request failed');
      }
      
      return data;
    } else {
      // For non-JSON responses (like file downloads)
      if (!response.ok) {
        throw new Error('API request failed');
      }
      
      return response;
    }
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
}

/**
 * Niche Analysis API endpoints
 */
export const nicheAnalysisAPI = {
  getMarketSegments: () => fetchAPI('/niche-analysis/segments'),
  
  analyzeNiches: (segments) => fetchAPI('/niche-analysis/analyze', {
    method: 'POST',
    body: JSON.stringify({ segments })
  }),
  
  getNicheResults: (analysisId) => fetchAPI(`/niche-analysis/results/${analysisId}`),
  
  getAllNicheResults: () => fetchAPI('/niche-analysis/results')
};

/**
 * Developer API endpoints
 */
export const developerAPI = {
  getNiches: () => fetchAPI('/developer/niches'),
  
  getTemplates: () => fetchAPI('/developer/templates'),
  
  generateSolution: (nicheId, templateId) => fetchAPI('/developer/solution', {
    method: 'POST',
    body: JSON.stringify({ nicheId, templateId })
  }),
  
  getSolutionDetails: (solutionId) => fetchAPI(`/developer/solutions/${solutionId}`),
  
  getAllSolutions: () => fetchAPI('/developer/solutions')
};

/**
 * Monetization API endpoints
 */
export const monetizationAPI = {
  getSolutions: () => fetchAPI('/monetization/solutions'),
  
  generateStrategy: (solutionId, options) => fetchAPI('/monetization/strategy', {
    method: 'POST',
    body: JSON.stringify({ solutionId, options })
  }),
  
  getStrategyDetails: (strategyId) => fetchAPI(`/monetization/strategy/${strategyId}`),
  
  getAllStrategies: () => fetchAPI('/monetization/strategies')
};

/**
 * Marketing API endpoints
 */
export const marketingAPI = {
  getSolutions: () => fetchAPI('/marketing/solutions'),
  
  getAudiencePersonas: () => fetchAPI('/marketing/audience-personas'),
  
  getChannels: () => fetchAPI('/marketing/channels'),
  
  generateCampaign: (solutionId, audienceIds, channelIds) => fetchAPI('/marketing/campaign', {
    method: 'POST',
    body: JSON.stringify({ solutionId, audienceIds, channelIds })
  }),
  
  getCampaignDetails: (campaignId) => fetchAPI(`/marketing/campaign/${campaignId}`),
  
  getAllCampaigns: () => fetchAPI('/marketing/campaigns')
};

/**
 * Dashboard API endpoints
 */
export const dashboardAPI = {
  getProjectsOverview: () => fetchAPI('/dashboard/overview'),
  
  getRevenueStats: () => fetchAPI('/dashboard/revenue'),
  
  getSubscriberStats: () => fetchAPI('/dashboard/subscribers')
};

/**
 * User API endpoints
 */
export const userAPI = {
  getCurrentUser: () => fetchAPI('/user/profile'),
  
  updateProfile: (profileData) => fetchAPI('/user/profile', {
    method: 'PUT',
    body: JSON.stringify(profileData)
  }),
  
  login: async (credentials) => {
    const authData = await fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    
    // Store the authentication data
    storeAuthData(authData);
    return authData;
  },
  
  logout: async () => {
    try {
      // Call the logout API endpoint
      await fetchAPI('/auth/logout', {
        method: 'POST'
      });
    } finally {
      // Always clear local auth data even if the API call fails
      clearAuthData();
    }
  },
  
  register: async (userData) => {
    const authData = await fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
    
    // Store the authentication data
    storeAuthData(authData);
    return authData;
  },
  
  // Check if user is authenticated
  isAuthenticated: () => isTokenValid(),
  
  // Get current authentication state
  getAuthState: () => ({
    isAuthenticated: isTokenValid(),
    user: getStoredUser()
  }),
  
  // Admin user management
  getUsers: (skip, limit) => {
    const params = new URLSearchParams();
    if (skip !== undefined) params.append('skip', skip);
    if (limit !== undefined) params.append('limit', limit);
    
    const queryString = params.toString();
    return fetchAPI(`/users${queryString ? '?' + queryString : ''}`);
  },
  
  getUser: (userId) => fetchAPI(`/users/${userId}`)
};

export default {
  nicheAnalysis: nicheAnalysisAPI,
  developer: developerAPI,
  monetization: monetizationAPI,
  marketing: marketingAPI,
  dashboard: dashboardAPI,
  user: userAPI
};