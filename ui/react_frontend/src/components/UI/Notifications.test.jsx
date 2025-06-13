/**
 * Tests for the Notifications component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Notifications from './Notifications';

// Mock AppContext
jest.mock('../../context/AppContext', () => {
  return {
    useAppContext: jest.fn()
  };
});

const { useAppContext } = require('../../context/AppContext');

describe('Notifications', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders nothing when there are no notifications', () => {
    useAppContext.mockReturnValue({
      notifications: [],
      dispatch: jest.fn()
    });
    const { container } = render(<Notifications />);
    // Should not render any Snackbar or Alert
    expect(container.querySelector('.MuiSnackbar-root')).not.toBeInTheDocument();
    expect(container.querySelector('.MuiAlert-root')).not.toBeInTheDocument();
  });

  it('renders a single notification with correct message and severity', () => {
    useAppContext.mockReturnValue({
      notifications: [
        { id: 1, message: 'Test notification', type: 'success' }
      ],
      dispatch: jest.fn()
    });
    render(<Notifications />);
    expect(screen.getByText(/Test notification/i)).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveClass('MuiAlert-filledSuccess');
  });

  it('renders multiple notifications', () => {
    useAppContext.mockReturnValue({
      notifications: [
        { id: 1, message: 'Info message', type: 'info' },
        { id: 2, message: 'Warning message', type: 'warning' }
      ],
      dispatch: jest.fn()
    });
    render(<Notifications />);
    expect(screen.getByText(/Info message/i)).toBeInTheDocument();
    expect(screen.getByText(/Warning message/i)).toBeInTheDocument();
    expect(screen.getAllByRole('alert').length).toBe(2);
  });

  it('defaults severity to "info" if type is missing', () => {
    useAppContext.mockReturnValue({
      notifications: [
        { id: 3, message: 'Default info message' }
      ],
      dispatch: jest.fn()
    });
    render(<Notifications />);
    expect(screen.getByRole('alert')).toHaveClass('MuiAlert-filledInfo');
  });

  it('calls dispatch to remove notification when closed', () => {
    const mockDispatch = jest.fn();
    useAppContext.mockReturnValue({
      notifications: [
        { id: 4, message: 'Closable notification', type: 'error' }
      ],
      dispatch: mockDispatch
    });
    render(<Notifications />);
    // Click the close button (Alert's close)
    const closeBtn = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeBtn);
    expect(mockDispatch).toHaveBeenCalledWith({
      type: expect.any(String),
      payload: 4
    });
  });
});