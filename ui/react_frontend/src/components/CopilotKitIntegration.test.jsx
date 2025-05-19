import '@testing-library/jest-dom';
import { render, screen } from "@testing-library/react";
import { vi } from 'vitest';
import CopilotChatDemo from "./CopilotChat";

// Mock CopilotKitProvider and CopilotChat if packages are not installed yet
vi.mock("@copilotkit/react-core", () => ({
  CopilotKitProvider: ({ children }) => <div data-testid="mock-provider">{children}</div>,
}));

vi.mock("@copilotkit/react-ui", () => ({
  CopilotChat: ({ instructions }) => (
    <div data-testid="mock-chat">
      <div data-testid="chat-instructions">Instructions: {instructions}</div>
      <div data-testid="chat-input-container">
        <input
          data-testid="chat-input"
          placeholder="Type your message..."
        />
        <button data-testid="chat-submit">Send</button>
      </div>
      <div data-testid="chat-messages">
        <div data-testid="chat-message">Welcome to CopilotKit + CrewAI Chat!</div>
      </div>
    </div>
  ),
}));

describe("CopilotChatDemo Component", () => {
  it("renders without crashing and displays the heading", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByRole("heading", { name: /CopilotKit \+ CrewAI Chat/i })).toBeInTheDocument();
  });

  it("shows the agent instructions", () => {
    render(<CopilotChatDemo />);
    const instructionsElement = screen.getByTestId("chat-instructions");
    expect(instructionsElement).toBeInTheDocument();
    expect(instructionsElement.textContent).toContain("You are a helpful project assistant");
  });

  it("contains the CopilotKitProvider and CopilotChat components", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("mock-provider")).toBeInTheDocument();
    expect(screen.getByTestId("mock-chat")).toBeInTheDocument();
  });

  it("displays the chat input field", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
    expect(screen.getByTestId("chat-submit")).toBeInTheDocument();
  });

  it("displays the welcome message", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("chat-message")).toBeInTheDocument();
    expect(screen.getByTestId("chat-message").textContent).toBe("Welcome to CopilotKit + CrewAI Chat!");
  });

  it("has the correct container element", () => {
    render(<CopilotChatDemo />);
    const container = screen.getByTestId("mock-chat").parentElement;

    // Just check that the container exists
    expect(container).toBeInTheDocument();

    // Note: Testing specific styles is challenging in JSDOM
    // In a real implementation, we would use a more robust approach
    // or use a visual testing tool like Storybook
  });
});

describe("CopilotKit Integration", () => {
  // This test would normally test the actual integration with CopilotKit
  // but since we're mocking the components, we'll just test the basic structure
  it("integrates CopilotKitProvider correctly", () => {
    render(<CopilotChatDemo />);

    // Check that the provider wraps the chat component
    const provider = screen.getByTestId("mock-provider");
    expect(provider).toContainElement(screen.getByTestId("mock-chat"));
  });

  it("passes the correct instructions to the CopilotChat component", () => {
    render(<CopilotChatDemo />);

    // Check that the instructions are passed correctly
    const instructions = screen.getByTestId("chat-instructions");
    expect(instructions.textContent).toContain("You are a helpful project assistant");
    expect(instructions.textContent).toContain("Answer user questions");
    expect(instructions.textContent).toContain("brainstorm ideas");
    expect(instructions.textContent).toContain("assist with task planning");
  });
});

// This test would be used if we had a real implementation with event handlers
describe("CopilotChat Interaction", () => {
  it("renders the chat interface with input field", async () => {
    render(<CopilotChatDemo />);

    // Just verify that the chat component renders with expected elements
    expect(screen.getByTestId("mock-chat")).toBeInTheDocument();
    expect(screen.getByTestId("chat-instructions")).toBeInTheDocument();

    // In a real implementation, we would test interaction with the chat
    // but for now we're just testing that the component renders correctly
  });
});
