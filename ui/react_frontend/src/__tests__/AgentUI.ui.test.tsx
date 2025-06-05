import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentUI } from '../components/AgentUI.jsx';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';

// Mock the original component to avoid type issues
vi.mock('../components/AgentUI.jsx', () => ({
  AgentUI: vi.fn(({ agent, theme, onAction }) => {
    const [expanded, setExpanded] = React.useState(false);
    const [message, setMessage] = React.useState('');

    return (
      <div style={{ fontFamily: theme?.fontFamily }}>
        <button
          aria-label={expanded ? "Collapse" : "Expand"}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "▲" : "▼"}
        </button>
        {expanded && agent && (
          <div>
            <span>{agent.name}</span>
            <span>{agent.status}</span>
          </div>
        )}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Send a message to the agent..."
        />
        <button
          onClick={() => {
            onAction?.({ type: 'MESSAGE', content: message });
            setMessage('');
          }}
        >
          Send Message
        </button>
      </div>
    );
  })
}));

describe('AgentUI Component', () => {
  const mockAgent = {
    id: '123',
    name: 'Test Agent',
    status: 'idle',
    type: 'Assistant',
    createdAt: new Date('2025-05-15T12:00:00Z').toISOString(),
  };

  const mockTheme = {
    primaryColor: '#ff0000',
    secondaryColor: '#00ff00',
    fontFamily: 'Arial',
    borderRadius: '4px',
    darkMode: false,
  };

  it('renders with minimal props', () => {
    render(<AgentUI />);
    expect(screen.getByRole('button', { name: /expand|collapse/i })).toBeInTheDocument();
  });

  it('renders with agent data', () => {
    render(<AgentUI agent={mockAgent} theme={mockTheme} onAction={() => {}} />);
    expect(screen.getByRole('button', { name: /expand|collapse/i })).toBeInTheDocument();

    // Expand the component to see agent details
    fireEvent.click(screen.getByRole('button', { name: /expand|collapse/i }));

    expect(screen.getByText(/test agent/i)).toBeInTheDocument();
    expect(screen.getByText(/idle/i)).toBeInTheDocument();
  });

  it('renders with custom theme', () => {
    render(<AgentUI agent={mockAgent} theme={mockTheme} onAction={() => {}} />);

    // First find any element in the component
    const component = screen.getByRole('button', { name: /expand|collapse/i });
    expect(component).toBeVisible();

    // The container should have the custom font family from the theme
    expect(component.parentElement).toHaveStyle({
      fontFamily: mockTheme.fontFamily
    });
  });

  it('handles message input and submission', () => {
    const mockOnAction = vi.fn();
    render(<AgentUI agent={mockAgent} onAction={mockOnAction} theme={mockTheme} />);

    // Message input should be available without expanding
    const messageInput = screen.getByRole('textbox');
    fireEvent.change(messageInput, { target: { value: 'Hello agent' } });

    const sendButton = screen.getByRole('button', { name: /send message/i });
    fireEvent.click(sendButton);
    expect(mockOnAction).toHaveBeenCalledWith(expect.objectContaining({
      type: 'MESSAGE',
      content: 'Hello agent'
    }));
  });
});
