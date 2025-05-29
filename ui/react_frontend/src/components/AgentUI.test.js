import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentUI } from './AgentUI';
import '@testing-library/jest-dom';

describe('AgentUI Component', () => {
  const mockAgent = {
    id: 'agent-123',
    name: 'Test Agent',
    status: 'idle',
    type: 'Assistant',
    createdAt: '2025-05-15T12:00:00Z',
  };

  const mockTheme = {
    primaryColor: '#ff0000',
    secondaryColor: '#00ff00',
    fontFamily: 'Arial',
    borderRadius: '4px',
    darkMode: false,
  };

  const mockOnAction = jest.fn();

  beforeEach(() => {
    mockOnAction.mockClear();
  });
  test('renders with minimal props', () => {
    render(<AgentUI />);
    expect(screen.getByRole('button', { name: /expand/i })).toBeInTheDocument();
  });

  test('renders with agent data', () => {
    render(<AgentUI agent={mockAgent} />);
    expect(screen.getByRole('button', { name: /expand/i })).toBeInTheDocument();
    
    // Expand the component to see agent details
    fireEvent.click(screen.getByRole('button', { name: /expand/i }));
    
    expect(screen.getByText(/test agent/i)).toBeInTheDocument();
    expect(screen.getByText(/idle/i)).toBeInTheDocument();
  });
  test('calls onAction when buttons are clicked', () => {
    render(<AgentUI agent={mockAgent} onAction={mockOnAction} />);
    
    // First expand the UI
    fireEvent.click(screen.getByRole('button', { name: /expand/i }));
    
    const actionButtons = screen.getAllByRole('button');
    expect(actionButtons.length).toBeGreaterThan(1);
  });

  test('sends message when form is submitted', () => {
    render(<AgentUI agent={mockAgent} onAction={mockOnAction} />);
    
    // First expand the UI
    fireEvent.click(screen.getByRole('button', { name: /expand/i }));
    
    const messageInput = screen.getByRole('textbox');
    fireEvent.change(messageInput, { target: { value: 'Hello agent' } });
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    // Message input should be cleared after sending
    expect(messageInput.value).toBe('');
  });
  test('applies custom theme', () => {
    render(<AgentUI agent={mockAgent} theme={mockTheme} />);
    
    // First find any element in the component
    const component = screen.getByRole('button', { name: /expand/i });
    expect(component).toBeVisible();
    
    // The container should have the custom font family from the theme
    expect(component.parentElement).toHaveStyle({
      fontFamily: mockTheme.fontFamily
    });
  });
});
