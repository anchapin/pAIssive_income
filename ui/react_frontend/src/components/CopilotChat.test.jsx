import '@testing-library/jest-dom';
import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from 'vitest';
import CopilotChatDemo from "./CopilotChat";

// Mock CopilotKit components
vi.mock("@copilotkit/react-core", () => ({
  CopilotKitProvider: ({ children }) => <div data-testid="mock-provider">{children}</div>
}));

vi.mock("@copilotkit/react-ui", () => ({
  CopilotChat: ({ instructions }) => (
    <div data-testid="mock-chat">
      <div data-testid="chat-instructions">{instructions}</div>
      <div data-testid="chat-interface">
        <input type="text" data-testid="chat-input" placeholder="Type your message..." />
        <button data-testid="chat-submit">Send</button>
      </div>
    </div>
  )
}));

describe("CopilotChatDemo", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders without crashing", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("mock-provider")).toBeInTheDocument();
  });

  it("renders title correctly", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByText(/CopilotKit \+ CrewAI Chat/i)).toBeInTheDocument();
  });

  it("includes the chat interface", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("chat-interface")).toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
    expect(screen.getByTestId("chat-submit")).toBeInTheDocument();
  });

  it("displays correct instructions", () => {
    render(<CopilotChatDemo />);
    const instructions = screen.getByTestId("chat-instructions");
    expect(instructions).toBeInTheDocument();
    expect(instructions).toHaveTextContent(/You are a helpful project assistant/);
  });

  it("has proper container styling", () => {
    render(<CopilotChatDemo />);
    const container = screen.getByTestId("mock-chat").parentElement;
    expect(container).toHaveClass("copilot-chat-container");
  });
});