import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentUI } from './AgentUI';

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
    expect(screen.getByText('Agent Interface')).toBeInTheDocument();
  });

  test('renders with agent data', () => {
    render(<AgentUI agent={mockAgent} />);
    expect(screen.getByText('Agent Interface')).toBeInTheDocument();
    
    // Expand the component to see agent details
    fireEvent.click(screen.getByLabelText('Expand'));
    
    expect(screen.getByText('ID:')).toBeInTheDocument();
    expect(screen.getByText('agent-123')).toBeInTheDocument();
    expect(screen.getByText('Name:')).toBeInTheDocument();
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
  });

  test('calls onAction when buttons are clicked', () => {
    render(<AgentUI agent={mockAgent} onAction={mockOnAction} />);
    
    fireEvent.click(screen.getByText('Start'));
    expect(mockOnAction).toHaveBeenCalledWith({
      type: 'START',
      agentId: 'agent-123',
      timestamp: expect.any(String),
    });
    
    fireEvent.click(screen.getByText('Help'));
    expect(mockOnAction).toHaveBeenCalledWith({
      type: 'HELP',
      agentId: 'agent-123',
      timestamp: expect.any(String),
    });
  });

  test('sends message when form is submitted', () => {
    render(<AgentUI agent={mockAgent} onAction={mockOnAction} />);
    
    const messageInput = screen.getByPlaceholderText('Send a message to the agent...');
    fireEvent.change(messageInput, { target: { value: 'Hello agent' } });
    
    fireEvent.click(screen.getByText('Send Message'));
    expect(mockOnAction).toHaveBeenCalledWith({
      type: 'MESSAGE',
      agentId: 'agent-123',
      content: 'Hello agent',
      timestamp: expect.any(String),
    });
    
    // Message input should be cleared after sending
    expect(messageInput.value).toBe('');
  });

  test('applies custom theme', () => {
    render(<AgentUI agent={mockAgent} theme={mockTheme} />);
    
    // This is a basic check - in a real test you might want to use
    // getComputedStyle or a similar approach to verify the styles
    const component = screen.getByTestId('agent-ui-component');
    expect(component).toHaveStyle('fontFamily: Arial');
  });
});
