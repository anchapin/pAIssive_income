/**
 * Enhanced tests for the AgentUI component
 *
 * These tests render the real AgentUI component and make assertions
 * about the rendered output and user interactions.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AgentUI from '../components/AgentUI';

// Mock agent data
const mockAgent = {
  id: 1,
  name: 'Test Agent',
  description: 'This is a test agent'
};

describe('AgentUI Component', () => {
  it('renders the agent name and description', () => {
    render(<AgentUI agent={mockAgent}></AgentUI>);
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('This is a test agent')).toBeInTheDocument();
  });

  it('renders an action button and triggers callback on click', () => {
    const mockOnAction = jest.fn();
    render(<AgentUI agent={mockAgent} onAction={mockOnAction}></AgentUI>);
    // Assume the button is labeled "Run Action"
    const button = screen.getByRole('button', { name: /run action/i });
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(mockOnAction).toHaveBeenCalledTimes(1);
  });
});
