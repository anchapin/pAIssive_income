import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from 'vitest';
import userEvent from '@testing-library/user-event';
import CopilotKitIntegration from './CopilotKitIntegration';

// Mock CopilotKit components
vi.mock('@copilotkit/react-core', () => ({
  CopilotKitProvider: ({ children }) => <div data-testid="mock-provider">{children}</div>
}));

vi.mock('@copilotkit/react-ui', () => ({
  CopilotTextarea: ({ placeholder, className }) => (
    <textarea
      data-testid="mock-copilot-textarea"
      placeholder={placeholder}
      className={className}
    />
  )
}));

describe('CopilotKitIntegration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<CopilotKitIntegration />);
    expect(screen.getByTestId('copilot-integration-container')).toBeInTheDocument();
  });

  it('renders the title correctly', () => {
    render(<CopilotKitIntegration />);
    expect(screen.getByText('CopilotKit Integration Demo')).toBeInTheDocument();
  });

  it('includes the CopilotTextarea component', () => {
    render(<CopilotKitIntegration />);
    const textarea = screen.getByTestId('mock-copilot-textarea');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveAttribute('placeholder', 'Type here and ask for help...');
  });

  it('displays usage instructions', () => {
    render(<CopilotKitIntegration />);
    expect(screen.getByText(/How to use:/i)).toBeInTheDocument();
    expect(screen.getByText(/Type in the textarea above/i)).toBeInTheDocument();
    expect(screen.getByText(/Ask for help with a task/i)).toBeInTheDocument();
    expect(screen.getByText(/The AI will respond with helpful suggestions/i)).toBeInTheDocument();
  });

  it('has proper styling classes', () => {
    render(<CopilotKitIntegration />);
    expect(screen.getByTestId('copilot-integration-container')).toHaveClass('p-4', 'bg-gray-100', 'rounded-lg', 'shadow-md');
  });
});
