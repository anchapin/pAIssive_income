/**
 * User service for the pAIssive Income API.
 *
 * This module provides a service for interacting with the user endpoints.
 */

const BaseService = require('./base');

/**
 * User service.
 * @extends BaseService
 */
class UserService extends BaseService {
  /**
   * Register a new user.
   *
   * @param {Object} data - User registration data
   * @param {string} data.username - Username
   * @param {string} data.email - Email address
   * @param {string} data.password - Password
   * @returns {Promise<Object>} Registration result and user data
   */
  async register(data) {
    return this._post('user/register', data);
  }

  /**
   * Log in a user.
   *
   * @param {Object} data - Login data
   * @param {string} data.email - Email address
   * @param {string} data.password - Password
   * @returns {Promise<Object>} Login result with authentication token
   */
  async login(data) {
    return this._post('user/login', data);
  }

  /**
   * Get the user's profile.
   *
   * @returns {Promise<Object>} User profile data
   */
  async getProfile() {
    return this._get('user/profile');
  }

  /**
   * Update the user's profile.
   *
   * @param {Object} data - Updated profile data
   * @returns {Promise<Object>} Updated profile
   */
  async updateProfile(data) {
    return this._put('user/profile', data);
  }

  /**
   * Change the user's password.
   *
   * @param {Object} data - Password change data
   * @param {string} data.current_password - Current password
   * @param {string} data.new_password - New password
   * @returns {Promise<Object>} Password change result
   */
  async changePassword(data) {
    return this._post('user/change-password', data);
  }

  /**
   * Request a password reset.
   *
   * @param {Object} data - Password reset request data
   * @param {string} data.email - Email address
   * @returns {Promise<Object>} Password reset request result
   */
  async requestPasswordReset(data) {
    return this._post('user/request-password-reset', data);
  }

  /**
   * Reset a password using a reset token.
   *
   * @param {Object} data - Password reset data
   * @param {string} data.token - Reset token
   * @param {string} data.new_password - New password
   * @returns {Promise<Object>} Password reset result
   */
  async resetPassword(data) {
    return this._post('user/reset-password', data);
  }

  /**
   * Verify an email address using a verification token.
   *
   * @param {string} token - Email verification token
   * @returns {Promise<Object>} Email verification result
   */
  async verifyEmail(token) {
    return this._get(`user/verify-email/${token}`);
  }
}

module.exports = UserService;
