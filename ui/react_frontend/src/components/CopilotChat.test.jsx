import '@testing-library/jest-dom';
import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from 'vitest';
import CopilotChatDemo from "./CopilotChat";

// Mock CopilotKitProvider and CopilotChat if packages are not installed yet
vi.mock("@copilotkit/react-core", () => ({
  CopilotKitProvider: ({ children }) => <div data-testid="mock-provider">{children}</div>,
}));
vi.mock("@copilotkit/react-ui", () => ({
  CopilotChat: ({ instructions }) => <div data-testid="mock-chat">Instructions: {instructions}</div>,
}));

describe("CopilotChatDemo", () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks();
  });

  it("renders without crashing and displays the heading", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByRole("heading", { name: /CopilotKit \+ CrewAI Chat/i })).toBeInTheDocument();
  });

  it("shows the agent instructions", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByText(/You are a helpful project assistant/i)).toBeInTheDocument();
  });

  it("contains the CopilotKitProvider and CopilotChat components", () => {
    render(<CopilotChatDemo />);
    expect(screen.getByTestId("mock-provider")).toBeInTheDocument();
    expect(screen.getByTestId("mock-chat")).toBeInTheDocument();
  });
});