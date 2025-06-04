import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { AgentUI } from '../components/AgentUI.jsx';

describe('AgentUI Component', () => {
  const mockAgent = {
    id: 1,
    name: 'Test Agent',
    description: 'This is a test agent'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('renders the agent data correctly', async () => {
    const { container } = render(React.createElement(AgentUI, { agent: mockAgent }));
    expect(screen.getByTestId('agent-ui-component')).toBeInTheDocument();
    expect(screen.getByText('Agent Interface')).toBeInTheDocument();
  });

  it('handles user interactions correctly', async () => {
    const user = userEvent.setup();
    const handleAction = vi.fn();

    render(React.createElement(AgentUI, { agent: mockAgent, onAction: handleAction }));

    const startButton = screen.getByRole('button', { name: /start/i });
    await user.click(startButton);

    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it('displays agent interface correctly', async () => {
    render(React.createElement(AgentUI, { agent: mockAgent }));
    expect(screen.getByTestId('agent-ui-component')).toBeInTheDocument();
    expect(screen.getByText('Agent Interface')).toBeInTheDocument();
  });
});
