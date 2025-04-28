import React, { createContext, useContext, useReducer, useEffect } from 'react';
import apiClient, { getStoredUser, isTokenValid } from '../services/apiClient';

// Initial state with authentication data from localStorage
const initialState = {
  user: getStoredUser(),
  isAuthenticated: isTokenValid(),
  isLoading: false,
  error: null,
  notifications: [],
  projectsData: null,
  nicheAnalysisResults: null,
  solutions: null,
  monetizationStrategies: null,
  marketingCampaigns: null,
  darkMode: localStorage.getItem('darkMode') === 'true' || false
};

// Action types
export const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_USER: 'SET_USER',
  LOGOUT: 'LOGOUT',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  SET_PROJECTS_DATA: 'SET_PROJECTS_DATA',
  SET_NICHE_RESULTS: 'SET_NICHE_RESULTS',
  SET_SOLUTIONS: 'SET_SOLUTIONS',
  SET_MONETIZATION_STRATEGIES: 'SET_MONETIZATION_STRATEGIES',
  SET_MARKETING_CAMPAIGNS: 'SET_MARKETING_CAMPAIGNS',
  TOGGLE_DARK_MODE: 'TOGGLE_DARK_MODE'
};

// Reducer function to handle state changes
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload };
      
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false };
      
    case ActionTypes.CLEAR_ERROR:
      return { ...state, error: null };
      
    case ActionTypes.SET_USER:
      return { 
        ...state, 
        user: action.payload, 
        isAuthenticated: !!action.payload,
        isLoading: false 
      };
      
    case ActionTypes.LOGOUT:
      return { 
        ...state, 
        user: null, 
        isAuthenticated: false,
        isLoading: false 
      };
      
    case ActionTypes.ADD_NOTIFICATION:
      return { 
        ...state, 
        notifications: [...state.notifications, action.payload] 
      };
      
    case ActionTypes.REMOVE_NOTIFICATION:
      return { 
        ...state, 
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        ) 
      };
      
    case ActionTypes.SET_PROJECTS_DATA:
      return { ...state, projectsData: action.payload, isLoading: false };
      
    case ActionTypes.SET_NICHE_RESULTS:
      return { ...state, nicheAnalysisResults: action.payload, isLoading: false };
      
    case ActionTypes.SET_SOLUTIONS:
      return { ...state, solutions: action.payload, isLoading: false };
      
    case ActionTypes.SET_MONETIZATION_STRATEGIES:
      return { ...state, monetizationStrategies: action.payload, isLoading: false };
      
    case ActionTypes.SET_MARKETING_CAMPAIGNS:
      return { ...state, marketingCampaigns: action.payload, isLoading: false };
      
    case ActionTypes.TOGGLE_DARK_MODE:
      // Persist dark mode to localStorage
      localStorage.setItem('darkMode', !state.darkMode);
      return { ...state, darkMode: !state.darkMode };
      
    default:
      return state;
  }
}

// Create context
const AppContext = createContext();

// Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  // Add notification with auto-removal after timeout
  const addNotification = (notification) => {
    const id = Date.now();
    const notificationWithId = { ...notification, id };
    
    dispatch({ 
      type: ActionTypes.ADD_NOTIFICATION, 
      payload: notificationWithId 
    });
    
    // Auto-remove notification after specified time or default of 5 seconds
    setTimeout(() => {
      dispatch({ 
        type: ActionTypes.REMOVE_NOTIFICATION, 
        payload: id 
      });
    }, notification.timeout || 5000);
  };
  
  // Helper function to fetch user profile
  const fetchUserProfile = async () => {
    // Only try to fetch profile if we think we're authenticated
    if (!isTokenValid()) {
      dispatch({ type: ActionTypes.SET_USER, payload: null });
      return;
    }
    
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const userData = await apiClient.user.getCurrentUser();
      dispatch({ type: ActionTypes.SET_USER, payload: userData });
    } catch (error) {
      console.error('Error fetching user profile:', error);
      // If we get an auth error, we're not authenticated
      dispatch({ type: ActionTypes.SET_USER, payload: null });
      
      if (error.isAuthError) {
        // Don't show notification for initial auth check
        return;
      }
      
      addNotification({
        type: 'error',
        message: 'Failed to load profile. Please log in again.'
      });
    }
  };
  
  // Helper function to handle login
  const login = async (credentials) => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const authData = await apiClient.user.login(credentials);
      // Set just the user data in state, not the whole auth object
      dispatch({ type: ActionTypes.SET_USER, payload: authData.user });
      addNotification({ 
        type: 'success', 
        message: 'Login successful!' 
      });
      return authData.user;
    } catch (error) {
      console.error('Login error:', error);
      dispatch({ 
        type: ActionTypes.SET_ERROR, 
        payload: 'Login failed. Please check your credentials and try again.' 
      });
      addNotification({ 
        type: 'error', 
        message: 'Login failed. Please check your credentials.' 
      });
      throw error;
    }
  };
  
  // Helper function to handle logout
  const logout = async () => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      await apiClient.user.logout();
      dispatch({ type: ActionTypes.LOGOUT });
      addNotification({ 
        type: 'info', 
        message: 'You have been logged out.' 
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Still log out the user locally even if the API call fails
      dispatch({ type: ActionTypes.LOGOUT });
    }
  };
  
  // Helper function to handle register
  const register = async (userData) => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const authData = await apiClient.user.register(userData);
      // Set just the user data in state, not the whole auth object
      dispatch({ type: ActionTypes.SET_USER, payload: authData.user });
      addNotification({ 
        type: 'success', 
        message: 'Registration successful!' 
      });
      return authData.user;
    } catch (error) {
      console.error('Registration error:', error);
      dispatch({ 
        type: ActionTypes.SET_ERROR, 
        payload: 'Registration failed. Please try again.' 
      });
      addNotification({ 
        type: 'error', 
        message: 'Registration failed. Please check your information.' 
      });
      throw error;
    }
  };
  
  // Check for auth token expiration periodically
  useEffect(() => {
    // On component mount, check if user is authenticated
    fetchUserProfile();
    
    // Set up interval to check token validity
    const authCheckInterval = setInterval(() => {
      if (state.isAuthenticated && !isTokenValid()) {
        // Token has expired, log out the user
        dispatch({ type: ActionTypes.LOGOUT });
        addNotification({
          type: 'warning',
          message: 'Your session has expired. Please log in again.'
        });
      }
    }, 60000); // Check every minute
    
    // Clear interval on unmount
    return () => clearInterval(authCheckInterval);
  }, [state.isAuthenticated]);
  
  // Value object with state and actions to provide
  const value = {
    ...state,
    dispatch,
    addNotification,
    login,
    logout,
    register,
    fetchUserProfile,
    fetchDashboardData,
    hasPermission: (permission) => {
      // Check if user has the specified permission
      // For now, this is a simple role check based on what we know about the roles
      if (!state.user || !state.user.roles) return false;
      
      // Admin has all permissions
      if (state.user.roles.includes('admin')) return true;
      
      // For other roles, we'll need a more sophisticated check
      // This is a placeholder for the real permission logic
      const creatorPermissions = [
        'niche:view', 'niche:create', 'niche:edit',
        'solution:view', 'solution:create', 'solution:edit',
        'monetization:view', 'monetization:create', 'monetization:edit',
        'marketing:view', 'marketing:create', 'marketing:edit'
      ];
      
      const basicUserPermissions = [
        'niche:view', 'niche:create',
        'solution:view',
        'monetization:view',
        'marketing:view'
      ];
      
      if (state.user.roles.includes('creator') && creatorPermissions.includes(permission)) {
        return true;
      }
      
      if (state.user.roles.includes('user') && basicUserPermissions.includes(permission)) {
        return true;
      }
      
      return false;
    }
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook for using the app context
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export default AppContext;