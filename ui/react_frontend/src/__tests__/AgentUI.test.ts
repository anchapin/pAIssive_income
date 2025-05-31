import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AgentUI from '../components/AgentUI';

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
    const { container } = render(<AgentUI agent={mockAgent} />);
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('This is a test agent')).toBeInTheDocument();
  });

  it('handles user interactions correctly', async () => {
    const user = userEvent.setup();
    const handleAction = vi.fn();

    render(<AgentUI agent={mockAgent} onAction={handleAction} />);
    
    const actionButton = screen.getByRole('button', { name: /action/i });
    await user.click(actionButton);
    
    expect(handleAction).toHaveBeenCalledTimes(1);
    expect(handleAction).toHaveBeenCalledWith(mockAgent.id);
  });

  it('displays loading state while fetching data', async () => {
    global.fetch.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(resolve, 100))
    );
    
    render(<AgentUI agent={mockAgent} />);
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });
});
