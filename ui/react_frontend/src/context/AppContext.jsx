import React, { createContext, useContext, useReducer, useEffect } from 'react';
import apiClient from '../services/apiClient';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  notifications: [],
  projectsData: null,
  nicheAnalysisResults: null,
  solutions: null,
  monetizationStrategies: null,
  marketingCampaigns: null,
  darkMode: false
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
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const userData = await apiClient.user.getCurrentUser();
      dispatch({ type: ActionTypes.SET_USER, payload: userData });
    } catch (error) {
      console.error('Error fetching user profile:', error);
      dispatch({ type: ActionTypes.SET_USER, payload: null });
    }
  };

  // Helper function to fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const projectsData = await apiClient.dashboard.getProjectsOverview();
      dispatch({ type: ActionTypes.SET_PROJECTS_DATA, payload: projectsData });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      dispatch({
        type: ActionTypes.SET_ERROR,
        payload: 'Failed to load dashboard data. Please try again.'
      });
    }
  };

  // Helper function to handle login
  const login = async (credentials) => {
    try {
      dispatch({ type: ActionTypes.SET_LOADING, payload: true });
      const userData = await apiClient.user.login(credentials);
      dispatch({ type: ActionTypes.SET_USER, payload: userData });
      addNotification({
        type: 'success',
        message: 'Login successful!'
      });
      return userData;
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
      const newUser = await apiClient.user.register(userData);
      dispatch({ type: ActionTypes.SET_USER, payload: newUser });
      addNotification({
        type: 'success',
        message: 'Registration successful!'
      });
      return newUser;
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

  // Check if user is already authenticated on app load
  useEffect(() => {
    fetchUserProfile();
  }, []);

  // Value object with state and actions to provide
  const value = {
    ...state,
    dispatch,
    addNotification,
    login,
    logout,
    register,
    fetchUserProfile,
    fetchDashboardData
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
