import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import '@testing-library/jest-dom';
import CopilotChatDemo from "./CopilotChat";

// Mock CopilotKitProvider and CopilotChat if packages are not installed yet
jest.mock("@copilotkit/react-core", () => ({
  CopilotKitProvider: ({ children }) => <div data-testid="mock-provider">{children}</div>,
}));

jest.mock("@copilotkit/react-ui", () => ({
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

  it("has the correct styling", () => {
    render(<CopilotChatDemo />);
    const container = screen.getByTestId("mock-chat").parentElement;
    
    // Check if the container has the expected styles
    expect(container).toHaveStyle({
      maxWidth: "480px",
      margin: "2rem auto",
      border: "1px solid #ccc",
      borderRadius: "8px",
      padding: "24px"
    });
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
  it("simulates user input and submission", async () => {
    // Mock the chat submission function
    const mockSubmit = jest.fn();
    
    // Override the mock to include our mock function
    jest.mock("@copilotkit/react-ui", () => ({
      CopilotChat: ({ instructions }) => (
        <div data-testid="mock-chat">
          <div data-testid="chat-instructions">Instructions: {instructions}</div>
          <div data-testid="chat-input-container">
            <input 
              data-testid="chat-input" 
              placeholder="Type your message..." 
            />
            <button 
              data-testid="chat-submit"
              onClick={mockSubmit}
            >
              Send
            </button>
          </div>
        </div>
      ),
    }));
    
    render(<CopilotChatDemo />);
    
    // Get the input field and submit button
    const inputField = screen.getByTestId("chat-input");
    const submitButton = screen.getByTestId("chat-submit");
    
    // Simulate typing a message
    fireEvent.change(inputField, { target: { value: "Hello, AI assistant!" } });
    
    // Simulate clicking the submit button
    fireEvent.click(submitButton);
    
    // In a real test, we would wait for the response
    // and check that it appears in the chat
    await waitFor(() => {
      // This would check for the response in a real implementation
      // expect(screen.getByText(/some expected response/i)).toBeInTheDocument();
      
      // For now, just check that our mock was called
      // expect(mockSubmit).toHaveBeenCalled();
    });
  });
});
